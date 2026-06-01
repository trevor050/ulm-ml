"""Adaptive stopping rules for self-consistency style reasoning.

The utilities in this module model the last stage of chain-of-thought
self-consistency: a black-box model emits answer samples, and an aggregator
must decide when another sample is still worth buying.  The code deliberately
avoids any LLM dependency so policies can be stress-tested on calibrated
sample streams before spending real inference budget.
"""

from __future__ import annotations

import csv
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

Answer = int
StopRule = Callable[[NDArray[np.int_], int], bool]


@dataclass(frozen=True)
class SampleStreamResult:
    """Outcome from applying a stopping rule to one answer stream."""

    prediction: Answer
    correct: bool
    samples_used: int
    counts: tuple[int, ...]


@dataclass(frozen=True)
class PolicyMetrics:
    """Aggregate cost/quality metrics for a stopping policy."""

    name: str
    accuracy: float
    mean_samples: float
    median_samples: float
    p90_samples: float
    max_samples: int
    efficiency: float


@dataclass(frozen=True)
class TraceReplayResult:
    """Outcome from replaying a stopping policy on one task's answer trace."""

    task_id: str
    prediction: str
    correct_answer: str
    correct: bool
    samples_used: int
    token_count: int | None


@dataclass(frozen=True)
class AnswerTraceRow:
    """One normalized answer sample from a cached self-consistency trace CSV.

    Required CSV columns are ``task_id``, ``sample_index``, ``answer``, and
    ``correct_answer``.  ``token_count`` is optional.  The loader preserves
    normalized answers as strings because real benchmark answers are not a
    shared integer class set across tasks.
    """

    task_id: str
    sample_index: int
    answer: str
    correct_answer: str
    token_count: int | None = None

    @property
    def is_correct(self) -> bool:
        """Return whether this sample's normalized answer matches the gold answer."""

        return self.answer == self.correct_answer


def majority_vote(counts: NDArray[np.int_]) -> Answer:
    """Return the deterministic majority answer, breaking ties by answer id."""

    return int(np.flatnonzero(counts == counts.max())[0])


def fixed_budget_rule(max_samples: int) -> StopRule:
    """Stop only after exactly ``max_samples`` observations."""

    if max_samples < 1:
        raise ValueError("max_samples must be positive")

    def should_stop(_counts: NDArray[np.int_], samples_seen: int) -> bool:
        return samples_seen >= max_samples

    return should_stop


def vote_margin_rule(min_samples: int, margin: int, max_samples: int) -> StopRule:
    """Stop when the current winner leads the runner-up by ``margin`` votes.

    This is the common cheap heuristic.  It is intentionally included as a
    baseline because it often stops too early on ambiguous problems where the
    first few samples happen to agree.
    """

    if min_samples < 1 or margin < 1 or max_samples < min_samples:
        raise ValueError("expected 1 <= min_samples <= max_samples and margin >= 1")

    def should_stop(counts: NDArray[np.int_], samples_seen: int) -> bool:
        if samples_seen >= max_samples:
            return True
        if samples_seen < min_samples:
            return False
        top_two = np.sort(counts)[-2:]
        return int(top_two[-1] - top_two[-2]) >= margin

    return should_stop


def posterior_leader_probability(
    counts: NDArray[np.int_],
    *,
    alpha: float = 0.5,
    draws: int = 4096,
    rng: np.random.Generator | None = None,
) -> float:
    """Estimate posterior probability that the empirical leader is truly best.

    We treat an answer sampler as a categorical distribution with a symmetric
    Dirichlet prior.  After observing answer counts, the probability of interest
    is ``P(p_leader > max_j!=leader p_j | counts)``.  This is not a claim that
    self-consistency samples are perfectly iid; it is a small, inspectable proxy
    for uncertainty that can be calibrated against held-out traces.
    """

    if counts.ndim != 1 or counts.size < 2:
        raise ValueError("counts must be a one-dimensional vector with at least two answers")
    if alpha <= 0 or draws < 1:
        raise ValueError("alpha and draws must be positive")

    generator = rng or np.random.default_rng()
    leader = majority_vote(counts)
    posterior = generator.dirichlet(counts.astype(float) + alpha, size=draws)
    winners = np.argmax(posterior, axis=1)
    return float(np.mean(winners == leader))


def posterior_confidence_rule(
    *,
    min_samples: int,
    confidence: float,
    max_samples: int,
    alpha: float = 0.5,
    draws: int = 4096,
    seed: int = 0,
) -> StopRule:
    """Stop when a Dirichlet posterior says the current leader is stable.

    The rule is intentionally conservative: it never stops before
    ``min_samples`` and it hard-stops at ``max_samples`` to preserve a strict
    latency/cost bound.
    """

    if not (0 < confidence < 1):
        raise ValueError("confidence must be between 0 and 1")
    if min_samples < 1 or max_samples < min_samples:
        raise ValueError("expected 1 <= min_samples <= max_samples")
    generator = np.random.default_rng(seed)

    def should_stop(counts: NDArray[np.int_], samples_seen: int) -> bool:
        if samples_seen >= max_samples:
            return True
        if samples_seen < min_samples:
            return False
        probability = posterior_leader_probability(
            counts,
            alpha=alpha,
            draws=draws,
            rng=generator,
        )
        return probability >= confidence

    return should_stop


def run_stream(
    samples: Sequence[Answer],
    correct_answer: Answer,
    num_answers: int,
    should_stop: StopRule,
) -> SampleStreamResult:
    """Apply a stopping rule to one pre-generated stream of answer samples."""

    if num_answers < 2:
        raise ValueError("num_answers must be at least two")
    counts = np.zeros(num_answers, dtype=int)
    samples_used = 0
    for raw_answer in samples:
        answer = int(raw_answer)
        if not 0 <= answer < num_answers:
            raise ValueError(f"answer {answer} outside [0, {num_answers})")
        counts[answer] += 1
        samples_used += 1
        if should_stop(counts, samples_used):
            break
    else:
        raise ValueError("sample stream ended before stopping rule fired")

    prediction = majority_vote(counts)
    return SampleStreamResult(
        prediction=prediction,
        correct=prediction == correct_answer,
        samples_used=samples_used,
        counts=tuple(int(x) for x in counts),
    )


def synthetic_answer_distributions(
    *,
    num_tasks: int,
    num_answers: int,
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    """Create a heterogeneous bank of answer distributions.

    The mixture intentionally contains easy, medium, and adversarially ambiguous
    prompts.  For each task, answer ``0`` is the ground-truth answer, but the
    model's sample probability for answer ``0`` varies by difficulty.
    """

    if num_tasks < 1 or num_answers < 2:
        raise ValueError("num_tasks must be positive and num_answers at least two")

    bands = rng.choice([0, 1, 2], size=num_tasks, p=[0.45, 0.35, 0.20])
    correct_probs = np.empty(num_tasks, dtype=float)
    correct_probs[bands == 0] = rng.beta(14, 3, size=np.sum(bands == 0))
    correct_probs[bands == 1] = rng.beta(6, 5, size=np.sum(bands == 1))
    correct_probs[bands == 2] = rng.beta(4, 6, size=np.sum(bands == 2))
    correct_probs = np.clip(correct_probs, 0.05, 0.97)

    distributions = np.zeros((num_tasks, num_answers), dtype=float)
    distributions[:, 0] = correct_probs
    for idx, p_correct in enumerate(correct_probs):
        distractor_mass = 1.0 - p_correct
        distractors = rng.dirichlet(np.full(num_answers - 1, 0.7))
        distributions[idx, 1:] = distractor_mass * distractors
    return distributions


def sample_answer_streams(
    distributions: NDArray[np.float64],
    *,
    max_samples: int,
    rng: np.random.Generator,
) -> NDArray[np.int_]:
    """Sample answer ids for every task under every planned draw."""

    if distributions.ndim != 2:
        raise ValueError("distributions must be a task by answer matrix")
    if max_samples < 1:
        raise ValueError("max_samples must be positive")

    streams = np.empty((distributions.shape[0], max_samples), dtype=int)
    answer_ids = np.arange(distributions.shape[1])
    for idx, probs in enumerate(distributions):
        streams[idx] = rng.choice(answer_ids, size=max_samples, p=probs)
    return streams


def evaluate_policy(
    name: str,
    streams: NDArray[np.int_],
    should_stop_factory: Callable[[], StopRule],
    *,
    correct_answer: Answer = 0,
) -> PolicyMetrics:
    """Evaluate a policy on pre-sampled answer streams."""

    if streams.ndim != 2:
        raise ValueError("streams must be a task by sample matrix")
    num_answers = int(streams.max()) + 1
    outcomes = [
        run_stream(row, correct_answer, num_answers, should_stop_factory()) for row in streams
    ]
    samples = np.array([outcome.samples_used for outcome in outcomes], dtype=float)
    accuracy = float(np.mean([outcome.correct for outcome in outcomes]))
    mean_samples = float(np.mean(samples))
    return PolicyMetrics(
        name=name,
        accuracy=accuracy,
        mean_samples=mean_samples,
        median_samples=float(np.median(samples)),
        p90_samples=float(np.quantile(samples, 0.9)),
        max_samples=int(np.max(samples)),
        efficiency=accuracy / mean_samples,
    )


def load_answer_trace_csv(path: str | Path) -> list[AnswerTraceRow]:
    """Load cached answer-only self-consistency traces from a compact CSV schema.

    The intended replay schema is one row per sampled answer:

    ``task_id,sample_index,answer,correct_answer,token_count``

    ``token_count`` may be omitted or left blank.  Rows are returned sorted by
    ``(task_id, sample_index)`` so replay policies see deterministic prefixes.
    Extra columns are ignored, which lets callers keep model names, prompt ids,
    or split labels in the same file without changing this lightweight loader.
    """

    trace_path = Path(path)
    required = {"task_id", "sample_index", "answer", "correct_answer"}
    rows: list[AnswerTraceRow] = []
    seen: set[tuple[str, int]] = set()

    with trace_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = required - fieldnames
        if missing:
            missing_columns = ", ".join(sorted(missing))
            raise ValueError(f"answer trace CSV missing required column(s): {missing_columns}")

        for line_number, raw in enumerate(reader, start=2):
            task_id = _required_text(raw, "task_id", line_number)
            sample_index = _nonnegative_int(raw["sample_index"], "sample_index", line_number)
            answer = _required_text(raw, "answer", line_number)
            correct_answer = _required_text(raw, "correct_answer", line_number)
            token_count = _optional_nonnegative_int(
                raw.get("token_count"), "token_count", line_number
            )

            key = (task_id, sample_index)
            if key in seen:
                raise ValueError(
                    f"duplicate sample_index {sample_index} for task_id {task_id!r} "
                    f"at line {line_number}"
                )
            seen.add(key)
            rows.append(
                AnswerTraceRow(
                    task_id=task_id,
                    sample_index=sample_index,
                    answer=answer,
                    correct_answer=correct_answer,
                    token_count=token_count,
                )
            )

    return sorted(rows, key=lambda row: (row.task_id, row.sample_index))


def group_answer_traces(rows: Sequence[AnswerTraceRow]) -> dict[str, list[AnswerTraceRow]]:
    """Group trace rows by task id and validate per-task gold answer consistency."""

    grouped: dict[str, list[AnswerTraceRow]] = {}
    for row in rows:
        grouped.setdefault(row.task_id, []).append(row)
    for task_id, task_rows in grouped.items():
        answers = {row.correct_answer for row in task_rows}
        if len(answers) != 1:
            raise ValueError(f"task_id {task_id!r} has inconsistent correct_answer values")
        task_rows.sort(key=lambda row: row.sample_index)
    return dict(sorted(grouped.items()))


def run_trace(
    task_rows: Sequence[AnswerTraceRow],
    should_stop: StopRule,
) -> TraceReplayResult:
    """Replay one task's string-answer trace through an integer stopping rule."""

    if not task_rows:
        raise ValueError("task_rows must not be empty")
    correct_answers = {row.correct_answer for row in task_rows}
    if len(correct_answers) != 1:
        raise ValueError("all rows for a task must share one correct_answer")

    answer_vocab = sorted({row.answer for row in task_rows} | correct_answers)
    if len(answer_vocab) == 1:
        answer_vocab.append("__unobserved_alternative__")
    answer_to_id = {answer: idx for idx, answer in enumerate(answer_vocab)}
    id_to_answer = {idx: answer for answer, idx in answer_to_id.items()}
    sample_ids = [answer_to_id[row.answer] for row in task_rows]
    correct_id = answer_to_id[next(iter(correct_answers))]

    def bounded_should_stop(counts: NDArray[np.int_], samples_seen: int) -> bool:
        return samples_seen >= len(sample_ids) or should_stop(counts, samples_seen)

    result = run_stream(sample_ids, correct_id, len(answer_vocab), bounded_should_stop)
    used_rows = task_rows[: result.samples_used]
    token_count: int | None
    if all(row.token_count is not None for row in used_rows):
        token_count = sum(row.token_count or 0 for row in used_rows)
    else:
        token_count = None
    prediction = id_to_answer[result.prediction]
    correct_answer = id_to_answer[correct_id]
    return TraceReplayResult(
        task_id=task_rows[0].task_id,
        prediction=prediction,
        correct_answer=correct_answer,
        correct=prediction == correct_answer,
        samples_used=result.samples_used,
        token_count=token_count,
    )


def evaluate_trace_policy(
    name: str,
    rows: Sequence[AnswerTraceRow],
    should_stop_factory: Callable[[], StopRule],
) -> dict[str, float | int | str]:
    """Evaluate a stopping policy on cached string-answer traces."""

    grouped = group_answer_traces(rows)
    outcomes = [run_trace(task_rows, should_stop_factory()) for task_rows in grouped.values()]
    samples = np.array([outcome.samples_used for outcome in outcomes], dtype=float)
    token_values = [outcome.token_count for outcome in outcomes if outcome.token_count is not None]
    mean_tokens = float(np.mean(token_values)) if token_values else float("nan")
    return {
        "policy": name,
        "tasks": len(outcomes),
        "accuracy": float(np.mean([outcome.correct for outcome in outcomes])),
        "mean_samples": float(np.mean(samples)),
        "median_samples": float(np.median(samples)),
        "p90_samples": float(np.quantile(samples, 0.9)),
        "max_samples": int(np.max(samples)),
        "mean_tokens": mean_tokens,
    }


def format_metrics_table(metrics: Sequence[PolicyMetrics]) -> str:
    """Render policy metrics as a Markdown table."""

    header = (
        "| policy | accuracy | mean samples | median | p90 | max | accuracy/sample |\n"
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    rows = [header]
    for item in metrics:
        rows.append(
            f"| {item.name} | {item.accuracy:.3f} | {item.mean_samples:.2f} | "
            f"{item.median_samples:.1f} | {item.p90_samples:.1f} | "
            f"{item.max_samples:d} | {item.efficiency:.4f} |"
        )
    return "\n".join(rows)


def _required_text(row: dict[str, str], column: str, line_number: int) -> str:
    value = row[column].strip()
    if not value:
        raise ValueError(f"{column} must be non-empty at line {line_number}")
    return value


def _nonnegative_int(value: str, column: str, line_number: int) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{column} must be an integer at line {line_number}") from exc
    if parsed < 0:
        raise ValueError(f"{column} must be non-negative at line {line_number}")
    return parsed


def _optional_nonnegative_int(value: str | None, column: str, line_number: int) -> int | None:
    if value is None or value.strip() == "":
        return None
    return _nonnegative_int(value, column, line_number)

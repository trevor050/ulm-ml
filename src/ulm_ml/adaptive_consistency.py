"""Adaptive stopping rules for self-consistency style reasoning.

The utilities in this module model the last stage of chain-of-thought
self-consistency: a black-box model emits answer samples, and an aggregator
must decide when another sample is still worth buying.  The code deliberately
avoids any LLM dependency so policies can be stress-tested on calibrated
sample streams before spending real inference budget.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

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

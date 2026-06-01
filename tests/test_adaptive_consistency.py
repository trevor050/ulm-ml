import numpy as np
import pytest

from ulm_ml.adaptive_consistency import (
    AnswerTraceRow,
    evaluate_policy,
    fixed_budget_rule,
    format_metrics_table,
    load_answer_trace_csv,
    posterior_confidence_rule,
    posterior_leader_probability,
    run_stream,
    sample_answer_streams,
    synthetic_answer_distributions,
    vote_margin_rule,
)


def test_fixed_budget_stream_uses_requested_number_of_samples() -> None:
    result = run_stream([1, 0, 0, 1, 0], 0, 2, fixed_budget_rule(5))

    assert result.prediction == 0
    assert result.correct
    assert result.samples_used == 5
    assert result.counts == (3, 2)


def test_vote_margin_rule_can_stop_early() -> None:
    result = run_stream([0, 0, 0, 1, 1, 1], 0, 2, vote_margin_rule(2, 2, 6))

    assert result.samples_used == 2
    assert result.prediction == 0


def test_posterior_probability_increases_with_stronger_leader() -> None:
    rng = np.random.default_rng(123)

    weak = posterior_leader_probability(np.array([3, 2]), draws=2048, rng=rng)
    strong = posterior_leader_probability(np.array([9, 1]), draws=2048, rng=rng)

    assert strong > weak
    assert strong > 0.95


def test_posterior_rule_respects_hard_cap() -> None:
    rule = posterior_confidence_rule(
        min_samples=2, confidence=0.999, max_samples=4, draws=128, seed=2
    )
    result = run_stream([0, 1, 0, 1, 0, 1], 0, 2, rule)

    assert result.samples_used == 4


def test_synthetic_evaluation_renders_markdown_table() -> None:
    rng = np.random.default_rng(4)
    distributions = synthetic_answer_distributions(num_tasks=20, num_answers=4, rng=rng)
    streams = sample_answer_streams(distributions, max_samples=8, rng=rng)

    metrics = [evaluate_policy("fixed-8", streams, lambda: fixed_budget_rule(8))]
    table = format_metrics_table(metrics)

    assert metrics[0].max_samples == 8
    assert "| fixed-8 |" in table


def test_load_answer_trace_csv_returns_typed_rows_sorted_by_trace_order(tmp_path) -> None:
    trace_path = tmp_path / "answer_traces.csv"
    trace_path.write_text(
        "\n".join(
            [
                "task_id,sample_index,answer,correct_answer,token_count",
                "gsm8k-2,1,17,42,21",
                "gsm8k-1,0,8,8,",
                "gsm8k-2,0,42,42,19",
            ]
        ),
        encoding="utf-8",
    )

    rows = load_answer_trace_csv(trace_path)

    assert rows == [
        AnswerTraceRow("gsm8k-1", 0, "8", "8", None),
        AnswerTraceRow("gsm8k-2", 0, "42", "42", 19),
        AnswerTraceRow("gsm8k-2", 1, "17", "42", 21),
    ]
    assert rows[0].is_correct
    assert not rows[-1].is_correct


def test_load_answer_trace_csv_rejects_missing_required_columns(tmp_path) -> None:
    trace_path = tmp_path / "answer_traces.csv"
    trace_path.write_text("task_id,answer,correct_answer\np1,yes,yes\n", encoding="utf-8")

    with pytest.raises(ValueError, match="sample_index"):
        load_answer_trace_csv(trace_path)

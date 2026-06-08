#!/usr/bin/env python3
"""Ablation and stress tests for the CSS simulator."""

from __future__ import annotations

import csv
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
SIM = runpy.run_path(str(ROOT / "work" / "stability_gated_tts_sim.py"))


FEATURE_SETS = {
    "all": [0, 1, 2, 3, 4, 5, 6, 7],
    "no_stability": [1, 2, 3, 4, 5, 6, 7],
    "consensus_only": [1, 2, 3, 4, 7],
    "score_only": [5, 6, 7],
    "stability_only": [0, 7],
    "support_only": [1, 7],
}


def split_pool(pool, n, train_size, test_size):
    correct = pool["correct"][:, :n]
    answer_group = pool["answer_group"][:, :n]
    score = pool["score"][:, :n]
    probe_score = pool["probe_score"][:, :, :n]

    train_slice = slice(0, train_size)
    test_slice = slice(train_size, train_size + test_size)
    return (
        (correct[train_slice], answer_group[train_slice], score[train_slice], probe_score[train_slice]),
        (correct[test_slice], answer_group[test_slice], score[test_slice], probe_score[test_slice]),
    )


def base_choices(correct, answer_group, score):
    idx = np.arange(correct.shape[0])
    bon = np.argmax(score, axis=1)
    maj = SIM["majority_answer_choice"](answer_group)
    return {
        "best_of_n": correct[idx, bon],
        "self_consistency": correct[idx, maj],
        "oracle_switch": correct[idx, np.where(correct[idx, bon] & ~correct[idx, maj], bon, maj)],
        "bon_idx": bon,
        "maj_idx": maj,
    }


def train_and_eval(train, test, feature_cols):
    train_correct, train_ag, train_score, train_probe = train
    test_correct, test_ag, test_score, test_probe = test
    train_choices = base_choices(train_correct, train_ag, train_score)
    test_choices = base_choices(test_correct, test_ag, test_score)

    train_x = SIM["candidate_set_features"](train_ag, train_score, train_probe)[:, feature_cols]
    test_x = SIM["candidate_set_features"](test_ag, test_score, test_probe)[:, feature_cols]
    model = SIM["fit_logistic_switch"](train_x, train_choices["best_of_n"], train_choices["self_consistency"])
    use_bon, prob = SIM["predict_logistic_switch"](model, test_x)
    idx = np.arange(test_correct.shape[0])
    switch_idx = np.where(use_bon, test_choices["bon_idx"], test_choices["maj_idx"])
    return {
        "best_of_n": float(test_choices["best_of_n"].mean()),
        "self_consistency": float(test_choices["self_consistency"].mean()),
        "oracle_switch": float(test_choices["oracle_switch"].mean()),
        "css_switch": float(test_correct[idx, switch_idx].mean()),
        "switch_used_bon_rate": float(use_bon.mean()),
        "switch_mean_prob": float(prob.mean()),
    }


def feature_ablation():
    cfg = SIM["SimConfig"](num_problems=24_000, max_n=64, probe_count=9, seed=9101)
    pool = SIM["simulate_pool"](0.25, cfg)
    train, test = split_pool(pool, n=32, train_size=4_000, test_size=16_000)
    rows = []
    for name, cols in FEATURE_SETS.items():
        out = train_and_eval(train, test, cols)
        rows.append({"experiment": "feature_ablation", "setting": name, "train_trap": 0.25, "test_trap": 0.25, "N": 32, "train_size": 4000, **out})
    return rows


def calibration_curve():
    cfg = SIM["SimConfig"](num_problems=26_000, max_n=64, probe_count=9, seed=9102)
    pool = SIM["simulate_pool"](0.25, cfg)
    rows = []
    for train_size in [50, 100, 250, 500, 1_000, 2_000, 4_000, 8_000]:
        train, test = split_pool(pool, n=32, train_size=train_size, test_size=16_000)
        out = train_and_eval(train, test, FEATURE_SETS["all"])
        rows.append({"experiment": "calibration_curve", "setting": "all", "train_trap": 0.25, "test_trap": 0.25, "N": 32, "train_size": train_size, **out})
    return rows


def mined_calibration():
    cfg = SIM["SimConfig"](num_problems=34_000, max_n=64, probe_count=9, seed=9155)
    pool = SIM["simulate_pool"](0.25, cfg)
    correct = pool["correct"][:, :32]
    answer_group = pool["answer_group"][:, :32]
    score = pool["score"][:, :32]
    probe_score = pool["probe_score"][:, :, :32]

    calib_slice = slice(0, 12_000)
    test_slice = slice(16_000, 32_000)
    test = (
        correct[test_slice],
        answer_group[test_slice],
        score[test_slice],
        probe_score[test_slice],
    )

    calib_features = SIM["candidate_set_features"](
        answer_group[calib_slice], score[calib_slice], probe_score[calib_slice]
    )
    # Unlabeled mining score: prioritize selector disagreement, low top-answer
    # support, high answer entropy, and high verifier confidence. This mines the
    # exact region where routing labels are most informative.
    stability, support, _majority, top_is_majority, entropy, z_margin, z_top, _log_n = calib_features.T
    mining_score = (
        3.0 * (1.0 - top_is_majority)
        + 1.2 * (1.0 - support)
        + 0.8 * entropy
        + 0.2 * np.maximum(z_top, 0.0)
        + 0.1 * np.maximum(z_margin, 0.0)
        + 0.0 * stability
    )
    mined_order = np.argsort(-mining_score)

    rows = []
    for train_size in [50, 100, 250, 500, 1_000, 2_000]:
        for mode, order in [
            ("uniform", np.arange(12_000)),
            ("disagreement_mined", mined_order),
        ]:
            idx = order[:train_size]
            train = (
                correct[calib_slice][idx],
                answer_group[calib_slice][idx],
                score[calib_slice][idx],
                probe_score[calib_slice][idx],
            )
            out = train_and_eval(train, test, FEATURE_SETS["all"])
            rows.append(
                {
                    "experiment": "mined_calibration",
                    "setting": mode,
                    "train_trap": 0.25,
                    "test_trap": 0.25,
                    "N": 32,
                    "train_size": train_size,
                    **out,
                }
            )
    return rows


def distribution_shift():
    rows = []
    traps = [0.0, 0.10, 0.25, 0.40]
    pools = {}
    for trap in traps:
        cfg = SIM["SimConfig"](num_problems=24_000, max_n=64, probe_count=9, seed=9200 + int(trap * 1000))
        pools[trap] = SIM["simulate_pool"](trap, cfg)
    for train_trap in traps:
        train, _ = split_pool(pools[train_trap], n=32, train_size=4_000, test_size=16_000)
        for test_trap in traps:
            _, test = split_pool(pools[test_trap], n=32, train_size=4_000, test_size=16_000)
            out = train_and_eval(train, test, FEATURE_SETS["all"])
            rows.append({"experiment": "distribution_shift", "setting": "all", "train_trap": train_trap, "test_trap": test_trap, "N": 32, "train_size": 4000, **out})
    return rows


def n_transfer():
    rows = []
    cfg = SIM["SimConfig"](num_problems=30_000, max_n=128, probe_count=9, seed=9301)
    pool = SIM["simulate_pool"](0.25, cfg)
    for train_n in [8, 32, 128]:
        train, _ = split_pool(pool, n=train_n, train_size=4_000, test_size=16_000)
        train_correct, train_ag, train_score, train_probe = train
        train_choices = base_choices(train_correct, train_ag, train_score)
        train_x = SIM["candidate_set_features"](train_ag, train_score, train_probe)[:, FEATURE_SETS["all"]]
        model = SIM["fit_logistic_switch"](train_x, train_choices["best_of_n"], train_choices["self_consistency"])

        for test_n in [8, 16, 32, 64, 128]:
            _, test = split_pool(pool, n=test_n, train_size=4_000, test_size=16_000)
            test_correct, test_ag, test_score, test_probe = test
            test_choices = base_choices(test_correct, test_ag, test_score)
            test_x = SIM["candidate_set_features"](test_ag, test_score, test_probe)[:, FEATURE_SETS["all"]]
            use_bon, prob = SIM["predict_logistic_switch"](model, test_x)
            idx = np.arange(test_correct.shape[0])
            switch_idx = np.where(use_bon, test_choices["bon_idx"], test_choices["maj_idx"])
            rows.append(
                {
                    "experiment": "n_transfer",
                    "setting": f"train_N_{train_n}",
                    "train_trap": 0.25,
                    "test_trap": 0.25,
                    "N": test_n,
                    "train_size": 4000,
                    "best_of_n": float(test_choices["best_of_n"].mean()),
                    "self_consistency": float(test_choices["self_consistency"].mean()),
                    "oracle_switch": float(test_choices["oracle_switch"].mean()),
                    "css_switch": float(test_correct[idx, switch_idx].mean()),
                    "switch_used_bon_rate": float(use_bon.mean()),
                    "switch_mean_prob": float(prob.mean()),
                }
            )
    return rows


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "experiment",
        "setting",
        "train_trap",
        "test_trap",
        "N",
        "train_size",
        "best_of_n",
        "self_consistency",
        "css_switch",
        "oracle_switch",
        "switch_used_bon_rate",
        "switch_mean_prob",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_md(rows, path):
    def fmt(v):
        if isinstance(v, float):
            return f"{v:.3f}"
        return str(v)

    sections = [
        ("Feature Ablation", [r for r in rows if r["experiment"] == "feature_ablation"]),
        ("Calibration Curve", [r for r in rows if r["experiment"] == "calibration_curve"]),
        ("Mined Calibration", [r for r in rows if r["experiment"] == "mined_calibration"]),
        ("Distribution Shift", [r for r in rows if r["experiment"] == "distribution_shift"]),
        ("N Transfer", [r for r in rows if r["experiment"] == "n_transfer"]),
    ]
    lines = ["# CSS Ablation Lab", ""]
    lines.append("All experiments are synthetic stress tests around verifier-trap instances. They are meant to decide whether CSS has a real shape before spending more GPU time.")
    lines.append("")
    for title, subset in sections:
        lines.append(f"## {title}")
        lines.append("")
        if title == "Feature Ablation":
            fields = ["setting", "best_of_n", "self_consistency", "css_switch", "oracle_switch", "switch_used_bon_rate"]
        elif title == "Calibration Curve":
            fields = ["train_size", "best_of_n", "self_consistency", "css_switch", "oracle_switch", "switch_used_bon_rate"]
        elif title == "Mined Calibration":
            fields = ["setting", "train_size", "best_of_n", "self_consistency", "css_switch", "oracle_switch", "switch_used_bon_rate"]
        elif title == "Distribution Shift":
            fields = ["train_trap", "test_trap", "best_of_n", "self_consistency", "css_switch", "oracle_switch"]
        else:
            fields = ["setting", "N", "best_of_n", "self_consistency", "css_switch", "oracle_switch"]
        lines.append("| " + " | ".join(fields) + " |")
        lines.append("|" + "|".join(["---"] * len(fields)) + "|")
        for row in subset:
            lines.append("| " + " | ".join(fmt(row[f]) for f in fields) + " |")
        lines.append("")
    path.write_text("\n".join(lines))


def main():
    rows = []
    for fn in [feature_ablation, calibration_curve, mined_calibration, distribution_shift, n_transfer]:
        print(f"running {fn.__name__}", flush=True)
        rows.extend(fn())
    write_csv(rows, OUT / "css_ablation_lab.csv")
    write_md(rows, OUT / "css_ablation_lab.md")
    print(f"wrote {OUT / 'css_ablation_lab.csv'}")
    print(f"wrote {OUT / 'css_ablation_lab.md'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CSS on real repeated-sampling traces from ScalingIntelligence/monkey_business.

This is the first non-toy benchmark for Candidate-Set Selector Switching:

1. Load GSM8K Llama-3-8B-Instruct samples with correctness labels.
2. Train a cheap candidate-level verifier from text-only features on train
   problems.
3. On held-out candidate sets, compare verifier Best-of-N, self-consistency,
   fixed gates, CSS router, oracle switch, and any-correct coverage.

No sklearn/pandas/torch dependency.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import warnings
from collections import Counter
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore", category=SyntaxWarning)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DATA_PATH = ROOT / "work" / "GSM8K_Llama-3-8B-Instruct.json"


ANSWER_RE = re.compile(r"####\s*(-?[0-9][0-9,]*(?:\.\d+)?)")
NUM_RE = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?")
CALC_RE = re.compile(r"<<([^<>]+?)=([^<>]+?)>>")
FRAC_RE = re.compile(r"(-?)\\frac\{([^{}]+)\}\{([^{}]+)\}")


def normalize_number(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.replace(",", "").strip()
    try:
        val = float(raw)
    except ValueError:
        return None
    if not math.isfinite(val):
        return raw.lower().strip()
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    return f"{val:.6f}".rstrip("0").rstrip(".")


def extract_answer(sample: str) -> str | None:
    matches = ANSWER_RE.findall(sample)
    if matches:
        return normalize_number(matches[-1])
    boxed = extract_last_boxed(sample)
    if boxed:
        return normalize_latex_answer(boxed)
    final = re.findall(r"Final Answer:\s*(.*)", sample, flags=re.I)
    if final:
        boxed = extract_last_boxed(final[-1])
        if boxed:
            return normalize_latex_answer(boxed)
        normalized = normalize_latex_answer(final[-1])
        if normalized is not None and not re.fullmatch(r".*[a-z].*", normalized):
            return normalized
        nums = NUM_RE.findall(final[-1])
        if nums:
            return normalize_number(nums[-1])
    nums = NUM_RE.findall(sample)
    return normalize_number(nums[-1]) if nums else None


def extract_last_boxed(text: str) -> str | None:
    token = r"\boxed{"
    starts = [m.start() for m in re.finditer(re.escape(token), text)]
    for start in reversed(starts):
        i = start + len(token)
        depth = 1
        out = []
        while i < len(text):
            ch = text[i]
            if ch == "{":
                depth += 1
                out.append(ch)
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return "".join(out).strip()
                out.append(ch)
            else:
                out.append(ch)
            i += 1
    return None


def normalize_latex_answer(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip().strip("$").strip()
    if "=" in raw:
        raw = raw.split("=")[-1]
    num = normalize_number(raw)
    if num is not None:
        return num
    cleaned = raw.lower()
    cleaned = cleaned.replace("\\left", "").replace("\\right", "")
    cleaned = cleaned.replace("\\,", "").replace("\\!", "")
    cleaned = re.sub(r"\\(?:mathrm|text)\{([^{}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\boxed\{([^{}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\dfrac", r"\\frac", cleaned)
    frac = FRAC_RE.search(cleaned)
    if frac:
        sign, numerator, denominator = frac.groups()
        numerator = normalize_latex_answer(numerator)
        denominator = normalize_latex_answer(denominator)
        if numerator is not None and denominator is not None:
            return f"{sign}{numerator}/{denominator}"
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = cleaned.strip(".;,")
    if re.fullmatch(r"-?\d+/-?\d+", cleaned):
        return cleaned
    return cleaned or None


def safe_eval_arith(expr: str) -> float | None:
    expr = expr.replace(",", "").replace("$", "").replace("x", "*").replace("X", "*")
    if not re.fullmatch(r"[0-9\.\+\-\*/\(\) ]+", expr):
        return None
    try:
        return float(eval(expr, {"__builtins__": {}}, {}))
    except Exception:
        return None


def equation_stats(sample: str) -> tuple[int, int, int]:
    total = valid = invalid = 0
    for expr, rhs in CALC_RE.findall(sample):
        total += 1
        lhs_val = safe_eval_arith(expr)
        rhs_num = NUM_RE.findall(rhs.replace(",", ""))
        rhs_val = float(rhs_num[-1]) if rhs_num else None
        if lhs_val is None or rhs_val is None:
            continue
        if abs(lhs_val - rhs_val) <= max(1e-6, abs(rhs_val) * 1e-4):
            valid += 1
        else:
            invalid += 1
    return total, valid, invalid


def candidate_features(sample: str) -> list[float]:
    chars = len(sample)
    words = len(sample.split())
    lines = [ln for ln in sample.splitlines() if ln.strip()]
    nums = NUM_RE.findall(sample)
    calc_total, calc_valid, calc_invalid = equation_stats(sample)
    has_answer = 1.0 if ANSWER_RE.search(sample) else 0.0
    answer_near_end = 1.0 if "####" in sample[-80:] else 0.0
    calc_frac_valid = calc_valid / calc_total if calc_total else 0.0
    calc_frac_invalid = calc_invalid / calc_total if calc_total else 0.0
    return [
        math.log1p(chars),
        math.log1p(words),
        min(chars / 512.0, 4.0),
        has_answer,
        answer_near_end,
        math.log1p(len(nums)),
        math.log1p(calc_total),
        calc_frac_valid,
        calc_frac_invalid,
        min(len(lines), 12) / 12.0,
        1.0 if "####" in sample else 0.0,
    ]


def fit_logistic(x: np.ndarray, y: np.ndarray, steps=900, lr=0.06, l2=1e-3, weights=None):
    mean = x.mean(axis=0)
    std = x.std(axis=0) + 1e-6
    xs = (x - mean) / std
    xs = np.column_stack([np.ones(xs.shape[0]), xs])
    w = np.zeros(xs.shape[1])
    if weights is None:
        weights = np.ones_like(y, dtype=float)
    denom = weights.sum()
    for _ in range(steps):
        logits = np.clip(xs @ w, -30, 30)
        pred = 1.0 / (1.0 + np.exp(-logits))
        grad = xs.T @ ((pred - y) * weights) / denom
        grad[1:] += l2 * w[1:]
        w -= lr * grad
    return {"w": w, "mean": mean, "std": std}


def predict_logistic(model, x: np.ndarray) -> np.ndarray:
    xs = (x - model["mean"]) / model["std"]
    xs = np.column_stack([np.ones(xs.shape[0]), xs])
    return 1.0 / (1.0 + np.exp(-np.clip(xs @ model["w"], -30, 30)))


def load_data(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def train_candidate_verifier(data, train_problem_ids, max_per_problem, seed):
    rng = random.Random(seed)
    feats, labels = [], []
    for pid in train_problem_ids:
        row = data[pid]
        idxs = list(range(len(row["samples"])))
        rng.shuffle(idxs)
        for i in idxs[:max_per_problem]:
            feats.append(candidate_features(row["samples"][i]))
            labels.append(float(row["is_corrects"][i]))
    x = np.array(feats, dtype=float)
    y = np.array(labels, dtype=float)
    pos = y.mean()
    weights = np.where(y > 0.5, 0.5 / max(pos, 1e-6), 0.5 / max(1 - pos, 1e-6))
    model = fit_logistic(x, y, steps=1100, lr=0.05, l2=2e-3, weights=weights)
    return model, {"samples": len(y), "positive_rate": float(pos)}


def score_samples(model, samples):
    x = np.array([candidate_features(s) for s in samples], dtype=float)
    return predict_logistic(model, x)


def answer_entropy(preds):
    vals = [p for p in preds if p is not None]
    if not vals:
        return 0.0
    counts = np.array(list(Counter(vals).values()), dtype=float)
    probs = counts / counts.sum()
    return float(-(probs * np.log(probs + 1e-12)).sum() / math.log(len(preds) + 1))


def majority_idx(preds):
    vals = [p for p in preds if p is not None]
    if not vals:
        return 0
    top, _ = Counter(vals).most_common(1)[0]
    for i, p in enumerate(preds):
        if p == top:
            return i
    return 0


def set_features(preds, scores, bon_idx, sc_idx, n):
    top_pred = preds[bon_idx]
    vals = [p for p in preds if p is not None]
    counts = Counter(vals)
    total = max(1, len(vals))
    support = counts.get(top_pred, 0) / max(1, n) if top_pred is not None else 0.0
    majority_support = counts.most_common(1)[0][1] / total if counts else 0.0
    top_is_majority = 1.0 if top_pred is not None and top_pred == preds[sc_idx] else 0.0
    sorted_scores = np.sort(scores)
    margin = float(sorted_scores[-1] - sorted_scores[-2]) if len(scores) > 1 else 1.0
    std = float(scores.std() + 1e-6)
    return [
        support,
        majority_support,
        answer_entropy(preds),
        top_is_majority,
        margin / std,
        float((scores[bon_idx] - scores.mean()) / std),
        float((scores[sc_idx] - scores.mean()) / std),
        math.log2(n),
        len(set(vals)) / max(1, n),
    ]


def support_scores(preds):
    counts = Counter(p for p in preds if p is not None)
    return np.array(
        [counts.get(p, 0) / max(1, len(preds)) if p is not None else 0.0 for p in preds],
        dtype=float,
    )


def make_trial(row, scores_all, answers_all, n, rng, support_weight=0.0):
    idxs = rng.sample(range(len(row["samples"])), n)
    labels = np.array([row["is_corrects"][i] for i in idxs], dtype=bool)
    preds = [answers_all[i] for i in idxs]
    scores = np.array([scores_all[i] for i in idxs], dtype=float)
    hybrid_scores = scores + support_weight * support_scores(preds)
    first = 0
    bon = int(np.argmax(scores))
    hybrid = int(np.argmax(hybrid_scores))
    sc = majority_idx(preds)
    sorted_scores = np.sort(scores)
    margin = sorted_scores[-1] - sorted_scores[-2] if n > 1 else 1.0
    margin_gate = bon if margin >= 0.10 else sc
    oracle = bon if labels[bon] and not labels[sc] else sc
    oracle_hybrid = hybrid if labels[hybrid] and not labels[sc] else sc
    return {
        "features": set_features(preds, scores, bon, sc, n),
        "labels": labels,
        "choices": {
            "first": first,
            "best_of_n": bon,
            "hybrid_bon": hybrid,
            "self_consistency": sc,
            "margin_gate": margin_gate,
            "oracle_switch": oracle,
            "oracle_hybrid_switch": oracle_hybrid,
        },
        "any_correct": bool(labels.any()),
        "bon_sc_disagree": int(preds[bon] != preds[sc]),
        "hybrid_sc_disagree": int(preds[hybrid] != preds[sc]),
    }


def build_trials(data, scores_by_pid, answers_by_pid, problem_ids, ns, trials_per_problem, seed, support_weight=0.0):
    rng = random.Random(seed)
    trials = []
    for pid in problem_ids:
        row = data[pid]
        for n in ns:
            for _ in range(trials_per_problem):
                t = make_trial(row, scores_by_pid[pid], answers_by_pid[pid], n, rng, support_weight=support_weight)
                t["pid"] = pid
                t["N"] = n
                trials.append(t)
    return trials


def train_css_router(trials, mode="uniform", max_train=None, selector="best_of_n"):
    if mode == "mined":
        def mining_score(t):
            f = t["features"]
            support, maj_support, entropy, top_is_maj, z_margin, z_top, _z_sc, _logn, unique_ratio = f
            return 3.0 * (1.0 - top_is_maj) + 1.2 * (1.0 - support) + 0.8 * entropy + 0.2 * max(z_top, 0) + 0.1 * max(z_margin, 0) + 0.3 * unique_ratio
        ordered = sorted(trials, key=mining_score, reverse=True)
    else:
        ordered = list(trials)
    if max_train:
        ordered = ordered[:max_train]
    x = np.array([t["features"] for t in ordered], dtype=float)
    bon_y = np.array([float(t["labels"][t["choices"][selector]]) for t in ordered])
    sc_y = np.array([float(t["labels"][t["choices"]["self_consistency"]]) for t in ordered])
    y = np.where((bon_y > 0.5) & (sc_y < 0.5), 1.0, 0.0)
    weights = np.where(bon_y == sc_y, 0.15, 1.0)
    return fit_logistic(x, y, steps=900, lr=0.08, l2=1e-3, weights=weights)


def eval_trials(trials, router=None, selector="best_of_n"):
    metrics = Counter()
    by_n = {}
    rows = []
    for t in trials:
        labels = t["labels"]
        choices = t["choices"]
        css_choice = None
        css_prob = 0.0
        if router is not None:
            css_prob = float(predict_logistic(router, np.array([t["features"]], dtype=float))[0])
            css_choice = choices[selector] if css_prob >= 0.5 else choices["self_consistency"]
        values = {
            "first": bool(labels[choices["first"]]),
            "best_of_n": bool(labels[choices["best_of_n"]]),
            "hybrid_bon": bool(labels[choices["hybrid_bon"]]),
            "self_consistency": bool(labels[choices["self_consistency"]]),
            "margin_gate": bool(labels[choices["margin_gate"]]),
            "oracle_switch": bool(labels[choices["oracle_switch"]]),
            "oracle_hybrid_switch": bool(labels[choices["oracle_hybrid_switch"]]),
            "any_correct": t["any_correct"],
        }
        if css_choice is not None:
            values["css_switch"] = bool(labels[css_choice])
            values["css_used_bon"] = css_choice == choices[selector]
            values["css_prob_bon"] = css_prob
        for k, v in values.items():
            metrics[k] += float(v)
        n = t["N"]
        by_n.setdefault(n, Counter())
        for k, v in values.items():
            by_n[n][k] += float(v)
        by_n[n]["count"] += 1
        rows.append({"N": n, **values})
    denom = len(trials)
    summary = {k: float(v / denom) for k, v in metrics.items()}
    per_n = []
    for n, c in sorted(by_n.items()):
        count = c.pop("count")
        per_n.append({"N": n, "count": int(count), **{k: float(v / count) for k, v in c.items()}})
    return summary, per_n, rows


def bootstrap_ci(rows, key, rounds=500, seed=0):
    rng = random.Random(seed)
    vals = [float(r[key]) for r in rows if key in r]
    if not vals:
        return (0.0, 0.0)
    means = []
    for _ in range(rounds):
        sample = [vals[rng.randrange(len(vals))] for _ in vals]
        means.append(sum(sample) / len(sample))
    means.sort()
    return means[int(0.025 * rounds)], means[int(0.975 * rounds)]


def write_outputs(verifier_info, overall, per_n, rows, train_ids, calib_ids, test_ids, args):
    OUT.mkdir(parents=True, exist_ok=True)
    prefix = args.output_prefix or "monkey_css_realbench"
    csv_path = OUT / f"{prefix}_by_n.csv"
    fields = [
        "N",
        "count",
        "first",
        "best_of_n",
        "hybrid_bon",
        "self_consistency",
        "margin_gate",
        "css_switch",
        "oracle_switch",
        "oracle_hybrid_switch",
        "any_correct",
        "css_used_bon",
        "css_prob_bon",
    ]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in per_n:
            writer.writerow({k: row.get(k, "") for k in fields})

    overall_path = OUT / f"{prefix}_summary.csv"
    ci_keys = ["best_of_n", "hybrid_bon", "self_consistency", "css_switch", "oracle_switch", "oracle_hybrid_switch", "any_correct"]
    with overall_path.open("w", newline="") as f:
        fields2 = ["metric", "value", "ci_low", "ci_high"]
        writer = csv.DictWriter(f, fieldnames=fields2)
        writer.writeheader()
        for k, v in sorted(overall.items()):
            lo, hi = bootstrap_ci(rows, k, seed=args.seed) if k in ci_keys else ("", "")
            writer.writerow({"metric": k, "value": v, "ci_low": lo, "ci_high": hi})

    md = OUT / f"{prefix}.md"
    lines = [
        "# Monkey Business CSS Real Benchmark",
        "",
        f"Dataset: `ScalingIntelligence/monkey_business`, config `{args.dataset_label}`.",
        "This uses real repeated-sampling traces with 10,000 samples and correctness labels per problem.",
        "",
        f"Problem split: {len(train_ids)} verifier-train, {len(calib_ids)} CSS-calibration, {len(test_ids)} test.",
        f"Candidate verifier train samples: {verifier_info['samples']} with positive rate {verifier_info['positive_rate']:.3f}.",
        f"Trials: N in `{args.ns}`, {args.trials_per_problem} random candidate sets per problem per N.",
        f"Hybrid support weight: `{args.support_weight}`. CSS routes between `{args.css_selector}` and self-consistency.",
        f"CSS calibration mode: `{args.css_mode}`, max router train trials: `{args.css_train_limit}`.",
        "",
        "## Overall Test Accuracy",
        "",
        "| Method | Accuracy | 95% bootstrap CI |",
        "|---|---:|---:|",
    ]
    name_order = [
        "first",
        "best_of_n",
        "hybrid_bon",
        "self_consistency",
        "margin_gate",
        "css_switch",
        "oracle_switch",
        "oracle_hybrid_switch",
        "any_correct",
        "css_used_bon",
    ]
    for k in name_order:
        if k in overall:
            lo, hi = bootstrap_ci(rows, k, seed=args.seed) if k in ci_keys else ("", "")
            ci = f"{lo:.3f}-{hi:.3f}" if lo != "" else ""
            lines.append(f"| {k} | {overall[k]:.3f} | {ci} |")
    best_base = max(overall["best_of_n"], overall["hybrid_bon"], overall["self_consistency"], overall["margin_gate"])
    oracle_key = "oracle_hybrid_switch" if args.css_selector == "hybrid_bon" else "oracle_switch"
    denom = overall[oracle_key] - best_base
    closed = (overall["css_switch"] - best_base) / denom if denom > 1e-9 else 0.0
    lines += [
        "",
        f"Oracle-switch headroom over best base selector: `{denom:.3f}`.",
        f"CSS headroom closed: `{closed:.3f}`.",
        "",
        "## By N",
        "",
        "| N | First | BoN verifier | Hybrid BoN | Self-consistency | Margin gate | CSS | Oracle switch | Hybrid oracle | Any-correct | CSS uses routed selector |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in per_n:
        lines.append(
            f"| {r['N']} | {r.get('first',0):.3f} | {r.get('best_of_n',0):.3f} | {r.get('hybrid_bon',0):.3f} | "
            f"{r.get('self_consistency',0):.3f} | {r.get('margin_gate',0):.3f} | {r.get('css_switch',0):.3f} | "
            f"{r.get('oracle_switch',0):.3f} | {r.get('oracle_hybrid_switch',0):.3f} | {r.get('any_correct',0):.3f} | "
            f"{r.get('css_used_bon',0):.3f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- This is no longer a toy simulator: candidate sets and correctness labels come from published repeated-sampling traces.",
        "- The verifier is deliberately cheap and text-feature based. That makes it a weak but inspectable stand-in for a learned verifier.",
        "- CSS is evaluated on held-out problems, not held-out samples from the same problems.",
        "- The key number is not only CSS accuracy; it is oracle-switch headroom and the fraction CSS closes.",
    ]
    md.write_text("\n".join(lines))
    return md, csv_path, overall_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(DATA_PATH))
    parser.add_argument("--dataset-label", default="GSM8K_Llama-3-8B-Instruct")
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--verifier-train-problems", type=int, default=45)
    parser.add_argument("--calib-problems", type=int, default=32)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=1800)
    parser.add_argument("--trials-per-problem", type=int, default=16)
    parser.add_argument("--ns", default="4,8,16,32,64,128,256")
    parser.add_argument("--css-mode", choices=["uniform", "mined"], default="mined")
    parser.add_argument("--css-train-limit", type=int, default=1200)
    parser.add_argument("--support-weight", type=float, default=0.0)
    parser.add_argument("--css-selector", choices=["best_of_n", "hybrid_bon"], default="best_of_n")
    parser.add_argument("--output-prefix", default="")
    args = parser.parse_args()

    data = load_data(Path(args.data))
    rng = random.Random(args.seed)
    problem_ids = list(range(len(data)))
    rng.shuffle(problem_ids)
    train_ids = problem_ids[: args.verifier_train_problems]
    calib_ids = problem_ids[args.verifier_train_problems : args.verifier_train_problems + args.calib_problems]
    test_ids = problem_ids[args.verifier_train_problems + args.calib_problems :]
    ns = [int(x) for x in args.ns.split(",") if x.strip()]

    print("training candidate verifier", flush=True)
    verifier, verifier_info = train_candidate_verifier(data, train_ids, args.verifier_samples_per_problem, args.seed)

    needed_ids = calib_ids + test_ids
    scores_by_pid, answers_by_pid = {}, {}
    for j, pid in enumerate(needed_ids, 1):
        row = data[pid]
        print(f"scoring problem {j}/{len(needed_ids)}", flush=True)
        scores_by_pid[pid] = score_samples(verifier, row["samples"])
        answers_by_pid[pid] = [extract_answer(s) for s in row["samples"]]

    print("building calibration/test trials", flush=True)
    calib_trials = build_trials(
        data,
        scores_by_pid,
        answers_by_pid,
        calib_ids,
        ns,
        args.trials_per_problem,
        args.seed + 1,
        support_weight=args.support_weight,
    )
    test_trials = build_trials(
        data,
        scores_by_pid,
        answers_by_pid,
        test_ids,
        ns,
        args.trials_per_problem,
        args.seed + 2,
        support_weight=args.support_weight,
    )
    router = train_css_router(calib_trials, mode=args.css_mode, max_train=args.css_train_limit, selector=args.css_selector)
    overall, per_n, rows = eval_trials(test_trials, router, selector=args.css_selector)
    md, csv_path, overall_path = write_outputs(verifier_info, overall, per_n, rows, train_ids, calib_ids, test_ids, args)
    print(md)
    print(csv_path)
    print(overall_path)
    print(Path(md).read_text())


if __name__ == "__main__":
    main()

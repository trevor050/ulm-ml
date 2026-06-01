# Adaptive Posterior Self-Consistency

## Status

Evidence level: **synthetic sanity check only**.

The current result in `reports/adaptive-consistency.md` is a simulator over
categorical answer distributions. It shows that the stopping rule behaves
plausibly when the assumptions are clean. It does **not** show that the method
saves real LLM calls on GSM8K, SVAMP, or any other benchmark.

The immediate research goal is trace replay: collect answer-only samples from a
real model once, then replay fixed-budget, vote-margin, and posterior policies
over identical prefixes.

## One-sentence idea

Self-consistency spends a fixed number of reasoning samples even when the answer
distribution has already converged; replace the fixed budget with a tiny
Dirichlet posterior test that asks how likely the current majority answer is to
remain the winner if sampling continued.

## Method

For a single task, let `c` be answer counts after `t` samples and use a symmetric
Dirichlet prior `Dirichlet(alpha)`. The posterior over the model's answer
probabilities is:

```text
p(answer probabilities | c) = Dirichlet(c + alpha)
```

Let `a* = argmax(c)` be the current majority answer. Estimate:

```text
P(p[a*] > max_j!=a* p[j] | c)
```

with Monte Carlo draws from the posterior. Stop if this probability exceeds a
confidence threshold, subject to a minimum sample count and a maximum budget.

The runnable implementation is in `src/ulm_ml/adaptive_consistency.py`.

## Synthetic result

The synthetic experiment generates heterogeneous categorical answer samplers,
where answer `0` is always treated as correct. That makes it useful for checking
policy mechanics, not benchmark performance.

Command:

```bash
python experiments/adaptive_consistency_synthetic.py
```

Observed behavior: on the synthetic suite, `posterior-0.95` matched fixed-32
accuracy while using roughly half the samples. This is a green light for a real
trace replay, not a claim of real inference savings.

## Trace replay schema

Real traces should be stored as answer-only CSV rows. Do not commit large raw
reasoning traces, prompts, or generated rationales unless they are tiny and
license-safe.

Required columns:

```text
task_id,sample_index,answer,correct_answer
```

Optional column:

```text
token_count
```

`load_answer_trace_csv(path)` loads this schema into `AnswerTraceRow` records and
sorts by `(task_id, sample_index)` so policies see deterministic prefixes. Extra
columns are ignored, so a local trace file can include split names, model names,
or prompt hashes.

Minimal example:

```csv
task_id,sample_index,answer,correct_answer,token_count
gsm8k-0001,0,42,42,89
gsm8k-0001,1,40,42,95
gsm8k-0002,0,17,17,76
```

## Minimum viable real experiment

1. Pick a small answer-extractable benchmark such as GSM8K or SVAMP.
2. Sample up to 32 stochastic answer traces per task from one fixed model and
   decoding configuration.
3. Store normalized final answers, gold answers, sample indices, and token counts
   using the CSV schema above.
4. Replay fixed budgets, vote-margin stopping, and posterior stopping over the
   exact same trace prefixes.
5. Tune only posterior confidence on a validation split.
6. Report accuracy, mean calls, mean generated tokens, p90 calls, and the
   Pareto frontier.

## Main caveats

- The posterior treats answer samples as iid draws from a categorical
  distribution. Real chain-of-thought samples can be correlated by prompt,
  decoding settings, answer extraction bugs, and model self-bias.
- The current synthetic setup fixes the correct answer to integer class `0`.
  Real benchmark replay must use per-task answer strings.
- A policy that saves calls by stopping early can hide extraction failures. The
  trace file should keep enough local metadata to audit normalization mistakes.

## References used for orientation

- Wei et al. introduced chain-of-thought prompting: <https://arxiv.org/abs/2201.11903>
- Wang et al. introduced self-consistency decoding: <https://arxiv.org/abs/2203.11171>
- Snell et al. studied inference-time compute allocation: <https://arxiv.org/abs/2408.03314>
- Zelikman et al. explored latent rationale generation in Quiet-STaR: <https://arxiv.org/abs/2403.09629>

# Candidate-Set Selector Switching: A Triage Layer for Test-Time Scaling

**Status:** v2 research pitch, June 1, 2026  
**Short version:** repeated sampling often finds a correct answer, but selection fails. Instead of betting on one selector, train a tiny black-box router that decides when to trust verifier Best-of-N and when to fall back to answer consensus. The router is cheap, calibratable, and explicitly aimed at verifier over-optimization.

## One-Sentence Pitch

Test-time scaling needs a **selector triage layer**: a small calibrated model that looks at the candidate set and routes each problem to the selector most likely to work on that instance.

## Why This Is The Right Problem

The current test-time scaling literature has created a very specific gap.

Repeated sampling can dramatically improve **coverage**, the chance that at least one generated candidate is correct. Brown et al.'s *Large Language Monkeys* shows coverage scaling over many orders of magnitude, but also reports that, when automatic verification is unavailable, majority voting and reward-model selection can plateau. Snell et al. show that test-time compute should be allocated adaptively because prompt-level difficulty matters. ROC-n-reroll then tightens the noose: verifier imperfection is not a minor implementation detail, it governs Best-of-N and rejection-sampling behavior through verifier ROC geometry, and low-compute behavior can fail to predict high-compute behavior.

So the pain is not "can we sample more?" The pain is:

> Given a candidate set that may contain a correct solution, which selector should we trust on this exact problem?

Most work tries to build a better scalar selector: PRMs, LLM judges, hidden-state rankers, reward models, process supervision, or calibrated rankers such as SCATR. Candidate-Set Selector Switching (CSS) is smaller and more modular. It asks whether we can learn a **selector reliability model** above existing selectors.

## Method

For each problem:

1. Generate N candidate solutions.
2. Compute a small selector portfolio:
   - first sample,
   - answer self-consistency,
   - verifier Best-of-N,
   - margin-gated verifier,
   - any other available selector.
3. Extract black-box candidate-set features:
   - support for the verifier top answer,
   - majority answer support,
   - answer-cluster entropy,
   - whether verifier top answer matches majority answer,
   - top-score margin,
   - normalized top score,
   - optional verifier rank stability under judge/prompt perturbations,
   - log2 sample budget.
4. Train a tiny calibration model, currently logistic regression, to route between selectors.
5. Evaluate against both individual selectors and an oracle selector-switch upper bound.

This is not a replacement for PRMs or hidden-state rankers. It is the layer that decides whether those rankers deserve trust on this instance.

## What Changed From v1

The first version overemphasized "stability." The ablations corrected that.

In the synthetic lab, perturbation rank-stability did **not** carry much additional signal. The useful signal came mainly from candidate-set structure: answer support, entropy, whether the verifier top agrees with the majority answer, and score-margin interactions.

That is good news and bad news:

- Good: the core method is simpler than a perturbation-heavy stability story.
- Bad: the original "Consensus-Stability Switching" name was too narrow.
- Better framing: **Candidate-Set Selector Switching**, with stability as one optional feature family.

The revised claim is not "stability solves verifier traps." The stronger, more defensible claim is:

> Selector failures leave detectable footprints in the candidate set, and a calibrated router can exploit those footprints better than any fixed selector.

## Synthetic Results

The simulator creates candidate sets with:

- correctness bits,
- answer clusters,
- a latent spurious style feature,
- a verifier score that combines true correctness signal with spurious style signal,
- trap instances where wrong candidates are especially attractive to the verifier.

At 25% trap instances and N=128:

| Method | Accuracy |
|---|---:|
| First sample | 0.614 |
| Best-of-N verifier | 0.822 |
| Answer majority | 0.941 |
| Fixed stability gate | 0.939 |
| CSS calibrated switch | 0.962 |
| Oracle switch | 0.986 |
| Any correct candidate | 1.000 |

At 0% trap instances and N=128:

| Method | Accuracy |
|---|---:|
| Best-of-N verifier | 0.998 |
| Answer majority | 0.938 |
| CSS calibrated switch | 0.998 |

The important behavior is asymmetric: CSS backs off when verifier traps are common, but preserves Best-of-N when the verifier is clean.

Full initial results: [stability_gated_tts_results.csv](stability_gated_tts_results.csv)  
Simulator: [stability_gated_tts_sim.py](stability_gated_tts_sim.py)
Formal metrics: [css_formalism_and_metrics.md](css_formalism_and_metrics.md)

## Ablation Results

Full ablation table: [css_ablation_lab.md](css_ablation_lab.md)  
CSV: [css_ablation_lab.csv](css_ablation_lab.csv)  
Script: [css_ablation_lab.py](css_ablation_lab.py)

### Feature Ablation

At 25% trap instances, N=32:

| Feature set | Best-of-N | Self-consistency | CSS | Oracle switch |
|---|---:|---:|---:|---:|
| all features | 0.836 | 0.924 | 0.947 | 0.977 |
| no stability | 0.836 | 0.924 | 0.947 | 0.977 |
| consensus only | 0.836 | 0.924 | 0.943 | 0.977 |
| score only | 0.836 | 0.924 | 0.924 | 0.977 |
| stability only | 0.836 | 0.924 | 0.924 | 0.977 |

Interpretation: in this simulator, the router is mostly learning from consensus/support structure, not perturbation stability. This is a useful negative result because it prevents the pitch from leaning on a fragile gimmick.

### Calibration Size

At 25% trap instances, N=32:

| Train examples | CSS | Self-consistency | Best-of-N |
|---:|---:|---:|---:|
| 50 | 0.916 | 0.928 | 0.830 |
| 100 | 0.945 | 0.928 | 0.830 |
| 500 | 0.948 | 0.928 | 0.830 |
| 4000 | 0.948 | 0.929 | 0.829 |

Interpretation: the toy setup suggests that the router does not need massive labels. It needs enough examples of BoN-vs-consensus disagreement.

### Disagreement-Mined Calibration

Uniform labels are wasteful because most prompts do not teach routing. I added an unlabeled mining score that prioritizes:

- verifier top answer differs from majority answer,
- low support for the verifier top answer,
- high answer entropy,
- high verifier confidence/margin.

At 25% trap instances, N=32:

| Calibration | Train examples | CSS | Self-consistency | Best-of-N |
|---|---:|---:|---:|---:|
| uniform | 50 | 0.926 | 0.925 | 0.834 |
| disagreement-mined | 50 | 0.935 | 0.925 | 0.834 |
| uniform | 100 | 0.925 | 0.925 | 0.834 |
| disagreement-mined | 100 | 0.943 | 0.925 | 0.834 |
| uniform | 2000 | 0.943 | 0.925 | 0.834 |
| disagreement-mined | 2000 | 0.948 | 0.925 | 0.834 |

Interpretation: this is a much sharper pitch. CSS should not ask for random labels; it should mine selector-disagreement regions and label those.

### Distribution Shift

Training only on clean verifier cases does not teach trap avoidance:

| Train trap | Test trap | Best-of-N | Self-consistency | CSS |
|---:|---:|---:|---:|---:|
| 0.00 | 0.25 | 0.829 | 0.926 | 0.833 |
| 0.10 | 0.25 | 0.829 | 0.926 | 0.939 |
| 0.25 | 0.25 | 0.829 | 0.926 | 0.946 |
| 0.40 | 0.25 | 0.829 | 0.926 | 0.934 |

Interpretation: calibration must include verifier failure modes. The next real-data version should mine calibration examples where selectors disagree, rather than sampling prompts uniformly.

### N Transfer

Training at N=32 transfers better to larger N than training only at N=8:

| Train N | Test N | Best-of-N | Self-consistency | CSS |
|---:|---:|---:|---:|---:|
| 8 | 128 | 0.818 | 0.943 | 0.937 |
| 32 | 128 | 0.818 | 0.943 | 0.964 |
| 128 | 128 | 0.818 | 0.943 | 0.964 |

Interpretation: high-N selector failure has its own shape. Calibrating only on low-N rollouts can underprepare the router.

## Real-Data Harness

I built a dependency-free Ollama harness for a real GSM8K probe:

[css_gsm8k_ollama.py](css_gsm8k_ollama.py)

Mac-side launcher for the Windows PC:

[launch_pc_gsm8k_probe.sh](launch_pc_gsm8k_probe.sh)

It does the following:

1. Downloads GSM8K test JSONL.
2. Uses `llama3.2:1b` to generate N candidate solutions.
3. Uses `qwen3.5:9b` as a verifier/judge under multiple judge prompts.
4. Extracts numeric answers.
5. Evaluates first sample, Best-of-N, self-consistency, margin gate, CSS, oracle switch, and any-correct coverage.
6. Writes resumable JSONL plus per-problem CSV and Markdown summaries.

The Windows GPU machine was reachable and reported:

- GPU: RTX 4070, 12GB VRAM.
- Ollama models: `llama3.2:1b`, `qwen3.5:9b`, `gemma4:26b`.
- `qwen3.5:9b` was already loaded on GPU.

Then SSH dropped and the host became unreachable. I sent a Wake-on-LAN magic packet to `FC:E7:B8:79:44:33`, but the machine did not come back during this pass. The harness is ready to run as soon as the PC is reachable.

Recommended first run on the PC:

```powershell
python css_gsm8k_ollama.py --limit 40 --n 8 --generator llama3.2:1b --judge qwen3.5:9b --out-jsonl css_gsm8k_records.jsonl --summary-md css_gsm8k_summary.md --summary-csv css_gsm8k_per_problem.csv
```

Expected runtime depends on qwen throughput, but the JSONL is resumable.

## Stronger Experimental Plan

The next serious version should be framed as four experiments:

### Experiment 1: Selector-Disagreement Mining

Instead of calibrating on random prompts, generate a large cheap pool and keep prompts where selectors disagree:

- verifier top answer differs from answer majority,
- verifier score margin is high but top-answer support is low,
- answer entropy is high,
- any-correct coverage is high but selectors fail.

Hypothesis: disagreement-mined calibration produces better routers than uniform calibration at the same label budget.

### Experiment 2: Black-Box Router vs Hidden-State Router

Compare:

- CSS black-box candidate-set features,
- SCATR-style hidden-state/logit features if available,
- combined black-box plus hidden-state features.

Hypothesis: black-box features recover much of the selector-routing benefit, while hidden-state features help when answer clustering is weak.

### Experiment 3: N-Generalization

Train routers at N=8, N=32, and mixed N. Test at N=8/16/32/64/128.

Hypothesis: routers trained only at low N under-detect high-N verifier over-optimization.

### Experiment 4: Perturbation Validity

Test whether judge perturbations actually add signal:

- judge prompt paraphrases,
- rationale-visible vs answer-only scoring,
- adversarial judge prompt,
- different judge model,
- stochastic judge temperature.

Hypothesis: perturbation stability helps only when perturbations decorrelate spurious verifier preferences. If all perturbations share the same blind spot, stability is fake confidence.

## Why This Could Become Real Research

The most promising contribution is not the logistic regression. It is the framing:

> Test-time scaling should report and optimize selector reliability separately from candidate coverage and selector quality.

That framing naturally produces useful diagnostics:

- coverage/selectability gap,
- selector disagreement rate,
- oracle-switch headroom,
- calibration label efficiency,
- N-transfer failure,
- trap-conditioned performance,
- candidate-set entropy regimes.

Even if CSS does not beat a strong PRM, these diagnostics could become a useful evaluation layer for any test-time scaling system.

## Reviewer Attacks And Current Answers

**"This is just self-consistency with extra steps."**  
Partly true in the toy. The ablation shows consensus features dominate. The real claim must be tested on cases where BoN sometimes beats self-consistency and sometimes fails. CSS only matters when selector choice is instance-dependent.

**"Your stability feature did nothing."**  
Correct in the current simulator. Stability should be treated as optional until real judge perturbations prove otherwise.

**"Distribution shift kills the router."**  
Clean-only calibration fails on trap-heavy tests. That is exactly why disagreement-mined calibration is part of the method, not a footnote.

**"A real PRM would solve this."**  
Maybe, but ROC-n-reroll suggests verifier imperfection still matters. CSS can route over a PRM too; it is not tied to weak judges.

**"You need real GSM8K/MATH500 numbers."**  
Yes. The Ollama harness exists, and the first real probe is the highest-priority next run once the GPU host is reachable.

## Go / No-Go Criteria

This deserves more work if the GSM8K probe shows at least one of:

- CSS beats both Best-of-N and self-consistency on held-out prompts.
- CSS closes at least 25% of the oracle-switch headroom.
- Disagreement-mined calibration beats uniform calibration.
- N=32 or mixed-N calibration transfers better to N=64/128 than N=8 calibration.

It should be killed or reframed if:

- self-consistency dominates all realistic verifier selectors,
- CSS never beats a fixed margin/support heuristic,
- oracle-switch headroom is tiny,
- router performance collapses under modest distribution shift.

## References

- Brown et al., 2024. [Large Language Monkeys: Scaling Inference Compute with Repeated Sampling](https://arxiv.org/abs/2407.21787).
- Snell et al., 2024. [Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314).
- Lightman et al., 2023. [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050).
- Huang et al., 2023/2024. [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798).
- Dorner et al., 2025. [ROC-n-reroll: How verifier imperfection affects test-time scaling](https://arxiv.org/abs/2507.12399).
- Shyamal et al., 2026. [SCATR: Simple Calibrated Test-Time Ranking](https://arxiv.org/abs/2604.16535).

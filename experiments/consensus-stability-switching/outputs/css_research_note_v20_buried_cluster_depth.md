# v20 Buried-Cluster Depth Audit

## Question

The earlier top-k result showed that top-3 cluster verification is too weak on high-N MATH. The open question is sharper:

> If a stronger semantic verifier is allowed to inspect more than the obvious top few clusters, how deep does it need to look before the cluster selectability gap becomes reachable?

This matters because the method pitch changes depending on the answer. If most correct clusters are top-3, a simple local reranker is enough. If they are top-20 or deeper, the method needs adaptive cluster-depth budgeting and/or evidence that changes the cluster ranking before verification.

## Setup

Script: `work/deep_topk_cluster_audit.py`.

I reran high-N parser-v2 MATH audits with `N=128`, 12 trials per held-out problem, and top-k windows:

```text
k = 1, 2, 3, 5, 10, 20, 50
```

The oracle is intentionally optimistic: it assumes a perfect verifier inside the inspected top-k clusters ranked by current `cluster_sum` evidence. This isolates the visibility/depth problem from detector quality and semantic verifier errors.

## Result

| dataset | cluster_sum | full oracle | avg clusters | miss rank p50 | miss rank p90 | top-5 oracle | top-10 oracle | top-20 oracle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MATH/Llama N=128 | 0.448 | 0.852 | 30.6 | 6 | 21 | 0.648 | 0.748 | 0.809 |
| MATH/Gemma N=128 | 0.233 | 0.725 | 55.5 | 8 | 33 | 0.411 | 0.536 | 0.635 |

Detailed reports:

- `outputs/deep_topk_math_llama_n128.md`
- `outputs/deep_topk_math_gemma2b_n128.md`

## Interpretation

Top-3 was too pessimistic as a final method target but correct as a warning. The correct cluster is often not one of the obvious alternatives.

For MATH/Llama, the median missed correct cluster is rank 6 and p90 is rank 21. A top-10 perfect verifier would reach `0.748`, closing about 74% of the selector headroom; top-20 would reach `0.809`.

For MATH/Gemma, the cluster field is much noisier. The median missed correct cluster is rank 8 and p90 is rank 33. Top-10 only reaches `0.536`; top-20 reaches `0.635`, still well below the full oracle `0.725`.

The method should therefore not be framed as "rerank the top few clusters." The tested pitch is:

> Repeated sampling should expose answer clusters, estimate when default evidence is unreliable, then allocate a variable semantic-verification budget over a bounded but nontrivial cluster frontier.

That frontier is not tiny. On high-N MATH, plausible budgets are closer to top-10 or top-20 clusters than top-3.

## Reviewer-Resistant Takeaway

The cluster selectability gap is not merely a failure to choose between the first and second cluster. It is often a depth problem. Current evidence ranks correct clusters at median rank 6-8 on selector misses, with p90 ranks 21-33. This creates a concrete target for future methods:

1. reduce failure-detector error,
2. improve cluster evidence so correct clusters move upward,
3. use adaptive top-k semantic verification when the detector predicts default selector failure,
4. report the bounded-verifier frontier instead of only any-correct coverage.

This is stronger than the original CSS idea because it produces a falsifiable method target: improve the deployed accuracy frontier at fixed invocation and fixed inspected-cluster budgets.

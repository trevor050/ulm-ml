"""Binary portfolio map for ULM ML research threads.

The user-facing rule is intentionally harsh: a project is either a full research
track with a concrete evidence plan, or it is given up as an active project.
This module gives tests and future agents one compact source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ResearchStatus = Literal["full_research", "given_up"]


@dataclass(frozen=True)
class ResearchProject:
    """One research thread and its current binary verdict."""

    slug: str
    title: str
    status: ResearchStatus
    verdict: str
    primary_doc: str
    representative_command: str | None


PROJECTS: tuple[ResearchProject, ...] = (
    ResearchProject(
        slug="cyclic-representation-probes",
        title="Cyclic Representation Probes",
        status="full_research",
        verdict=(
            "Merged modular spectral diagnostics, modular character baselines, and "
            "phase-state tracking into one research track on cyclic representations."
        ),
        primary_doc="experiments/cyclic-representation-probes/README.md",
        representative_command=(
            "python "
            "experiments/cyclic-representation-probes/modular_spectral_probe.py "
            "--modulus 31 "
            "--fractions 0.05 0.10 0.20 --seeds 0 1 2 3"
        ),
    ),
    ResearchProject(
        slug="symmetry-sparse-recovery",
        title="Symmetry-Augmented Sparse Recovery",
        status="full_research",
        verdict=(
            "Strict one-to-one recovery improves under the correct cyclic action and "
            "fails under a size-matched shuffled-action control."
        ),
        primary_doc="experiments/symmetry-sparse-recovery/README.md",
        representative_command=(
            "python "
            "experiments/symmetry-sparse-recovery/symmetry_augmented_sparse_recovery.py"
        ),
    ),
    ResearchProject(
        slug="sequence-memory-interference",
        title="Sequence-Memory Interference",
        status="full_research",
        verdict=(
            "Compact fast-weight memories are now framed as an interference benchmark "
            "with load curves against nearest-neighbor retrieval."
        ),
        primary_doc="experiments/sequence-memory-interference/README.md",
        representative_command=(
            "python experiments/sequence-memory-interference/associative_recall_fast_weights.py "
            "--epochs 8 --key-dims 16 32 64 --train-size 2048 --test-size 1024"
        ),
    ),
    ResearchProject(
        slug="doubt-tts",
        title="Doubt-TTS / Reliability-Action Routing",
        status="full_research",
        verdict=(
            "Generic doubt prompting failed the neutral-control bar, but the "
            "reliability-action framing has runnable route, source-selection, and "
            "verifier probes with explicit negative controls."
        ),
        primary_doc="experiments/doubt-tts/README.md",
        representative_command=(
            "python experiments/doubt-tts/scripts/doubt_probe.py "
            "--data experiments/doubt-tts/benchmarks/event_contrast_route_questions.jsonl "
            "--route-only --event-verifier-only "
            "--out /tmp/doubt_tts_table_event_results.jsonl "
            "--report /tmp/doubt_tts_table_event_report.md"
        ),
    ),
    ResearchProject(
        slug="adaptive-self-consistency",
        title="Adaptive Posterior Self-Consistency",
        status="given_up",
        verdict=(
            "Given up as active research until cached real-model answer traces exist; "
            "current synthetic simulator remains only replay infrastructure."
        ),
        primary_doc="experiments/adaptive-self-consistency/README.md",
        representative_command=None,
    ),
    ResearchProject(
        slug="egpr-prototype-replay",
        title="EGPR Prototype Replay",
        status="given_up",
        verdict=(
            "Given up as an adaptation method because true no-adapt baselines beat or "
            "match online prototype updates on the digits shifts."
        ),
        primary_doc="experiments/egpr-prototype-replay/README.md",
        representative_command=None,
    ),
    ResearchProject(
        slug="pace-bias-tta",
        title="PACE Bias-Only TTA",
        status="given_up",
        verdict=(
            "Given up as a standalone project; it survives only as a narrow "
            "label-prior-drift diagnostic baseline."
        ),
        primary_doc="experiments/pace-bias-tta/README.md",
        representative_command=None,
    ),
)


def projects_by_status(status: ResearchStatus) -> tuple[ResearchProject, ...]:
    """Return projects with a given binary status."""

    return tuple(project for project in PROJECTS if project.status == status)


def project_slugs() -> set[str]:
    """Return all registered portfolio slugs."""

    return {project.slug for project in PROJECTS}

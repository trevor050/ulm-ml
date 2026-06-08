import shlex
from pathlib import Path

from ulm_ml.paths import PROJECT_ROOT
from ulm_ml.research_portfolio import PROJECTS, project_slugs, projects_by_status


def test_every_research_project_has_binary_verdict_and_doc() -> None:
    assert projects_by_status("full_research")
    assert projects_by_status("given_up")

    for project in PROJECTS:
        assert project.status in {"full_research", "given_up"}
        assert project.verdict
        assert (PROJECT_ROOT / project.primary_doc).is_file()


def test_portfolio_covers_all_known_project_slugs() -> None:
    expected = {
        "cyclic-representation-probes",
        "symmetry-sparse-recovery",
        "sequence-memory-interference",
        "doubt-tts",
        "consensus-stability-switching",
        "adaptive-self-consistency",
        "egpr-prototype-replay",
        "pace-bias-tta",
    }

    assert project_slugs() == expected


def test_representative_commands_only_required_for_full_research() -> None:
    for project in PROJECTS:
        if project.status == "full_research":
            assert project.representative_command
            command_parts = shlex.split(project.representative_command)
            script_path = PROJECT_ROOT / command_parts[1]
            assert script_path.is_file()
        else:
            assert project.representative_command is None


def test_portfolio_docs_are_linked_from_top_level_index() -> None:
    index = Path(PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for project in PROJECTS:
        assert str(Path(project.primary_doc).parent) in index

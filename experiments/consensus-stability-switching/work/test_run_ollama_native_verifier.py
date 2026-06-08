#!/usr/bin/env python3
"""Smoke tests for Ollama-native verifier runner helpers."""

from __future__ import annotations

import importlib.util
import json
import http.client
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "run_ollama_native_verifier",
        ROOT / "work" / "run_ollama_native_verifier.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows))


def test_parse_answer_and_message_content():
    mod = load_module()
    response = {"message": {"content": '{"answer":"42","confidence":0.75,"reason":"visible"}'}}

    content = mod.message_content(response)
    answer, confidence, reason = mod.parse_answer(content)

    assert answer == "42"
    assert confidence == 0.75
    assert reason == "visible"


def test_parse_answer_salvages_truncated_json_prefix():
    mod = load_module()
    answer, confidence, reason = mod.parse_answer('{"answer":"-2","confidence":0.9,"reason":"long')

    assert answer == "-2"
    assert confidence == 0.9
    assert reason.startswith('{"answer"')


def test_schema_for_answer_only_mode():
    mod = load_module()

    schema = mod.schema_for_mode("answer_only")

    assert schema["required"] == ["answer", "confidence"]
    assert "reason" not in schema["properties"]


def test_iter_pending_prompt_rows_skips_done_and_respects_limit():
    mod = load_module()
    with TemporaryDirectory() as tmp:
        prompts = Path(tmp) / "prompts.jsonl"
        write_jsonl(
            prompts,
            [
                {"packet_id": "a", "messages": []},
                {"packet_id": "b", "messages": []},
                {"packet_id": "c", "messages": []},
            ],
        )

        rows = list(mod.iter_pending_prompt_rows(prompts, done={"a"}, limit=1))

        assert len(rows) == 1
        assert rows[0][0] == 2
        assert rows[0][1]["packet_id"] == "b"


def test_remote_disconnect_is_retryable():
    mod = load_module()

    assert http.client.RemoteDisconnected in mod.RETRYABLE_EXCEPTIONS


def main():
    test_parse_answer_and_message_content()
    test_parse_answer_salvages_truncated_json_prefix()
    test_schema_for_answer_only_mode()
    test_iter_pending_prompt_rows_skips_done_and_respects_limit()
    test_remote_disconnect_is_retryable()
    print("ok")


if __name__ == "__main__":
    main()

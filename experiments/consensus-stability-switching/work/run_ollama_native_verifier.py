#!/usr/bin/env python3
"""Run cluster-verifier prompts through Ollama's native chat API.

This is useful for models whose OpenAI-compatible endpoint emits reasoning
fields but leaves assistant content empty. Ollama native `/api/chat` with
`format: "json"` returns parseable message content for those models.
"""

from __future__ import annotations

import argparse
import http.client
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": ["string", "number", "null"]},
        "confidence": {"type": ["number", "null"]},
        "reason": {"type": "string"},
    },
    "required": ["answer", "confidence", "reason"],
}

ANSWER_ONLY_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": ["string", "number", "null"]},
        "confidence": {"type": ["number", "null"]},
    },
    "required": ["answer", "confidence"],
}

RETRYABLE_EXCEPTIONS = (
    urllib.error.URLError,
    http.client.RemoteDisconnected,
    TimeoutError,
    KeyError,
    json.JSONDecodeError,
)


def schema_for_mode(mode: str) -> dict:
    if mode == "answer_only":
        return ANSWER_ONLY_SCHEMA
    return ANSWER_SCHEMA


def chat_completion(base_url: str, model: str, messages: list[dict], temperature: float, timeout: int, num_predict: int | None, think: bool, use_schema: bool, schema_mode: str) -> dict:
    url = base_url.rstrip("/") + "/api/chat"
    options = {"temperature": temperature}
    if num_predict is not None:
        options["num_predict"] = num_predict
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": schema_for_mode(schema_mode) if use_schema else "json",
        "think": think,
        "options": options,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def message_content(response: dict) -> str:
    message = response.get("message") or {}
    return str(message.get("content") or "")


def parse_answer(text: str) -> tuple[str | None, float | None, str]:
    try:
        data = json.loads(text)
        return data.get("answer"), data.get("confidence"), data.get("reason", "")
    except json.JSONDecodeError:
        answer = None
        confidence = None
        answer_match = re.search(r'"answer"\s*:\s*("(?P<quoted>(?:\\.|[^"\\])*)"|(?P<bare>-?\d+(?:\.\d+)?|null))', text)
        if answer_match:
            if answer_match.group("quoted") is not None:
                answer = json.loads(answer_match.group(1))
            elif answer_match.group("bare") != "null":
                answer = answer_match.group("bare")
        confidence_match = re.search(r'"confidence"\s*:\s*(?P<confidence>-?\d+(?:\.\d+)?)', text)
        if confidence_match:
            confidence = float(confidence_match.group("confidence"))
        return answer, confidence, text[:500]


def existing_packet_ids(path: Path) -> set[str]:
    ids = set()
    if not path.exists():
        return ids
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                ids.add(json.loads(line)["packet_id"])
            except Exception:
                pass
    return ids


def iter_pending_prompt_rows(prompts: Path, done: set[str], limit: int | None = None):
    yielded = 0
    with prompts.open() as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            packet_id = row["packet_id"]
            if packet_id in done:
                continue
            if limit is not None and yielded >= limit:
                break
            yielded += 1
            yield line_no, row


def run(args: argparse.Namespace) -> None:
    done = existing_packet_ids(args.output) if args.resume else set()
    count = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume else "w"
    limit = args.limit if args.limit and args.limit > 0 else None
    with args.output.open(mode) as out:
        for line_no, row in iter_pending_prompt_rows(args.prompts, done, limit):
            packet_id = row["packet_id"]
            last_error = None
            for attempt in range(args.retries + 1):
                try:
                    response = chat_completion(args.base_url, args.model, row["messages"], args.temperature, args.timeout, args.num_predict, args.think, not args.no_schema, args.schema_mode)
                    content = message_content(response)
                    answer, confidence, reason = parse_answer(content)
                    pred = {
                        "packet_id": packet_id,
                        "answer": answer,
                        "confidence": confidence,
                        "reason": reason,
                        "raw_content": content,
                        "model": args.model,
                    }
                    if args.include_timing:
                        pred["total_duration"] = response.get("total_duration")
                        pred["load_duration"] = response.get("load_duration")
                        pred["eval_count"] = response.get("eval_count")
                        pred["eval_duration"] = response.get("eval_duration")
                    out.write(json.dumps(pred) + "\n")
                    out.flush()
                    count += 1
                    if count == 1 or count % args.log_every == 0:
                        print(f"wrote {count} predictions, latest {packet_id}", flush=True)
                    break
                except RETRYABLE_EXCEPTIONS as exc:
                    last_error = exc
                    if attempt < args.retries:
                        time.sleep(args.retry_sleep * (attempt + 1))
            else:
                raise RuntimeError(f"failed on line {line_no} packet {packet_id}: {last_error}") from last_error
    print(f"done wrote={count} output={args.output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument("--think", action="store_true", help="enable Ollama thinking mode; default disables thinking for parseable JSON content")
    parser.add_argument("--no-schema", action="store_true", help="use format=json instead of the answer JSON schema")
    parser.add_argument("--schema-mode", choices=["answer_reason", "answer_only"], default="answer_reason")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=2.0)
    parser.add_argument("--log-every", type=int, default=10)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--include-timing", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="maximum pending prompts to run; 0 means all")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Dependency-free validator for the Doubt-TTS benchmark JSON Schema subset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "outputs" / "doubt_tts_benchmark_schema_v1.json"
DEFAULT_INPUT = ROOT / "work" / "probe" / "preregistered_benchmark_candidate_locked.jsonl"


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def validate_value(value: Any, schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type and not type_matches(value, expected_type):
        return [f"{path}: expected {expected_type}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: `{value}` not in enum {schema['enum']}")

    if expected_type == "object":
        if not isinstance(value, dict):
            return errors
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key `{key}`")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            for key in extra:
                errors.append(f"{path}: additional property `{key}`")
        for key, child in properties.items():
            if key in value:
                errors.extend(validate_value(value[key], child, f"{path}.{key}"))

    if expected_type == "array":
        if not isinstance(value, list):
            return errors
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_value(item, item_schema, f"{path}[{index}]"))
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(value)}")

    min_length = schema.get("minLength")
    if min_length is not None and isinstance(value, str) and len(value) < min_length:
        errors.append(f"{path}: expected length >= {min_length}, got {len(value)}")

    return errors


def read_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    with path.open() as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                rows.append((lineno, json.loads(line)))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    schema_path = args.schema if args.schema.is_absolute() else ROOT / args.schema
    input_path = args.input if args.input.is_absolute() else ROOT / args.input

    schema = json.loads(schema_path.read_text())
    errors: list[str] = []
    for lineno, row in read_jsonl(input_path):
        for error in validate_value(row, schema, "$"):
            errors.append(f"{input_path.relative_to(ROOT)}:{lineno}: {error}")

    if errors:
        for error in errors[:200]:
            print(error)
        if len(errors) > 200:
            print(f"... {len(errors) - 200} more")
        raise SystemExit(1)
    print(f"validated {input_path.relative_to(ROOT)} against {schema_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

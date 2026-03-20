#!/usr/bin/env python3
"""
Validate LLM JSON output against a research schema.

Usage:
    python validate_output.py '{"company_name": "Acme", ...}'
    python validate_output.py response.json
    echo '{"company_name": "Acme", ...}' | python validate_output.py -
"""

import json
import sys
from pathlib import Path

# --- Schema definition ---
# Matches the example prompt in references/example-schema-validation.md
# Replace with your own schema per project.

SCHEMA = {
    "required": ["company_name", "website", "headquarters",
                 "employee_count", "year_founded", "summary"],
    "fields": {
        "company_name":   {"type": str,  "nullable": False},
        "website":        {"type": str,  "nullable": True},
        "headquarters":   {"type": str,  "nullable": True},
        "employee_count": {"type": int,  "nullable": True,  "min": 0},
        "year_founded":   {"type": int,  "nullable": True,  "min": 1800},
        "summary":        {"type": str,  "nullable": False, "min_length": 20},
    }
}


def validate(data: dict) -> list[dict]:
    """
    Validate a dict against SCHEMA. Returns a list of error dicts.
    Each error has: field, rule, message, value.
    """
    errors = []

    # Check for extra keys (key name drift protection)
    extra_keys = set(data.keys()) - set(SCHEMA["fields"].keys())
    for key in sorted(extra_keys):
        errors.append({
            "field": key,
            "rule": "additionalProperties",
            "message": f"Unexpected key '{key}': not in schema",
            "value": data[key],
        })

    # Check required fields and types
    for field_name, rules in SCHEMA["fields"].items():
        if field_name not in data:
            errors.append({
                "field": field_name,
                "rule": "required",
                "message": f"Missing required field '{field_name}'",
                "value": None,
            })
            continue

        value = data[field_name]

        # Null check
        if value is None:
            if not rules.get("nullable", False):
                errors.append({
                    "field": field_name,
                    "rule": "nullable",
                    "message": f"'{field_name}' cannot be null",
                    "value": value,
                })
            continue

        # Type check
        if not isinstance(value, rules["type"]):
            errors.append({
                "field": field_name,
                "rule": "type",
                "message": f"'{field_name}' expected {rules['type'].__name__}, "
                           f"got {type(value).__name__}",
                "value": value,
            })
            continue

        # Min value (integers)
        if "min" in rules and isinstance(value, int) and value < rules["min"]:
            errors.append({
                "field": field_name,
                "rule": "minimum",
                "message": f"'{field_name}' must be >= {rules['min']}, got {value}",
                "value": value,
            })

        # Min length (strings)
        if "min_length" in rules and isinstance(value, str):
            if len(value) < rules["min_length"]:
                errors.append({
                    "field": field_name,
                    "rule": "minLength",
                    "message": f"'{field_name}' must be >= {rules['min_length']} chars, "
                               f"got {len(value)}",
                    "value": value,
                })

    return errors


def load_input() -> str:
    """Load JSON string from argument, file, or stdin."""
    if len(sys.argv) < 2:
        print("Usage: validate_output.py <json-string | file.json | ->")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "-":
        return sys.stdin.read()
    elif Path(arg).is_file():
        return Path(arg).read_text()
    else:
        return arg


def main():
    raw = load_input()

    # Step 1: Parse JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"FAIL: Invalid JSON: {e}")
        print(f"Raw output:\n{raw[:500]}")
        sys.exit(1)

    if not isinstance(data, dict):
        print(f"FAIL: Expected JSON object, got {type(data).__name__}")
        print(f"Raw output:\n{raw[:500]}")
        sys.exit(1)

    # Step 2: Validate
    errors = validate(data)

    if not errors:
        print("PASS: Output conforms to schema")
        print(json.dumps(data, indent=2))
        sys.exit(0)

    # Step 3: Report errors with full diagnostic context
    print(f"FAIL: {len(errors)} validation error(s)\n")
    for err in errors:
        print(f"  Field: {err['field']}")
        print(f"  Rule:  {err['rule']}")
        print(f"  Error: {err['message']}")
        print(f"  Value: {repr(err['value'])}")
        print()

    print("Raw output:")
    print(json.dumps(data, indent=2))
    sys.exit(1)


if __name__ == "__main__":
    main()

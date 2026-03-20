# Example: Schema Validation for LLM Output

## The prompt

This prompt demonstrates how to communicate the expected JSON contract to the
model. The key elements: explicit schema, `additionalProperties: false`, and
a concrete example.

```text
Research the following company and return your findings as a JSON object.

You MUST return valid JSON conforming exactly to this schema: no extra keys,
no renamed keys, no missing required fields. If you are uncertain about a
value, use null.

Schema:
{
  "type": "object",
  "required": ["company_name", "website", "headquarters", "employee_count", "year_founded", "summary"],
  "additionalProperties": false,
  "properties": {
    "company_name":   { "type": "string" },
    "website":        { "type": ["string", "null"], "format": "uri" },
    "headquarters":   { "type": ["string", "null"] },
    "employee_count": { "type": ["integer", "null"], "minimum": 0 },
    "year_founded":   { "type": ["integer", "null"], "minimum": 1800 },
    "summary":        { "type": "string", "minLength": 20 }
  }
}

Example valid response:
{
  "company_name": "Acme Corp",
  "website": "https://acme.example.com",
  "headquarters": "Austin, TX",
  "employee_count": 150,
  "year_founded": 2018,
  "summary": "Acme Corp provides supply chain automation for mid-market manufacturers."
}

Company to research: {{COMPANY_NAME}}
```

## The validation script

Save as `scripts/validate_output.py`. Validates LLM output against the schema
and produces actionable error reports instead of silent failures.

```python
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

# --- Schema definition (matches the prompt above) ---

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
```

## Usage examples

```bash
# Validate a JSON string directly
python scripts/validate_output.py '{"company_name":"Acme","website":"https://acme.com","headquarters":"Austin, TX","employee_count":150,"year_founded":2018,"summary":"Acme provides supply chain automation for manufacturers."}'

# Validate from a file
python scripts/validate_output.py output/row_001.json

# Pipe from another process
curl -s https://api.example.com/enrich | python scripts/validate_output.py -
```

## What the validation catches

| Input problem | Error reported |
|---|---|
| `companyName` instead of `company_name` | `Unexpected key 'companyName'` + `Missing required field 'company_name'` |
| `employee_count: "about 200"` | `expected int, got str` |
| `summary: "Short"` | `must be >= 20 chars, got 5` |
| `year_founded: 1200` | `must be >= 1800, got 1200` |
| Missing `website` field entirely | `Missing required field 'website'` |
| Non-nullable field set to `null` | `'company_name' cannot be null` |

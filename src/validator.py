from __future__ import annotations

from typing import Any


def validate(projected_record: dict[str, Any], config: dict) -> bool:
    fields = config.get("fields", [])
    on_missing = config.get("on_missing", "null")

    for spec in fields:
        out_key = spec["path"]
        expected_type = spec.get("type", "string")
        required = spec.get("required", False)

        val = projected_record.get(out_key)

        if val is None or val == [] or val == {}:
            if required:
                if on_missing == "error":
                    raise ValueError(f"Required field '{out_key}' is missing or null")
                elif on_missing == "omit" and out_key not in projected_record:
                    # if omit, it's fine if it's missing in dictionary, but if required, we still validate
                    raise ValueError(f"Required field '{out_key}' was omitted")
            continue

        _validate_type(out_key, val, expected_type)

    return True


def _validate_type(field_name: str, val: Any, expected_type: str) -> None:
    if expected_type == "string":
        if not isinstance(val, str):
            raise TypeError(f"Field '{field_name}' must be a string, got {type(val).__name__}")
    elif expected_type == "string[]":
        if not isinstance(val, list):
            raise TypeError(f"Field '{field_name}' must be a list of strings, got {type(val).__name__}")
        for idx, item in enumerate(val):
            if not isinstance(item, str) and item is not None:
                raise TypeError(f"Item at index {idx} in field '{field_name}' must be a string, got {type(item).__name__}")
    elif expected_type == "number":
        if not isinstance(val, (int, float)):
            raise TypeError(f"Field '{field_name}' must be a number, got {type(val).__name__}")
    elif expected_type == "object":
        if not isinstance(val, dict):
            raise TypeError(f"Field '{field_name}' must be an object, got {type(val).__name__}")
    elif expected_type == "object[]":
        if not isinstance(val, list):
            raise TypeError(f"Field '{field_name}' must be a list of objects, got {type(val).__name__}")
        for idx, item in enumerate(val):
            if not isinstance(item, dict) and item is not None:
                raise TypeError(f"Item at index {idx} in field '{field_name}' must be an object, got {type(item).__name__}")
    else:
        # fallback for unknown type
        pass

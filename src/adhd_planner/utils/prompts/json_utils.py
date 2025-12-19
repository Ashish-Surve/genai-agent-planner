"""Utilities for parsing JSON responses from LLMs."""

import json
import re
from typing import Any


def parse_json_response(response: str) -> dict[str, Any]:
    """
    Parse JSON from LLM response, handling markdown code blocks and common LLM quirks.

    Args:
        response: Raw response from LLM (may contain markdown code blocks)

    Returns:
        Parsed JSON dictionary

    Raises:
        json.JSONDecodeError: If response is not valid JSON after cleaning
    """
    # Remove markdown code blocks (```json ... ``` or ``` ... ```)
    cleaned = re.sub(r'```(?:json)?\s*\n?', '', response)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned)
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()

    # Try direct parsing first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Apply fixes to cleaned string
    cleaned = _fix_json_string(cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object using balanced brace matching
    json_str = _extract_json_object(cleaned)
    if json_str:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Apply fixes and try again
            json_str = _fix_json_string(json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

    # Last resort: try simple regex extraction
    json_match = re.search(r'\{[^{}]*\}', cleaned, re.DOTALL)
    if json_match:
        extracted = _fix_json_string(json_match.group())
        return json.loads(extracted)

    raise json.JSONDecodeError("Could not parse JSON from response", response, 0)


def _fix_json_string(s: str) -> str:
    """Apply common fixes to malformed JSON strings from LLMs."""
    # Remove trailing commas before closing braces/brackets
    s = re.sub(r',(\s*[}\]])', r'\1', s)

    # Remove comments (// style)
    s = re.sub(r'//[^\n]*', '', s)

    # Fix unquoted property names (simple cases)
    # Match word characters followed by colon that aren't already quoted
    s = re.sub(r'(?<=[{,])\s*(\w+)\s*:', r'"\1":', s)

    # Remove any text before first { or [
    match = re.search(r'[\[{]', s)
    if match:
        s = s[match.start():]

    # Remove any text after last } or ]
    for i in range(len(s) - 1, -1, -1):
        if s[i] in ']}':
            s = s[:i + 1]
            break

    return s


def _extract_json_object(s: str) -> str | None:
    """Extract a complete JSON object using balanced brace matching."""
    start = s.find('{')
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for i, char in enumerate(s[start:], start):
        if escape:
            escape = False
            continue

        if char == '\\':
            escape = True
            continue

        if char == '"' and not escape:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return s[start:i + 1]

    return None

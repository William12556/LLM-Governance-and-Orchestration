"""
Mistral tool call parser.

Parses tool calls from model response content field.
Handles two observed formats:

  1. Official Mistral JSON array:
       [TOOL_CALLS] [{"name": "func", "arguments": {"k": "v"}}]

  2. Plain-text variant (observed with Devstral via oMLX):
       [TOOL_CALLS]tool_name[ARGS]{"k": "v"}
"""

import json
import re
from typing import Any


def parse_tool_calls(content: str) -> list[dict[str, Any]]:
    """
    Extract tool calls from content string.
    Returns list of {"name": str, "arguments": dict}.
    Returns empty list if no tool calls found.
    """
    if "[TOOL_CALLS]" not in content:
        return []

    # Format 1: official Mistral JSON array
    json_match = re.search(r"\[TOOL_CALLS\]\s*(\[.*?\])", content, re.DOTALL)
    if json_match:
        try:
            calls = json.loads(json_match.group(1))
            return [
                {"name": c["name"], "arguments": c.get("arguments", {})}
                for c in calls
                if "name" in c
            ]
        except (json.JSONDecodeError, KeyError):
            pass

    # Format 2: plain-text variant
    # Use raw_decode to correctly extract nested JSON objects (handles multi-level
    # nesting that a non-greedy regex cannot).
    results = []
    seen: set[tuple] = set()
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\[TOOL_CALLS\](\w+)\[ARGS\]", content):
        name = match.group(1)
        start = match.end()
        # Skip leading whitespace
        while start < len(content) and content[start] in " \t\n":
            start += 1
        try:
            arguments, _ = decoder.raw_decode(content, start)
        except json.JSONDecodeError:
            arguments = {}
        # Deduplicate: skip identical (name, args) pairs emitted twice in one response
        key = (name, json.dumps(arguments, sort_keys=True))
        if key in seen:
            continue
        seen.add(key)
        results.append({"name": name, "arguments": arguments})

    return results

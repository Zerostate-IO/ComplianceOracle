---
name: fastmcp-runtime-tool-contract
description: |
  Use when validating MCP tool parity in FastMCP projects and commands referencing mcp._tools fail
  or docs/runtime tool names drift unexpectedly. Covers current FastMCP introspection method,
  leading-underscore registration behavior, and reliable README-vs-runtime verification.
---

# FastMCP Runtime Tool Contract

## Problem
Legacy verification commands that inspect `mcp._tools` fail, and documented tool names can drift from runtime names.

## Context / Trigger Conditions
- Command fails with `AttributeError: 'FastMCP' object has no attribute '_tools'`.
- Runtime exposes unexpected tool names like `_evaluate_compliance`.
- README tool table count differs from runtime tool count.

## Solution
- Use `asyncio.run(mcp.get_tools())` as the source of truth for runtime tools.
- Compare `set(asyncio.run(mcp.get_tools()).keys())` against parsed README tool names.
- In FastMCP, decorated function names are exposed literally; leading underscores in function names become leading underscores in tool names unless explicitly renamed.

## Verification
- `uv run python -c "import asyncio; from compliance_oracle.server import mcp; print(sorted(asyncio.run(mcp.get_tools()).keys()))"`
- Confirm README set difference is empty (`runtime - docs` and `docs - runtime`).

## Example
A server registers `_evaluate_compliance` via `@mcp.tool()` on a function named `_evaluate_compliance`; runtime exposes `_evaluate_compliance`, while docs may list `evaluate_compliance`, causing parity failure.

## Notes
Use exact runtime keys for audits and CI checks; do not rely on assumed normalization of tool names.

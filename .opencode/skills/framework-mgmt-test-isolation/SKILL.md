---
name: framework-mgmt-test-isolation
description: |
  Use when adding tests for compliance_oracle.tools.framework_mgmt helper functions that
  read/write data/frameworks files or when coverage shows "module-not-imported" for this tool.
  Triggers: coverage command uses src/... path and returns no data, or helper tests need safe
  filesystem isolation for download/remove/validate paths.
---

# Framework Mgmt Test Isolation

## Problem

Testing `framework_mgmt` helpers directly can write into repo `data/frameworks` unless path resolution is isolated, and coverage can report no data if the wrong target string is used.

## Context / Trigger Conditions

- Testing `_download_framework`, `_remove_framework`, `_validate_framework`.
- Coverage command emits:
  - `Module src/compliance_oracle/tools/framework_mgmt was never imported`
  - `No data was collected`
- Code computes path via `Path(__file__).parent.parent.parent.parent / "data" / "frameworks"`.

## Solution

1. Patch module `__file__` to a synthetic file under `tmp_path` so parent traversal lands in temp storage.
2. Build temp files under `tmp_path/data/frameworks` for remove/validate scenarios.
3. Mock `httpx.AsyncClient` with async context manager (`__aenter__`/`__aexit__`) for download success/error branches.
4. Use coverage target `--cov=compliance_oracle.tools.framework_mgmt` (import path, not filesystem path).

## Verification

- `uv run pytest tests/test_framework_mgmt.py -q` passes.
- `uv run pytest --cov=compliance_oracle.tools.framework_mgmt --cov-report=term-missing` reports expected coverage for this module.
- File writes and deletes happen only under pytest temp directories.

## Example

```python
module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
module_file.parent.mkdir(parents=True)
_ = module_file.write_text("# test")

with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
    result = await framework_mgmt._validate_framework("nist-csf-2.0", manager=manager)
```

## Notes

- Branch dispatch inside `manage_framework` is easiest to test through `register_framework_tools(mcp)` + `mcp.get_tool("manage_framework")` while patching helper globals.

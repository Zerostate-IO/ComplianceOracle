# Learnings - Project Documentation Gap Roadmap

## Task 1: Documentation Surface Inventory (2026-02-28)

### Key Patterns Discovered

1. **Documentation Layer Separation**
   - README.md serves as user-facing quick reference (281 lines)
   - PROJECT_DESIGN_DRAFT.md contains full architectural spec (1800+ lines)
   - AGENTS.md bridges the two for AI agent consumption
   - pyproject.toml provides package metadata

2. **Claim Traceability Approach**
   - Used grep to find all "Compliance Oracle" and "evaluate" references
   - Cross-referenced claims across all four documentation files
   - Identified gaps where claims appear in design docs but not user docs

### Critical Findings

1. **evaluate_compliance Tool Gap**
   - Specified in PROJECT_DESIGN_DRAFT.md (lines 127, 172, 187-276)
   - Mentioned in pyproject.toml description (line 4)
   - ABSENT from README.md tools table (lines 131-149)
   - This is a user-facing documentation gap

2. **Framework Scope Mismatch**
   - Design doc claims: CSF 2.0, 800-53, 800-171, SOC2, ISO 27001
   - README/pyproject.toml claim: CSF 2.0, 800-53 only
   - 800-171, SOC2, ISO 27001 are planned but documented as available

3. **Core Principle Undocumented**
   - Design doc line 14: "Identify what isn't compliant and why. Never suggest fixes."
   - This principle is not communicated to users in README.md

### Approach That Worked

- Running grep in parallel with file reads saved time
- Creating structured claim table with IDs enables traceability
- Cross-referencing "evaluate" term across all files quickly identified the gap
- Verification step (grep for "Compliance Oracle") confirmed all files captured

### Tools Used

- `grep -n "pattern" file1 file2 file3 file4` for multi-file search
- `read` for full file contents
- Line number references from task specification matched actual content


## Task 2: Runtime Tool Contract Baseline (2026-02-28)

### FastMCP Tool Introspection

- FastMCP.get_tools() is an async method that returns a dict (keys are tool names as strings)
- Cannot iterate synchronously; must use `asyncio.run()` wrapper
- Pattern: `tools = await mcp.get_tools()` returns dict with tool name keys

### Tool Registration Architecture

- Each module in `src/compliance_oracle/tools/` exports a `register_*_tools(mcp: FastMCP)` function
- Server imports and calls registration functions in sequence (server.py lines 8-12 imports, 21-25 calls)
- Tools are decorated with `@mcp.tool()` within each registration function
- Pattern ensures clean separation between tool definitions and server setup

### CLI Command Structure

- CLI uses Click with `@click.group()` pattern (main function at line 16)
- Commands decorated with `@main.command()` at function level
- All CLI commands have async implementations via `_command_name()` helper functions
- CLI and MCP tools share underlying FrameworkManager and ControlSearcher

### Extraction Verification

- Python extraction command confirmed working:
  ```python
  uv run python -c "
  import asyncio
  from compliance_oracle.server import mcp
  async def main():
      tools = await mcp.get_tools()
      for tool in tools: print(f'  {tool}')
      print(f'Total: {len(tools)} tools')
  asyncio.run(main())
  "
  ```

### Key Findings

1. **MCP Tools Count: 13** - All verified via runtime extraction
2. **CLI Commands Count: 7** - fetch, validate, status, index, search, show, clear
3. **No `evaluate_compliance` tool exists** - Confirms Task 1 finding that this is a design-only feature
4. **Tool names follow snake_case convention** - Consistent across all modules



## Task 3: Gap Register with Risk Disposition (2026-02-28)

### Gap Classification Framework

Established four risk classes:
1. **TRUST** - Claimed capability does not exist (highest severity)
2. **OPERABILITY** - Feature exists but hidden/unusable
3. **SEMANTIC_DRIFT** - Meaning diverges between docs and reality
4. **CORRECTNESS** - Factual error (counts, names, values)

### Disposition Framework

Four dispositions with clear action criteria:
1. **FIX NOW** - Immediate correction required
2. **SCHEDULE** - Plan for next release cycle
3. **ACCEPT** - Explicit decision to leave as-is (with trigger)
4. **DEFER_WITH_TRIGGER** - Postpone with documented condition

### Critical Finding Pattern

The "evaluating designs and code" claim appears in TWO places:
- `pyproject.toml:4` - Package description (user-facing)
- `server.py:17` - MCP server instructions (agent-facing)

Both claim a capability that has NO implementation. This is a **dual-source trust violation**.

### Gap Prioritization Approach

1. Group gaps by root cause (GAP-001 and GAP-007 are same issue, different locations)
2. Identify which gaps can be fixed with single edit vs multiple edits
3. TRUST gaps always get FIX NOW unless explicitly accepted with trigger
4. OPERABILITY gaps that hide working features get FIX NOW

### Tool Count Verification

- README table: 12 tools (grep -c "| \`" README.md)
- Runtime: 13 tools (FastMCP.get_tools() extraction)
- Missing: `get_assessment_questions` (exists in tools/assessment.py:23)
- Note: Tool IS mentioned in README roadmap section but NOT in tools table

### Source Anchor Pattern

Each gap should include:
1. Line numbers for claims in documentation
2. Line numbers for implementation (or "not found")
3. Grep command for verification
4. Expected vs observed output

This enables automated regression testing of gap fixes.


## Task 5: README Tools Reconciliation (2026-02-28)

### Problem Solved

GAP-002 identified that `get_assessment_questions` tool was missing from README MCP tools table despite existing in runtime.

### Fix Applied

- Added single row to README.md tools table (line 149)
- Tool: `get_assessment_questions()` 
- Purpose: "Generate interview-style questions"
- Example: `get_assessment_questions(framework="nist-csf-2.0", function="PR")`

### Verification Method

1. Read runtime baseline from Task 2 evidence (13 tools)
2. Count README table rows (was 12, now 13)
3. Confirm set difference empty (all runtime tools now documented)

### Key Insight

The tool WAS mentioned in README roadmap section (0.1.x milestone) but was missing from the primary tools table. This created an OPERABILITY gap - the feature works but users couldn't discover it from the reference table.

### Pattern: Table-Driven Documentation

For tool catalogs, a markdown table is the single source of truth for users. If a tool exists at runtime but isn't in the table, it's effectively invisible. Runtime extraction should be the verification baseline.



## Task 4: Purpose Alignment (2026-02-28)

### Documentation Truth Pattern

Not all files needed changes:
- README.md and AGENTS.md already had accurate purpose statements
- Only pyproject.toml and server.py had false claims

Lesson: Gap analysis revealed that the problem was isolated to two specific locations, not a systemic issue across all docs.

### Accurate Capability Description

The accurate description captures five capability areas:
1. Framework lookup (list_frameworks, list_controls, get_control_details, get_control_context)
2. Semantic search (search_controls)
3. Documentation tracking (document_compliance, link_evidence, get_documentation, export_documentation)
4. Cross-framework mappings (compare_frameworks, get_guidance, get_framework_gap)
5. Assessment templates (get_assessment_questions)

### Canonical Purpose String

Changed from: "MCP server for evaluating designs and code against compliance frameworks"
Changed to: "MCP server for compliance framework lookup, search, documentation, and gap analysis"

This pattern (verb list + scope) is more honest and specific than the aspirational claim.

### Verification Strategy

Single grep command verified all four files:
```bash
grep -n "evaluating designs and code" README.md AGENTS.md src/compliance_oracle/server.py pyproject.toml
```

Zero output = zero false claims = verified fix.

### Future Features in Roadmap

The README already correctly places unimplemented features (evaluate_compliance, Agent Mode) in the roadmap section only. No changes needed there - the gap was in metadata claiming these as current capabilities.

## Task 6: Design Draft Status Markers (2026-02-28)

### Pattern: Vision Documents Need Explicit Status

When a design document describes both implemented and future features, add:
1. **Header status block** - prominent warning that document is "historical vision"
2. **Status legend** - define markers (✅ IMPLEMENTED, 🔴 NOT IMPLEMENTED, 🫂 PARTIAL)
3. **Per-tool markers** - add status to each tool/function heading
4. **Summary table** - include Status column in tool catalogs
5. **Implementation phases** - update checkboxes and add phase-level status

### Reference to Authoritative Source

Always point to README.md (or equivalent) as the source of truth for current capabilities.
This prevents design docs from being treated as contracts.

### Status Markers Used

- `✅ IMPLEMENTED` - Feature available in current release
- `🔴 NOT IMPLEMENTED` - Planned but not yet built  
- `🫂 PARTIAL` - Exists with differences from original spec

### Key Insight: Spec Drift

The design draft described 20+ tools, but only 13 are implemented. The gap included:
- evaluate_compliance (the "flagship" feature described in package description)
- assess_control (partially covered by get_assessment_questions)
- interview_control (partially covered by get_assessment_questions)
- manage_framework (CLI alternative exists)
- import_framework, build_mapping (not implemented)

This spec drift created trust issues (GAP-001, GAP-007 from Task 3).


## Task 7: Documentation Governance Pack (2026-02-28)

### Governance Documents Created

Two new files establish update discipline:
1. **CHANGELOG.md** - Keep a Changelog format with v0.1.3 baseline
2. **CONTRIBUTING.md** - Development workflow, verification, ownership

### Changelog Pattern

Follow keepachangelog.com format:
- Header with format reference and semver link
- Version sections with date tags
- Categories: Added, Changed, Deprecated, Removed, Fixed, Security
- [Unreleased] section for upcoming changes
- Version history table for quick reference

### Mandatory Verification Sequence

Every PR must pass this sequence:
```bash
ruff check --fix    # Lint
mypy src/           # Type check (strict mode)
pytest              # Tests
```

This is non-negotiable. If any fails, the PR is not ready.

### Ownership Matrix Pattern

Define who updates what with trigger conditions:

| Document | Owner | Trigger |
|----------|-------|--------|
| README.md | Any contributor | User-facing changes |
| CHANGELOG.md | PR author | Every user-facing PR |
| AGENTS.md | Maintainers | Architecture changes |
| pyproject.toml | Maintainers | Version/dependency changes |

### Drift Prevention Checklist

Before every release:
1. README tools table matches runtime (count comparison)
2. CHANGELOG has entries for all changes since last release
3. Version in pyproject.toml matches CHANGELOG
4. No claims of non-existent features

### Common Drift Patterns

- **Ghost tools**: Documented but not implemented
- **Missing tools**: Implemented but not documented
- **Stale examples**: Code samples that no longer work
- **Framework mismatch**: Docs claim more than exists

### Key Insight: Process Over Memory

Drift happens because contributors forget. The governance pack replaces memory with process:
- CHANGELOG update is part of every PR
- Verification commands are mandatory, not optional
- Ownership is explicit, not assumed
- Checklist is reviewed before every release

This makes documentation maintenance a first-class activity, not an afterthought.


## Task 8: Test Architecture Baseline and Prioritized Test Matrix (2026-02-28)

### Test Priority Framework

Tests should be prioritized by risk, not coverage percentage:

| Priority | Module | Risk Score | Rationale |
|----------|--------|------------|-----------|
| HIGH | lookup.py | Critical | Foundation for all other tools |
| HIGH | search.py | Critical | Primary user interaction path |
| HIGH | documentation.py | Critical | Persists state, complex logic |
| MEDIUM | framework_mgmt.py | Important | Cross-framework mappings |
| LOW | assessment.py | Useful | Generates questions, no mutations |

### Mock-Based Testing Pattern

For MCP tools that depend on external systems:

1. **Create mock fixtures in conftest.py**
   - Mock FrameworkManager for lookup tests
   - Mock ControlSearcher for search tests
   - Mock ComplianceStateManager for documentation tests

2. **Use AsyncMock for async methods**
   - All manager methods are async
   - `manager.list_controls = AsyncMock(return_value=[sample_control])`

3. **Provide sample data fixtures**
   - sample_framework_info, sample_control, sample_control_details
   - sample_search_result, sample_control_documentation, sample_evidence

### Mock Assertion Gotcha

When asserting mock calls with default arguments:

```python
# This FAILS if call was made without explicit defaults:
mock.assert_called_once_with(framework_id="x", function_id=None)

# This WORKS - check only what was actually passed:
call_args = mock.call_args
assert call_args.kwargs.get("framework_id") == "x"
```

Mock records only the kwargs explicitly passed, not default values.

### Test Organization

- **tests/conftest.py** - Shared fixtures (206 lines)
- **tests/test_lookup.py** - 9 tests for lookup tools
- **tests/test_search.py** - 9 tests for search tools
- **tests/test_documentation.py** - 15 tests for documentation tools
- **Total: 34 tests** (exceeds 13 minimum)

### Pytest Async Configuration

pyproject.toml must have:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

This enables `@pytest.mark.asyncio` decorator to work automatically.

### Dependency Installation

Dev dependencies must be installed explicitly:
```bash
uv pip install pytest pytest-asyncio
```

`uv sync --dev` didn't install pytest automatically - needed explicit install.

### Test Categories

Each test should be categorized:
- `[HAPPY]` - Happy path, normal operation
- `[EDGE]` - Edge cases (empty, not found)
- `[FILTER]` - Filtering behavior
- `[FEATURE]` - Specific feature verification
- `[PARAM]` - Parameter validation
- `[ERROR]` - Error handling
- `[STATUS]` - Status transitions
- `[TYPE]` - Type-specific behavior
- `[FORMAT]` - Output format options

### Evidence Artifacts

Test matrix should include:
- Module risk prioritization
- Test file structure
- Coverage by tool
- Fixture inventory
- Testing patterns used
- Deferred coverage items
- Verification commands




## Task 9: CI Workflow Baseline (2026-02-28)

### GitHub Actions Pattern with uv

Use `astral-sh/setup-uv@v5` action for deterministic uv installation:
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v5
  with:
    enable-cache: true
```

Combined with `actions/setup-python@v5` for Python version management.

### CI Step Sequence

The mandatory verification sequence from CONTRIBUTING.md becomes CI steps:
1. `uv sync` - Install dependencies
2. `uv run ruff check` - Lint (no --fix in CI)
3. `uv run mypy src/` - Typecheck
4. `uv run pytest` - Tests

### Key Insight: Separate Fix from Check

- Local dev: `ruff check --fix` auto-fixes issues
- CI: `ruff check` only reports (no --fix)

CI should fail on issues, not silently fix them.

### Trigger Pattern

```yaml
on:
  push:
    branches: [main]
  pull_request:
```

Runs on both push to main and all PRs - catches issues before merge.

### Existing Technical Debt

CI workflow revealed pre-existing issues:
- 28 ruff errors (unused imports, style issues)
- 32 mypy errors (missing type stubs for fastmcp/chromadb)

CI correctly configured to catch these; fixes are separate tasks.

### Evidence File Structure

Evidence files should include:
- Files created/modified
- Verification commands with output
- Known issues (pre-existing vs new)
- Baseline counts (tests, errors)


## Task 10: Tool-Contract Smoke Tests (2026-02-28)

### FastMCP Tool Testing Pattern

Tool functions in FastMCP are defined inside `register_*_tools(mcp: FastMCP)` functions as local functions decorated with `@mcp.tool()`. They are NOT module-level exports.

To test tools via the MCP interface:

```python
from fastmcp import FastMCP

mcp = FastMCP("test-server")

# Register tools
from compliance_oracle.tools.lookup import register_lookup_tools
register_lookup_tools(mcp)

# Get tool and call underlying function
tool = await mcp.get_tool("list_frameworks")
result = await tool.fn()  # Returns the original response object (not MCP-serialized)
```

### Contract Test Philosophy

Contract tests verify response **shape**, not internal logic:
- Assert response is not None
- Assert response is correct type (Pydantic model or dict)
- Assert required keys/attributes exist
- Assert key types are correct (list, str, dict, int)

They do NOT test:
- Edge cases (empty results, errors)
- Internal logic
- Mock call assertions

### Tool Response Types

| Tool | Response Type | Required Keys |
|------|---------------|---------------|
| list_frameworks | ListFrameworksResponse | frameworks |
| list_controls | ListControlsResponse | controls, framework_id, total_count |
| get_control_details | ControlDetails | id, name, description |
| search_controls | SearchResponse | results, query, total_results |
| get_control_context | dict | control, hierarchy |
| document_compliance | dict | success, control_id, status |
| link_evidence | dict | success, control_id, evidence_type, path |
| get_documentation | dict | framework, controls |
| export_documentation | dict | format, framework, content |
| compare_frameworks | dict | source, mappings |
| get_guidance | dict | control_id, control_name, description |
| get_framework_gap | GapAnalysisResult | gaps, summary, current_framework, target_framework |
| get_assessment_questions | AssessmentTemplate | questions, framework_id, scope |

### Test File Structure

- `tests/test_tool_contracts.py` - 13 contract tests, one per tool
- Each test class follows pattern: `Test{ToolName}Contract`
- Each test method: `test_tool_contract_{tool_name}`
- Tests are marked with `[CONTRACT]` category

### Mocking Strategy

Tools instantiate managers internally, so patch at the module level:

```python
with patch(
    "compliance_oracle.tools.lookup.FrameworkManager",
    return_value=mock_framework_manager,
):
    # Tool registration and execution
```

### Key Insight: Function-Level Decorators

The `@mcp.tool()` decorator registers the function with FastMCP, making it accessible via `mcp.get_tool()`. The original function remains callable via `tool.fn()`, which returns the actual response object rather than the MCP-serialized format.

### Test Count Summary

After this task: 47 total tests (34 existing + 13 new contract tests)
- test_lookup.py: 9 tests
- test_search.py: 9 tests
- test_documentation.py: 15 tests
- test_tool_contracts.py: 13 tests (NEW)


## Task 11: Coverage and Regression Guardrails (2026-02-28)

### Coverage Baseline Establishment

Current coverage: **32%** (47 tests, 1025 statements)

### High-Risk Module Identification

Coverage by module reveals clear priorities:

| Priority | Module | Coverage | Action |
|----------|--------|----------|--------|
| HIGH | tools/lookup.py | 100% | Maintain |
| HIGH | tools/search.py | 100% | Maintain |
| HIGH | tools/documentation.py | 66% | Improve |
| MEDIUM | rag/search.py | 17% | Add tests |
| MEDIUM | frameworks/mapper.py | 11% | Add tests |
| MEDIUM | frameworks/manager.py | 10% | Add tests |
| MEDIUM | documentation/state.py | 15% | Add tests |
| LOW | cli.py | 0% | Integration tests |

### pytest-cov Configuration Pattern

Add to pyproject.toml:
```toml
[tool.coverage.run]
source = ["src/compliance_oracle"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### Ratchet Policy Approach

- Document current baseline explicitly
- Do NOT set fail_under threshold initially (blocks progress)
- Policy: "Coverage should not decrease below baseline"
- High-risk modules listed with explicit coverage targets

### Coverage Command

```bash
pytest --cov=src/compliance_oracle --cov-report=term-missing
```

### Key Insight: 100% Modules Are Entry Points

The tools with 100% coverage (lookup.py, search.py) are thin wrappers around managers. The managers (frameworks/manager.py, rag/search.py) have low coverage. This is a testing architecture issue - unit tests mock the managers rather than testing them.

Future improvement: Add integration tests that exercise the full stack.

### Coverage Goals Progression

- Short-term: Maintain 32% baseline
- Medium-term: Target 50% overall
- Long-term: Target 70% for production readiness


## Task 12: 90-Day Risk-First Roadmap Backlog (2026-02-28)

### Backlog Structure Pattern

A risk-first roadmap uses weighted scoring across four dimensions:
1. **Risk Score (1-5)** - Trust impact if not addressed
2. **Priority (P0/P1/P2)** - Response time requirement
3. **Effort (S/M/L)** - Time estimate bands
4. **Dependencies** - Explicit blocking relationships

### Phase Organization

**Now/Next/Later** is clearer than version numbers for execution:
- **NOW (0-30 days):** Stabilization, CI quality, blocking issues
- **NEXT (30-60 days):** Coverage improvement, feature completion
- **LATER (60-90 days):** New features, framework expansion

### Required Fields Per Backlog Item

Every item must have:
- ID (R-XXX format for roadmap items)
- Title
- Type: FIX | ENHANCEMENT
- Priority: P0 | P1 | P2
- Risk Score: 1-5
- Effort: S | M | L
- Dependencies: List of IDs or "none"
- Milestone Exit: Measurable completion criteria

### Critical Path Analysis

The backlog should include a dependency graph showing the critical path to the highest-value item. For Compliance Oracle, the critical path is:

R-001 (ruff) → R-002 (mypy) → R-005 (rag tests) + R-006 (manager tests) → R-009 (evaluate_compliance)

This shows that ~3-4 weeks of debt payoff is required before the flagship feature can be safely implemented.

### Gap-to-Backlog Mapping

Gaps from the register map to backlog items:
- GAP-001, GAP-007 → R-009 (evaluate_compliance implementation)
- GAP-002, GAP-006 → Already fixed (Task 5)
- GAP-003 → R-008 (framework scope docs)
- GAP-004 → R-004 (core principle docs)
- GAP-005 → Already fixed (Task 6)

### Completed Items Pattern

Include a "Completed Items" section that references the original gap IDs. This provides traceability from gap discovery to resolution.

### README Roadmap Update Pattern

Replace version-only roadmap with:
1. 90-day execution backlog (Now/Next/Later tables)
2. Critical path summary
3. Version milestones for long-term vision

Keep tables concise in README; full details in evidence file.

### Key Insight: Debt Before Features

The roadmap prioritizes technical debt (28 ruff errors, 32 mypy errors, low coverage) before new features. Adding evaluate_compliance on a shaky foundation would repeat the trust violations that triggered this initiative.

### Verification Commands in Backlog

Include verification commands in the backlog so each item has a clear "done" criteria:
```bash
uv run ruff check          # R-001 milestone exit
uv run mypy src/           # R-002 milestone exit
pytest --cov=...           # Coverage items milestone exit
```

### Parallelization Opportunities

Document which items can proceed in parallel:
- R-003, R-004, R-008 can proceed alongside R-001/R-002
- R-005 and R-006 can proceed in parallel after R-001/R-002

This enables efficient resource allocation.

### Effort Estimation Reality Check

L (Large) items may take longer than estimated if they involve:
- LLM integration complexity
- Third-party library limitations
- Unexpected edge cases in framework data

Pad estimates for L items by 50% when planning sprints.



## Task 13: Enhancement Epics with Entry Gates (2026-02-28)

### Epic Definition Pattern

Epics differ from backlog items - they are larger initiatives with explicit gating:
1. **ID** - EPIC-XXX format for epics (vs R-XXX for roadmap items)
2. **Title** - Descriptive name
3. **Summary** - 1-2 sentence description
4. **Scope** - What capabilities will be delivered
5. **Out of Scope** - Explicitly what will NOT be included
6. **Entry Criteria** - Measurable conditions with current status
7. **Dependencies** - What must exist first
8. **Estimated Effort** - S/M/L/XL bands
9. **Roadmap Tier** - LATER or specific quarter target

### Entry Criteria Pattern

Each entry criterion must be:
1. **Measurable** - Specific command or metric (e.g., `uv run ruff check` returns 0)
2. **Current Status** - Show current state vs target (✅/❌/⚠️)
3. **Blocking** - If not met, the epic should NOT start

Example format:

| Criterion | Measurable Condition | Current Status |
|-----------|---------------------|----------------|
| Ruff errors resolved | `uv run ruff check` returns 0 | ❌ 28 pre-existing |

### Out of Scope Pattern

Explicitly listing what's OUT of scope prevents scope creep:
- Features that seem related but aren't in this epic
- Features that are in later epics
- Features that are explicitly deferred

This creates clear boundaries for what "done" means.

### Epic Dependency Graph Pattern

Epics should include a dependency graph showing:
- Which epics depend on others
- Which roadmap items block epics
- The critical path through the epic chain

Example:
```
EPIC-001 → EPIC-003 → EPIC-004 → EPIC-005
    ↑           ↑
    └───────────┴── R-001, R-002, R-005, R-006
```

### Risk If Started Too Early

Each epic should document what goes wrong if entry criteria are ignored:
- Lint/type errors mask bugs in new code
- Low coverage means regressions undetected
- CI instability blocks merges
- Trust damage if feature ships with quality issues

This provides rationale for the gates.

### Key Insight: Gated vs. Scheduled

Traditional roadmaps schedule work by calendar. Gated roadmaps schedule work by readiness:
- "Start EPIC-001 in March" → Wrong approach
- "Start EPIC-001 when R-001, R-002, R-005, R-006 are complete" → Correct approach

This prevents starting work before the foundation is ready.

### Epic Tiers

Map epics to roadmap phases:
- **LATER (60-90 days)** - EPIC-001, EPIC-002, EPIC-003
- **Q3 2026** - EPIC-004 (Local Web UI)
- **Q4 2026** - EPIC-005 (Multi-tenant)

This shows both near-term and long-term planning.

### README Epic Table Format

For the README, use a condensed table that links to full evidence:

| Epic | Title | Entry Gate | Effort | Tier |
|------|-------|------------|--------|------|
| EPIC-001 | evaluate_compliance | R-001, R-002, R-005, R-006 | L | LATER |

This provides quick reference while full details live in evidence file.

### Verification Pattern

Include verification commands in the epic definition:
```bash
uv run ruff check          # Entry criterion check
uv run mypy src/           # Entry criterion check
pytest --cov=...           # Coverage check
```

This enables automated verification of entry criteria.

### Effort Estimation for Epics

Use expanded effort bands for epics:
- **S (Small)** - 1-3 days
- **M (Medium)** - 1-2 weeks
- **L (Large)** - 2-4 weeks
- **XL (Extra Large)** - 4-8 weeks

Pad estimates by 50% for L and XL items when sprint planning.



## Task 14: End-to-End Consistency Audit (2026-02-28)

### Audit Scope Pattern

A final consistency audit should verify:
1. **Quality Gates** - Tests pass, coverage baseline established
2. **Narrative Parity** - Purpose claims consistent across ALL files
3. **Tool Parity** - Documentation matches runtime
4. **Roadmap Completeness** - All items have required fields
5. **Gap Register Status** - All gaps resolved or explicitly accepted

### Grep Scope Gotcha

When verifying claim removal, search ALL files in a directory, not just a subset:

```bash
# WRONG - may miss files
grep -n "pattern" file1 file2 file3 file4

# RIGHT - catches all occurrences
grep -rn "pattern" src/
```

Task 4 fixed `pyproject.toml` and `server.py` but missed `__init__.py` because the verification
command only checked 4 specific files.

### Audit Report Structure

A complete audit report should include:
1. Executive summary with PASS/PARTIAL/FAIL status per category
2. Detailed verification commands with expected vs observed output
3. Exceptions register with severity, trigger, and owner
4. Final verdict with clear recommendation
5. Handoff summary linking to all deliverables

### Exception Acceptance Pattern

Not all findings require immediate fix. Accept exceptions with:
- **Issue** - What's wrong
- **Severity** - LOW/MEDIUM/HIGH
- **Risk Class** - TRUST/OPERABILITY/SEMANTIC_DRIFT/CORRECTNESS
- **Disposition** - ACCEPT WITH TRIGGER
- **Trigger** - When to resolve
- **Owner** - Which roadmap item owns the resolution

### Handoff Documentation

The final audit should produce a handoff summary that lists:
- All tasks completed (1-14)
- All deliverables with file locations
- Next steps for the execution team
- Critical path to the highest-value item (R-009)

### Key Insight: Partial Fixes Are Still Drift

A fix that addresses 4/5 files is still drift. The audit must verify ALL occurrences,
not just the primary ones. The `__init__.py` file was missed because it wasn't in the
original Task 4 search scope.

### Verification Command Pattern

Include re-runnable verification commands in the audit report:

```bash
# Each command should have expected output documented
uv run pytest -q                    # Expected: 47 passed
grep -c "| \`" README.md             # Expected: 13
grep -rn "pattern" src/              # Expected: (specific result)
```

This enables anyone to re-verify the audit findings.

### Final Verdict Categories

- **READY** - All checks pass, no exceptions
- **READY WITH EXCEPTIONS** - Minor issues accepted with triggers
- **NOT READY** - Critical issues unresolved

The Compliance Oracle audit result: **READY WITH EXCEPTIONS** due to the `__init__.py`
drift (LOW severity, accepted with trigger).
## 2026-02-28: Testing FastMCP Tool Functions

**Problem:** Tests were mocking `ComplianceStateManager` methods directly but not exercising the actual tool functions defined inside `register_documentation_tools()`.

**Solution:** 
1. Create a FastMCP instance: `mcp = FastMCP("test")`
2. Register tools: `register_documentation_tools(mcp)`
3. Get tool functions via: `tools = await mcp._tool_manager.get_tools()`
4. Access the underlying function: `fn = getattr(tools["tool_name"], "fn")`
5. Call the function directly: `await fn(**kwargs)`

**Pattern for testing MCP tools:**
```python
from fastmcp import FastMCP
from compliance_oracle.tools.documentation import register_documentation_tools

mcp = FastMCP("test")
register_documentation_tools(mcp)
tools = await mcp._tool_manager.get_tools()
tool_fn = getattr(tools["tool_name"], "fn")

with patch("module.ClassName") as mock_class:
    mock_instance = MagicMock()
    mock_instance.method = AsyncMock()
    mock_class.return_value = mock_instance
    result = await tool_fn(param=value)
```

**Type checker note:** Use `getattr(tool, "fn")` instead of `tool.fn` to avoid basedpyright errors since the `fn` attribute isn't in the type stubs.

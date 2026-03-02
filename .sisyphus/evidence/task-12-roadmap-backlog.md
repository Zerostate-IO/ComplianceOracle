# Compliance Oracle - 90-Day Risk-First Roadmap Backlog

**Generated:** 2026-02-28
**Task:** 12 - Build 90-Day Risk-First Roadmap Backlog (Now/Next/Later)
**Source:** Gap Register (Task 3), Design Draft, Completed Tasks 4-11

---

## Priority Legend

| Priority | Definition | Response Time |
|----------|------------|---------------|
| **P0** | Critical / Trust-impacting | Immediate (blocking) |
| **P1** | High / Quality-impacting | Within sprint |
| **P2** | Medium / Enhancement | Next release cycle |

## Risk Score Legend

| Score | Trust Impact | Definition |
|-------|--------------|------------|
| 5 | Critical | User trust severely damaged, blocking adoption |
| 4 | High | Users encounter incorrect behavior regularly |
| 3 | Medium | Noticeable gap but workaround exists |
| 2 | Low | Minor inconvenience |
| 1 | Minimal | Cosmetic or documentation-only |

## Effort Legend

| Band | Definition | Time Estimate |
|------|------------|---------------|
| **S** | Small | Hours (1-8 hours) |
| **M** | Medium | Days (1-5 days) |
| **L** | Large | Weeks (1-3 weeks) |

## Type Legend

| Type | Definition |
|------|------------|
| **FIX** | Corrects a bug, gap, or technical debt |
| **ENHANCEMENT** | New feature or capability |

---

## Completed Items (Tasks 4-11)

These items were resolved as part of the documentation gap roadmap initiative:

| ID | Title | Type | Original Gap | Status |
|----|-------|------|--------------|--------|
| R-000 | Purpose alignment | FIX | GAP-001, GAP-007 | ✅ DONE |
| R-000 | README tools reconciliation | FIX | GAP-002, GAP-006 | ✅ DONE |
| R-000 | Design draft status markers | FIX | GAP-005 | ✅ DONE |
| R-000 | Governance pack (CHANGELOG, CONTRIBUTING) | FIX | - | ✅ DONE |
| R-000 | Test architecture baseline | FIX | - | ✅ DONE |
| R-000 | CI workflow baseline | FIX | - | ✅ DONE |
| R-000 | Tool-contract smoke tests | FIX | - | ✅ DONE |
| R-000 | Coverage guardrails | FIX | - | ✅ DONE |

---

## NOW (Days 0-30) - Stabilization, Trust Restoration, CI Quality

Focus: Address technical debt that blocks reliable development and deployment.

### R-001: Fix Pre-existing Ruff Errors

| Field | Value |
|-------|-------|
| **ID** | R-001 |
| **Title** | Fix pre-existing ruff linting errors |
| **Type** | FIX |
| **Priority** | P1 |
| **Risk Score** | 4 (CI blocks merge, quality degradation) |
| **Effort** | M (2-3 days) |
| **Dependencies** | none |
| **Milestone Exit** | `uv run ruff check` returns 0 errors |

**Description:** 28 pre-existing ruff errors (unused imports, style issues) block clean CI. Must be resolved before any feature work.

**Source:** Task 9 CI baseline revealed these as pre-existing debt.

---

### R-002: Fix Pre-existing MyPy Errors

| Field | Value |
|-------|-------|
| **ID** | R-002 |
| **Title** | Fix pre-existing mypy type errors |
| **Type** | FIX |
| **Priority** | P1 |
| **Risk Score** | 4 (CI blocks merge, type safety compromised) |
| **Effort** | M (2-3 days) |
| **Dependencies** | R-001 |
| **Milestone Exit** | `uv run mypy src/` returns 0 errors |

**Description:** 32 pre-existing mypy errors (missing type stubs for fastmcp/chromadb). May require py.typed markers or third-party stubs.

**Source:** Task 9 CI baseline revealed these as pre-existing debt.

---

### R-003: Increase Documentation Module Coverage

| Field | Value |
|-------|-------|
| **ID** | R-003 |
| **Title** | Increase test coverage for documentation.py (66% → 85%) |
| **Type** | FIX |
| **Priority** | P1 |
| **Risk Score** | 3 (persists state, complex logic) |
| **Effort** | M (2 days) |
| **Dependencies** | none |
| **Milestone Exit** | `pytest --cov` shows documentation.py ≥85% |

**Description:** documentation.py has 66% coverage but handles critical state persistence. Add tests for edge cases and error paths.

**Source:** Task 11 coverage baseline identified as HIGH priority module.

---

### R-004: Add Core Principle to README

| Field | Value |
|-------|-------|
| **ID** | R-004 |
| **Title** | Document "Never suggest fixes" core principle |
| **Type** | FIX |
| **Priority** | P2 |
| **Risk Score** | 2 (expectation gap for users) |
| **Effort** | S (1 hour) |
| **Dependencies** | none |
| **Milestone Exit** | README contains explicit statement about compliance-only focus |

**Description:** Design doc line 14 states: "Identify what isn't compliant and why. Never suggest fixes." This principle is not communicated to users.

**Source:** GAP-004 from Task 3 Gap Register.

---

## NEXT (Days 30-60) - Coverage Improvement, Feature Completion

Focus: Build confidence in existing features and prepare for new capabilities.

### R-005: Add RAG Search Module Tests

| Field | Value |
|-------|-------|
| **ID** | R-005 |
| **Title** | Add tests for rag/search.py (17% → 70%) |
| **Type** | FIX |
| **Priority** | P1 |
| **Risk Score** | 3 (primary user interaction path depends on it) |
| **Effort** | M (3 days) |
| **Dependencies** | R-001, R-002 |
| **Milestone Exit** | `pytest --cov` shows rag/search.py ≥70% |

**Description:** rag/search.py has only 17% coverage but is critical for semantic search. Add integration tests with mock ChromaDB.

**Source:** Task 11 coverage baseline identified as MEDIUM priority module.

---

### R-006: Add Framework Manager Tests

| Field | Value |
|-------|-------|
| **ID** | R-006 |
| **Title** | Add tests for frameworks/manager.py (10% → 70%) |
| **Type** | FIX |
| **Priority** | P1 |
| **Risk Score** | 3 (foundation for all lookup tools) |
| **Effort** | M (3 days) |
| **Dependencies** | R-001, R-002 |
| **Milestone Exit** | `pytest --cov` shows frameworks/manager.py ≥70% |

**Description:** frameworks/manager.py has only 10% coverage but is the foundation for all control lookup. Add integration tests.

**Source:** Task 11 coverage baseline identified as MEDIUM priority module.

---

### R-007: Add Crosswalk Mapper Tests

| Field | Value |
|-------|-------|
| **ID** | R-007 |
| **Title** | Add tests for frameworks/mapper.py (11% → 70%) |
| **Type** | FIX |
| **Priority** | P1 |
| **Risk Score** | 3 (cross-framework analysis depends on it) |
| **Effort** | M (2 days) |
| **Dependencies** | R-001, R-002 |
| **Milestone Exit** | `pytest --cov` shows frameworks/mapper.py ≥70% |

**Description:** frameworks/mapper.py has only 11% coverage but handles cross-framework mappings. Add tests for relationship types.

**Source:** Task 11 coverage baseline identified as MEDIUM priority module.

---

### R-008: Align Framework Scope Documentation

| Field | Value |
|-------|-------|
| **ID** | R-008 |
| **Title** | Align framework scope claims across docs |
| **Type** | FIX |
| **Priority** | P2 |
| **Risk Score** | 2 (expectation gap for planned features) |
| **Effort** | S (2 hours) |
| **Dependencies** | none |
| **Milestone Exit** | Design doc clarifies future scope; README reflects current scope |

**Description:** Design doc claims 800-171, SOC2, ISO 27001 support. README/pyproject.toml only list CSF 2.0 and 800-53. Add roadmap note clarifying future support.

**Source:** GAP-003 from Task 3 Gap Register.

---

## LATER (Days 60-90) - New Features, Framework Expansion

Focus: Deliver value through new capabilities while maintaining quality.

### R-009: Implement evaluate_compliance Tool

| Field | Value |
|-------|-------|
| **ID** | R-009 |
| **Title** | Implement evaluate_compliance MCP tool |
| **Type** | ENHANCEMENT |
| **Priority** | P0 |
| **Risk Score** | 5 (flagship feature, high user expectation) |
| **Effort** | L (2-3 weeks) |
| **Dependencies** | R-001, R-002, R-005, R-006 |
| **Milestone Exit** | Tool available at runtime; tests pass; documented in README |

**Description:** Core "Agent Mode" feature for evaluating designs/code against compliance frameworks. Requires LLM integration and RAG pipeline.

**Source:** PROJECT_DESIGN_DRAFT.md lines 200-292. Originally claimed in pyproject.toml (GAP-001, GAP-007).

**Note:** This was the false claim that triggered the gap roadmap initiative. Implementing it properly is the ultimate resolution.

---

### R-010: Implement assess_control Tool

| Field | Value |
|-------|-------|
| **ID** | R-010 |
| **Title** | Implement assess_control with evaluate_response flow |
| **Type** | ENHANCEMENT |
| **Priority** | P1 |
| **Risk Score** | 3 (extends existing assessment capability) |
| **Effort** | M (1 week) |
| **Dependencies** | R-009 |
| **Milestone Exit** | Tool available at runtime; returns maturity assessment |

**Description:** Extends get_assessment_questions with response evaluation. Returns maturity level, strengths, gaps, and recommendations.

**Source:** PROJECT_DESIGN_DRAFT.md lines 466-537.

---

### R-011: Implement interview_control Tool

| Field | Value |
|-------|-------|
| **ID** | R-011 |
| **Title** | Implement interview_control for guided Q&A |
| **Type** | ENHANCEMENT |
| **Priority** | P2 |
| **Risk Score** | 2 (improves documentation UX) |
| **Effort** | M (1 week) |
| **Dependencies** | R-010 |
| **Milestone Exit** | Tool available at runtime; supports start/submit/skip modes |

**Description:** Guided Q&A to document controls like a GRC portal questionnaire but conversational. Supports maturity indicators and evidence linking.

**Source:** PROJECT_DESIGN_DRAFT.md lines 740-827.

---

### R-012: Add NIST 800-171 Framework Support

| Field | Value |
|-------|-------|
| **ID** | R-012 |
| **Title** | Add NIST 800-171 Rev 2 framework support |
| **Type** | ENHANCEMENT |
| **Priority** | P2 |
| **Risk Score** | 2 (extends framework catalog) |
| **Effort** | M (3-5 days) |
| **Dependencies** | R-006 |
| **Milestone Exit** | Framework available via list_frameworks; controls searchable |

**Description:** Add NIST 800-171 Rev 2 (CUI protection) to framework catalog. Requires CPRT data fetch and mapping.

**Source:** PROJECT_DESIGN_DRAFT.md mentions as planned framework.

---

### R-013: Add SOC2 Trust Principles Support

| Field | Value |
|-------|-------|
| **ID** | R-013 |
| **Title** | Add SOC2 Trust Service Principles framework |
| **Type** | ENHANCEMENT |
| **Priority** | P2 |
| **Risk Score** | 2 (extends framework catalog) |
| **Effort** | M (3-5 days) |
| **Dependencies** | R-006, R-007 |
| **Milestone Exit** | Framework available; CSF→SOC2 mappings functional |

**Description:** Add SOC2 Trust Service Principles framework. Community-maintained source. Requires crosswalk mapping from CSF.

**Source:** PROJECT_DESIGN_DRAFT.md mentions as planned framework.

---

### R-014: Implement manage_framework MCP Tool

| Field | Value |
|-------|-------|
| **ID** | R-014 |
| **Title** | Implement manage_framework MCP tool |
| **Type** | ENHANCEMENT |
| **Priority** | P2 |
| **Risk Score** | 2 (exposes CLI capability via MCP) |
| **Effort** | M (3 days) |
| **Dependencies** | R-006 |
| **Milestone Exit** | Tool available; supports list/download/update/remove/validate actions |

**Description:** MCP wrapper for framework management currently available via CLI. Enables agents to manage frameworks directly.

**Source:** PROJECT_DESIGN_DRAFT.md lines 955-1028.

---

---

## Backlog Summary

### By Priority

| Priority | Count | Items |
|----------|-------|-------|
| P0 | 1 | R-009 |
| P1 | 6 | R-001, R-002, R-003, R-005, R-006, R-007, R-010 |
| P2 | 7 | R-004, R-008, R-011, R-012, R-013, R-014 |

### By Type

| Type | Count | Items |
|------|-------|-------|
| FIX | 8 | R-001, R-002, R-003, R-004, R-005, R-006, R-007, R-008 |
| ENHANCEMENT | 6 | R-009, R-010, R-011, R-012, R-013, R-014 |

### By Phase

| Phase | Count | Focus |
|-------|-------|-------|
| NOW (0-30 days) | 4 | Stabilization, CI quality |
| NEXT (30-60 days) | 4 | Coverage improvement |
| LATER (60-90 days) | 6 | New features, expansion |

### By Effort

| Effort | Count | Total Time (approx) |
|--------|-------|---------------------|
| S | 2 | 3 hours |
| M | 10 | 25-30 days |
| L | 1 | 2-3 weeks |

---

## Dependency Graph

```
R-001 (ruff errors) ─────────────────────────────────────┐
                                                          │
R-002 (mypy errors) ◄── R-001 ────────────────────────────┤
                                                          │
R-003 (doc coverage) ─────────────────────────────────────┤
                                                          │
R-004 (core principle) ───────────────────────────────────┤
                                                          │
R-005 (rag tests) ◄── R-001, R-002 ───────────────────────┤
                                                          │
R-006 (manager tests) ◄── R-001, R-002 ───────────────────┤
                                                          │
R-007 (mapper tests) ◄── R-001, R-002 ────────────────────┤
                                                          │
R-008 (scope docs) ───────────────────────────────────────┤
                                                          │
R-009 (evaluate_compliance) ◄── R-001, R-002, R-005, R-006┤
                                                          │
R-010 (assess_control) ◄── R-009 ─────────────────────────┤
                                                          │
R-011 (interview_control) ◄── R-010 ──────────────────────┤
                                                          │
R-012 (800-171) ◄── R-006 ────────────────────────────────┤
                                                          │
R-013 (SOC2) ◄── R-006, R-007 ────────────────────────────┤
                                                          │
R-014 (manage_framework) ◄── R-006 ───────────────────────┘
```

---

## Critical Path

**To unblock R-009 (evaluate_compliance - the flagship feature):**

1. R-001 (ruff) → R-002 (mypy) [parallel: R-003, R-004, R-008]
2. R-005 (rag tests) + R-006 (manager tests) [parallel]
3. R-009 (evaluate_compliance)

**Minimum time to R-009:** ~3-4 weeks with dedicated focus.

---

## Verification Commands

All items should pass these checks before marking complete:

```bash
# CI baseline
uv run ruff check          # 0 errors
uv run mypy src/           # 0 errors
uv run pytest              # All tests pass

# Coverage check
uv run pytest --cov=src/compliance_oracle --cov-report=term-missing

# Tool count verification
uv run python -c "
import asyncio
from compliance_oracle.server import mcp
async def main():
    tools = await mcp.get_tools()
    print(f'{len(tools)} tools')
asyncio.run(main())
"
```

---

## Notes

1. **R-009 is the ultimate goal** - It resolves the original trust violation (GAP-001, GAP-007) that triggered this entire initiative.

2. **Coverage before features** - The NOW and NEXT phases prioritize paying down technical debt. Adding features on a shaky foundation would repeat past mistakes.

3. **Dependency ordering matters** - R-001/R-002 unblock all subsequent test work. R-005/R-006 unblock R-009.

4. **Parallelization opportunities** - R-003, R-004, R-008 can proceed in parallel with R-001/R-002.

5. **Effort estimates are optimistic** - L items may take longer if LLM integration proves complex.

---

**END OF BACKLOG**

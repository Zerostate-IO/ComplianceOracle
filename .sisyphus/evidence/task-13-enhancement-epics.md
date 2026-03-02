# Compliance Oracle - Enhancement Epics with Entry Gates

**Generated:** 2026-02-28
**Task:** 13 - Define Enhancement Epics with Entry Gates (Not Immediate Build)
**Source:** PROJECT_DESIGN_DRAFT.md, Task 12 Roadmap Backlog

---

## Purpose

These epics define medium-term enhancements that should be considered **intentionally, not accidentally**. Each epic has explicit entry criteria that must be satisfied before work begins. This prevents starting ambitious features on an unstable foundation.

**Key Principle:** These epics are GATED. They should NOT be started until:
1. Stabilization is complete (R-001, R-002 resolved)
2. Coverage baseline is improved (R-003, R-005, R-006, R-007)
3. Quality gates are passing in CI

---

## Epic Definitions

### EPIC-001: evaluate_compliance (Agent Mode)

| Field | Value |
|-------|-------|
| **ID** | EPIC-001 |
| **Title** | evaluate_compliance - Design/Code Compliance Evaluation |
| **Summary** | Core "Agent Mode" feature for evaluating design documents and code against compliance frameworks via LLM-assisted analysis. |
| **Roadmap Tier** | LATER (Days 60-90) → Links to R-009 in backlog |

#### Scope

- RAG-based retrieval of relevant controls from input content
- LLM-assisted compliance evaluation with structured findings output
- Support for design documents, code, and architecture inputs
- Severity classification (critical/high/medium/low)
- Framework-specific evaluation (CSF 2.0, 800-53)
- Focus area filtering by function/category

#### Out of Scope

- Automated remediation suggestions (core principle: "Never suggest fixes")
- Real-time code scanning (static analysis integration)
- IDE plugins or editor integration
- Batch evaluation of entire repositories
- Custom LLM prompts per evaluation

#### Entry Criteria

| Criterion | Measurable Condition | Current Status |
|-----------|---------------------|----------------|
| Ruff errors resolved | `uv run ruff check` returns 0 errors | ❌ 28 pre-existing |
| MyPy errors resolved | `uv run mypy src/` returns 0 errors | ❌ 32 pre-existing |
| RAG search tested | `rag/search.py` coverage ≥70% | ❌ 17% |
| Framework manager tested | `frameworks/manager.py` coverage ≥70% | ❌ 10% |
| CI pipeline green | All CI checks pass on main branch | ❌ Blocked by lint/type errors |

#### Dependencies

- R-001: Fix pre-existing ruff errors
- R-002: Fix pre-existing mypy errors
- R-005: Add rag/search.py tests
- R-006: Add frameworks/manager.py tests

#### Estimated Effort

**L (Large)** - 2-3 weeks
- LLM integration complexity
- RAG pipeline refinement
- Structured output parsing
- Comprehensive testing

#### Risk If Started Too Early

- Lint/type errors mask bugs in new code
- Low coverage means regressions undetected
- CI instability blocks merges
- Trust damage if feature ships with quality issues

---

### EPIC-002: Additional Framework Support

| Field | Value |
|-------|-------|
| **ID** | EPIC-002 |
| **Title** | Additional Framework Support (800-171, SOC2, ISO 27001) |
| **Summary** | Extend framework catalog to include NIST 800-171, SOC2 Trust Principles, and ISO 27001, enabling cross-framework compliance analysis. |
| **Roadmap Tier** | LATER (Days 60-90) → Links to R-012, R-013 in backlog |

#### Scope

- NIST 800-171 Rev 2 (CUI protection) framework ingestion
- SOC2 Trust Service Principles framework ingestion
- ISO 27001:2022 framework ingestion (community-maintained source)
- Crosswalk mappings from CSF 2.0 to each new framework
- Search and lookup support for all new frameworks
- Gap analysis between frameworks

#### Out of Scope

- CIS Controls v8 (requires license)
- Custom/proprietary frameworks
- Automated framework updates from CPRT
- Framework version migration tools
- Partial/attestation-based frameworks (FedRAMP, CMMC)

#### Entry Criteria

| Criterion | Measurable Condition | Current Status |
|-----------|---------------------|----------------|
| Framework manager tested | `frameworks/manager.py` coverage ≥70% | ❌ 10% |
| Crosswalk mapper tested | `frameworks/mapper.py` coverage ≥70% | ❌ 11% |
| Framework scope documented | README clarifies future support | ⚠️ Partial |
| CI pipeline green | All CI checks pass on main branch | ❌ Blocked |

#### Dependencies

- R-006: Add frameworks/manager.py tests
- R-007: Add frameworks/mapper.py tests
- R-008: Align framework scope documentation

#### Estimated Effort

**M (Medium)** - 1-2 weeks per framework
- CPRT data fetch for 800-171
- Community data source for SOC2
- Crosswalk mapping creation
- Testing per framework

#### Risk If Started Too Early

- Framework ingestion bugs masked by low coverage
- Mapping errors undetected
- Inconsistent cross-framework behavior

---

### EPIC-003: Richer Assessment Flows

| Field | Value |
|-------|-------|
| **ID** | EPIC-003 |
| **Title** | Richer Assessment Flows (assess_control, interview_control) |
| **Summary** | Extend assessment capabilities with granular question types, response evaluation, and guided Q&A workflows for comprehensive control documentation. |
| **Roadmap Tier** | LATER (Days 60-90) → Links to R-010, R-011 in backlog |

#### Scope

- `assess_control` with evaluate_response mode (maturity assessment)
- `interview_control` for guided Q&A (start/submit/skip modes)
- Maturity level indicators (basic/intermediate/advanced)
- Policy vs. technical question categorization
- Per-asset question scoping
- Automation hooks for evidence ingestion from other MCP tools
- Recommended ControlStatus mapping from answers

#### Out of Scope

- External GRC platform integration (ServiceNow, Jira)
- Automated evidence collection (CI/CD pipelines)
- Multi-user interview sessions
- Interview templates marketplace
- Compliance scoring algorithms

#### Entry Criteria

| Criterion | Measurable Condition | Current Status |
|-----------|---------------------|----------------|
| evaluate_compliance implemented | EPIC-001 complete | ❌ Not started |
| Documentation module tested | `documentation.py` coverage ≥85% | ❌ 66% |
| Assessment templates working | `get_assessment_questions` returns valid templates | ✅ Working |
| CI pipeline green | All CI checks pass on main branch | ❌ Blocked |

#### Dependencies

- EPIC-001: evaluate_compliance (LLM evaluation patterns)
- R-003: Increase documentation.py coverage
- R-010: Implement assess_control tool
- R-011: Implement interview_control tool

#### Estimated Effort

**M (Medium)** - 1-2 weeks
- assess_control: 1 week
- interview_control: 1 week
- Testing and refinement: 3-5 days

#### Risk If Started Too Early

- LLM patterns from EPIC-001 not established
- Assessment state management bugs
- Poor UX if maturity indicators not calibrated

---

### EPIC-004: Local Web UI (Docker/Compose)

| Field | Value |
|-------|-------|
| **ID** | EPIC-004 |
| **Title** | Local Web UI (Docker/Compose) |
| **Summary** | Docker Compose stack with ComplianceOracle MCP server and local web UI for per-project posture views and interactive assessment sessions. |
| **Roadmap Tier** | Beyond LATER (Q3 2026 target per README) |

#### Scope

- Docker Compose configuration for MCP server + web UI
- Per-project compliance posture dashboard
- Interactive assessment session UI
- Framework hierarchy browser
- Evidence attachment interface
- Export/report generation UI
- Local-only deployment (no cloud services)

#### Out of Scope

- Multi-tenant support (separate epic)
- User authentication (single-user mode only)
- Cloud deployment templates (AWS, GCP, Azure)
- Mobile/responsive design
- Real-time collaboration
- External API access

#### Entry Criteria

| Criterion | Measurable Condition | Current Status |
|-----------|---------------------|----------------|
| All MCP tools stable | 0 runtime errors in production use | ⚠️ Needs validation |
| Coverage baseline achieved | Overall coverage ≥50% | ❌ 32% |
| Export formats complete | JSON/Markdown/CSV/HTML exports working | ✅ Working |
| Documentation state stable | No breaking changes to state schema | ⚠️ Needs validation |
| CI pipeline green | All CI checks pass on main branch | ❌ Blocked |

#### Dependencies

- EPIC-001: evaluate_compliance (core evaluation capability)
- EPIC-003: Richer Assessment Flows (assessment UI needs this)
- R-003: Increase documentation.py coverage
- R-005, R-006, R-007: Module coverage improvements

#### Estimated Effort

**L (Large)** - 3-4 weeks
- Frontend framework selection and setup: 3 days
- Dashboard and posture views: 1 week
- Assessment UI: 1 week
- Docker Compose configuration: 2 days
- Testing and documentation: 3 days

#### Risk If Started Too Early

- MCP API changes break frontend
- State schema changes require frontend rework
- Limited testing coverage means edge cases missed

---

### EPIC-005: Multi-tenant Deployment

| Field | Value |
|-------|-------|
| **ID** | EPIC-005 |
| **Title** | Multi-tenant Deployment (SaaS Model) |
| **Summary** | Full SaaS deployment with multi-tenancy, user model, roles, asset inventory, delegation/approval flows, and secure authentication/authorization. |
| **Roadmap Tier** | Beyond LATER (Q4 2026 target per README) |

#### Scope

- Multi-tenant data isolation
- User model with roles (admin, auditor, contributor, viewer)
- Asset inventory model scoped to controls
- Delegation and approval workflows
- Authentication integration (OAuth2, SAML)
- Authorization framework (RBAC)
- Secure deployment guides
- Audit logging

#### Out of Scope

- Billing/subscription management
- White-label customization
- API rate limiting (separate concern)
- Data residency requirements
- FedRAMP/ATO deployment

#### Entry Criteria

| Criterion | Measurable Condition | Current Status |
|-----------|---------------------|----------------|
| Local Web UI complete | EPIC-004 shipped and stable | ❌ Not started |
| Coverage at production level | Overall coverage ≥70% | ❌ 32% |
| Security review complete | No critical/high vulnerabilities | ❌ Not performed |
| Schema stable | No breaking changes for 30 days | ❌ Active development |
| CI pipeline green | All CI checks pass on main branch | ❌ Blocked |

#### Dependencies

- EPIC-004: Local Web UI (foundation for SaaS)
- R-001 through R-008: All stabilization complete
- Security audit of codebase
- Performance baseline established

#### Estimated Effort

**XL (Extra Large)** - 6-8 weeks
- Multi-tenant architecture: 2 weeks
- User model and auth: 1.5 weeks
- RBAC implementation: 1 week
- Asset inventory: 1 week
- Delegation/approval: 1 week
- Testing and security review: 1.5 weeks

#### Risk If Started Too Early

- Single-tenant assumptions baked into code
- No security review means vulnerabilities exposed
- State management not designed for isolation
- Performance unknown at scale

---

## Epic Dependency Graph

```
EPIC-001 (evaluate_compliance)
    ▲
    │
    ├── R-001 (ruff errors)
    ├── R-002 (mypy errors)
    ├── R-005 (rag tests)
    └── R-006 (manager tests)

EPIC-002 (Additional Frameworks)
    ▲
    │
    ├── R-006 (manager tests)
    ├── R-007 (mapper tests)
    └── R-008 (scope docs)

EPIC-003 (Richer Assessment)
    ▲
    │
    ├── EPIC-001 (evaluate_compliance)
    └── R-003 (documentation coverage)

EPIC-004 (Local Web UI)
    ▲
    │
    ├── EPIC-001 (evaluate_compliance)
    ├── EPIC-003 (assessment flows)
    └── Coverage ≥50%

EPIC-005 (Multi-tenant)
    ▲
    │
    ├── EPIC-004 (local web UI)
    └── Coverage ≥70%
```

---

## Entry Criteria Summary

| Epic | Blocking Criteria | Current Blockers |
|------|-------------------|------------------|
| EPIC-001 | R-001, R-002, R-005, R-006 | 28 ruff, 32 mypy, low coverage |
| EPIC-002 | R-006, R-007, R-008 | Low manager/mapper coverage |
| EPIC-003 | EPIC-001, R-003 | Blocked by EPIC-001 |
| EPIC-004 | EPIC-001, EPIC-003, Coverage ≥50% | Blocked by earlier epics |
| EPIC-005 | EPIC-004, Coverage ≥70% | Blocked by earlier epics |

---

## Verification

Each epic's entry criteria can be verified with:

```bash
# Ruff check
uv run ruff check

# MyPy check
uv run mypy src/

# Coverage check
uv run pytest --cov=src/compliance_oracle --cov-report=term-missing

# CI status
gh run list --limit 1
```

---

## Notes

1. **These epics are gated intentionally** - Starting them before entry criteria are met would repeat the mistakes that triggered the gap roadmap initiative.

2. **EPIC-001 is the critical path** - It unblocks EPIC-003 and EPIC-004, which in turn unblock EPIC-005.

3. **Coverage targets are minimums** - Higher coverage is always better; these are floor values.

4. **Effort estimates are optimistic** - L and XL items should be padded by 50% when sprint planning.

5. **Entry criteria should be re-evaluated quarterly** - As the codebase matures, criteria may be adjusted.

---

**END OF EPIC DEFINITIONS**

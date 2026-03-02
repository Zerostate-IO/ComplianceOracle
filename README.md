# Compliance Oracle MCP Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/package%20manager-uv-orange.svg)](https://docs.astral.sh/uv/)

Compliance Oracle is an MCP server that provides tools for working with compliance frameworks
(such as NIST CSF 2.0 and NIST SP 800-53 Rev. 5) from OpenCode/OhMyOpenCode agents.

It supports:

- Semantic search across framework controls via RAG/ChromaDB
- Documentation mode for tracking implementation status and evidence
- Cross-framework gap analysis (CSF → 800-53) using relationship-aware mappings
- A CLI for fetching, indexing, validating, and exporting data

## Design Philosophy

Compliance Oracle follows a single core principle:

> **Identify what isn't compliant and why. Never suggest fixes.**

This tool is designed to help you understand compliance gaps, not to prescribe
solutions. Remediation decisions require human judgment about risk tolerance,
resource constraints, and organizational context. The tool provides:

- Clear identification of non-compliant controls
- Evidence linking and documentation
- Cross-framework mapping and gap analysis

What it does NOT provide:

- Automated fix recommendations
- Remediation scripts
- "One-click" compliance solutions

## Hybrid Intelligence Mode

Compliance Oracle supports optional LLM enrichment via local Ollama for enhanced
rationale and context. Key behaviors:

- **Deterministic-first**: All control status and gap detection comes from rule-based logic
- **LLM enrichment only**: The LLM can only add rationale/context, never change assessments
- **Hard-degrade**: If Ollama is unavailable, the system returns deterministic results
- **No-fix guard**: All LLM output passes through a policy filter that blocks prescriptive language

See [docs/HYBRID_OPERATIONS.md](docs/HYBRID_OPERATIONS.md) for the complete operations
runbook covering Ollama setup, model selection, timeout tuning, and troubleshooting.

## Quickstart (Users)

Requires [uv](https://docs.astral.sh/uv/).

### 1. Set up the environment

```bash
git clone <repo> && cd ComplianceOracle
uv sync
```

### 2. Prepare NIST framework data

```bash
# Fetch NIST data (~10MB JSON)
uv run compliance-oracle fetch

# Index for semantic search (uses sentence-transformers)
uv run compliance-oracle index

# Verify status
uv run compliance-oracle status
```

If the `compliance-oracle` command is not found, prefix with `uv run` as shown above.

### 3. Connect to OpenCode

Add the following block to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "complianceoracle": {
      "type": "local",
      "command": ["uv", "--directory", "/path/to/ComplianceOracle", "run", "python", "-m", "compliance_oracle.server"],
      "enabled": true,
      "environment": {
        "PYTHONPATH": "/path/to/ComplianceOracle/src"
      }
    }
  }
}
```

Replace `/path/to/ComplianceOracle` with the actual path to this repository on your system.

### 4. Configure the compliance agent (OpenCode 1.0)

Create a Markdown subagent so you can explicitly mention the compliance agent from any project:

```bash
mkdir -p ~/.config/opencode/agent
$EDITOR ~/.config/opencode/agent/compliance-oracle.md
```

Use the following content:

```markdown
---
description: NIST CSF 2.0 and 800-53 compliance auditing, gap analysis, and documentation
mode: subagent
tools:
  complianceoracle_*: true
---

You are a dedicated compliance auditor using the Compliance Oracle MCP tools.

Focus on:
- Listing and exploring frameworks and controls
- Searching for relevant controls based on natural-language requirements
- Providing implementation guidance and checklists when asked
- Recording and exporting compliance documentation when requested
- Projecting cross-framework coverage and identifying gaps using formal mappings
```

Restart OpenCode after creating this file so the new agent is discovered.

### 5. Basic usage

In your OpenCode chat, explicitly mention `@compliance-oracle`:

```text
@compliance-oracle list all frameworks
@compliance-oracle search "data encryption"
@compliance-oracle list CSF 2.0 controls for PR.DS
@compliance-oracle get_framework_gap current_framework="nist-csf-2.0" target_framework="nist-800-53-r5"
```

## Architecture and agent access

### MCP server vs. compliance agent

| Component                      | Purpose                                                              | How to enable                    |
|--------------------------------|----------------------------------------------------------------------|----------------------------------|
| MCP server (`complianceoracle`) | Provides tools (lookup, search, documentation, mappings, gap analysis) | Configure in `opencode.json`     |
| Compliance agent (`@compliance-oracle`) | The only agent that should bind `complianceoracle_*` tools directly     | Add the subagent markdown file   |

The `AGENTS.md` file in this repository is a template you can copy into your project to
configure a compliance agent that uses the Compliance Oracle MCP server.

### Access pattern and delegation

- The recommended pattern is to access Compliance Oracle only through the `@compliance-oracle` subagent.
- Other agents (including general-purpose coding agents) should not bind `complianceoracle_*` tools directly.
- When another agent needs compliance context, it should delegate to `@compliance-oracle`, for example:

  ```text
  @compliance-oracle summarize our NIST CSF posture for this repository
  ```

This avoids unnecessary or accidental compliance queries, while still allowing orchestration
layers to pull in compliance insights when required.

## MCP tools catalog

The main MCP tools exposed by the server are:

| Tool                        | Purpose                              | Example                                                             |
|-----------------------------|--------------------------------------|---------------------------------------------------------------------|
| `list_frameworks()`         | List available frameworks            | `list_frameworks()`                                                 |
| `manage_framework()`         | Manage framework lifecycle (list, validate, update, remove) | `manage_framework(action='list')` |
| `list_controls()`           | Browse controls in a framework       | `list_controls("nist-csf-2.0", "PR")`                              |
| `search_controls()`         | Semantic search over controls        | `search_controls("MFA")`                                           |
| `get_control_details()`     | Retrieve full control details        | `get_control_details("PR.AC-01")`                                  |
| `document_compliance()`     | Record direct implementation status  | `document_compliance("PR.DS-02", "implemented", framework="nist-csf-2.0")` |
| `link_evidence()`           | Attach evidence to a control         | `link_evidence("PR.DS-02", "config", "docker-compose.yml", "Secrets mounted", line_start=10, line_end=15)` |
| `get_documentation()`       | Retrieve current documentation state | `get_documentation(framework="nist-csf-2.0")`                      |
| `export_documentation()`    | Export documentation as JSON/Markdown| `export_documentation("markdown", framework="nist-csf-2.0")`      |
| `compare_frameworks()`      | Show cross-framework mappings        | `compare_frameworks("PR.AC-01")`                                   |
| `get_guidance()`            | Provide implementation guidance      | `get_guidance("PR.AC-01")`                                         |
| `get_control_context()`     | Show hierarchy and related controls  | `get_control_context("PR.DS-01")`                                  |
| `get_framework_gap()`       | Relationship-aware migration gaps    | `get_framework_gap("nist-csf-2.0", "nist-800-53-r5")`             |
| `get_assessment_questions()` | Generate interview-style questions   | `get_assessment_questions(framework="nist-csf-2.0", function="PR")` |
| `assess_control()`          | Assess control with response eval    | `assess_control("PR.AC-01", response="We use MFA...", evaluate_response=True)` |
| `interview_control()`       | Guided Q&A to document a control     | `interview_control("PR.DS-01", mode="start")` |
| `evaluate_compliance()`      | Evaluate compliance posture against framework controls | `evaluate_compliance(content='Our security policy...', content_type='POLICY')` |

See `src/compliance_oracle/models/schemas.py` for complete response schemas.

## Direct vs. derived status and hypothetical coverage

Compliance Oracle distinguishes between two types of control status:

- Direct status (`status`): explicitly recorded via `document_compliance` for a given framework.
- Derived status (`derived_status` and `derived_sources`): optional, inferred coverage based on
  crosswalk mappings from other frameworks. Derived status is advisory, not authoritative.

Cross-framework mappings use typed relationships:

- `equivalent` – controls are roughly one-to-one
- `broader` – the source control covers more than the target
- `narrower` – the source control covers part of the target
- `related` – overlapping or related, but not directly covering

`get_framework_gap` treats the current framework as the source of truth and projects
hypothetical coverage into the target framework according to these relationship types. This
supports questions such as:

- "We are strong on NIST CSF; what would our NIST 800-53 posture look like?"
- "Which 800-53 controls have no meaningful mapping from our current framework?"

When you formally adopt a new framework, you should still perform direct assessments with
`document_compliance` for high‑risk controls and treat derived coverage as guidance rather than
final ground truth.

## Advanced usage

### Export a compliance report

```bash
compliance-oracle export --format markdown > compliance-report.md
```

### Start a custom MCP endpoint

```bash
uv run python -m compliance_oracle.server --transport http --port 8001
```

### Example LLM agent prompt

```text
Role: Compliance auditor using Compliance Oracle MCP

1. list_frameworks()
2. search_controls("[requirement]")
3. For each relevant control:
   - get_control_details()
   - get_guidance()
   - document_compliance() if evidence is found
4. get_documentation() → export_documentation("markdown")

Frameworks in scope: ["nist-csf-2.0", ...]
Project: [describe codebase]
```

## Development

```bash
uv sync --dev          # Install dev dependencies (pytest, ruff, mypy, etc.)
pytest                 # Run tests
pytest --cov=src/compliance_oracle --cov-report=term-missing  # Run with coverage
ruff check --fix       # Lint and auto-fix
mypy src/              # Type checking
```

If framework data is missing, run:

```bash
compliance-oracle fetch --framework all
```

## Data sources

- NIST CSF 2.0: <https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/CSF_2_0_0/home>
- NIST 800-53 Rev. 5: <https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home>
- Embeddings: `all-MiniLM-L6-v2` (sentence-transformers)
- Project state file: `.compliance-oracle/state.json` (per project)

## Roadmap

### 90-Day Execution Backlog (Risk-First)

See `.sisyphus/evidence/task-12-roadmap-backlog.md` for detailed item specifications.

#### NOW (Days 0-30) – Stabilization & CI Quality

| ID | Item | Type | Priority | Effort |
|----|------|------|----------|--------|
| R-001 | Fix pre-existing ruff errors (28) | FIX | P1 | M |
| R-002 | Fix pre-existing mypy errors (32) | FIX | P1 | M |
| R-003 | Increase documentation.py coverage (66%→85%) | FIX | P1 | M |
| R-004 | Document "Never suggest fixes" core principle | FIX | P2 | S |

#### NEXT (Days 30-60) – Coverage Improvement

| ID | Item | Type | Priority | Effort |
|----|------|------|----------|--------|
| R-005 | Add rag/search.py tests (17%→70%) | FIX | P1 | M |
| R-006 | Add frameworks/manager.py tests (10%→70%) | FIX | P1 | M |
| R-007 | Add frameworks/mapper.py tests (11%→70%) | FIX | P1 | M |
| R-008 | Align framework scope documentation | FIX | P2 | S |

#### LATER (Days 60-90) – New Features & Expansion

| ID | Item | Type | Priority | Effort |
|----|------|------|----------|--------|
| R-009 | **Implement evaluate_compliance tool** | ENHANCEMENT | P0 | L |
| R-010 | Implement assess_control with evaluate_response | ENHANCEMENT | P1 | M |
| R-011 | Implement interview_control for guided Q&A | ENHANCEMENT | P2 | M |
| R-012 | Add NIST 800-171 framework support | ENHANCEMENT | P2 | M |
| R-013 | Add SOC2 Trust Principles support | ENHANCEMENT | P2 | M |
| R-014 | Implement manage_framework MCP tool | ENHANCEMENT | P2 | M |


**Critical Path to R-009:** R-001 → R-002 → R-005 + R-006 → R-009 (~3-4 weeks)

### Enhancement Epics (Gated)

See `.sisyphus/evidence/task-13-enhancement-epics.md` for full epic specifications.

These epics define medium-term enhancements with explicit entry criteria. They should
NOT be started until stabilization is complete.

| Epic | Title | Entry Gate | Effort | Tier |
|------|-------|------------|--------|------|
| EPIC-001 | evaluate_compliance (Agent Mode) | R-001, R-002, R-005, R-006 complete | L | LATER |
| EPIC-002 | Additional Frameworks (800-171, SOC2, ISO) | R-006, R-007, R-008 complete | M | LATER |
| EPIC-003 | Richer Assessment Flows | EPIC-001 complete, R-003 complete | M | LATER |
| EPIC-004 | Local Web UI (Docker/Compose) | EPIC-001, EPIC-003, Coverage ≥50% | L | Q3 2026 |
| EPIC-005 | Multi-tenant Deployment (SaaS) | EPIC-004, Coverage ≥70% | XL | Q4 2026 |

**Key Principle:** Each epic has measurable entry criteria. Starting before these are met
would repeat the trust violations that triggered the gap roadmap initiative.

### Deferred Specifications

The following specifications define future epics that are explicitly deferred until
current stabilization work is complete. No implementation should occur based on these
specs until the entry criteria for the relevant epic are met.

| Spec | Title | Description | Target |
|------|-------|-------------|--------|
| [LATEX_REPORTING_SPEC](docs/LATEX_REPORTING_SPEC.md) | LaTeX Report Generation | Professional PDF compliance reports via LaTeX templates | Post-1.x |

---

### Version Milestones (Long-Term)

- **0.x – MCP server + CLI** ✅ COMPLETE
  - Core MCP tools for NIST CSF 2.0 / NIST SP 800-53.
  - RAG search, documentation state, evidence linking, gap analysis.

- **0.1.x – Assessment/interview API** ✅ COMPLETE
  - Relationship-aware mappings (`ControlRelationship`).
  - Direct vs. derived control status fields.
  - Assessment/interview templates via `get_assessment_questions`.

- **1.x–2.x – Richer assessment flows** (Target: Q2 2026)
  - More granular question types (policy vs. technical, per-asset questions).
  - Better guidance mapping from answers to recommended `ControlStatus` and notes.
  - Optional automation hooks to ingest evidence from other MCP tools.

- **3.x – Local-only web UI (Docker/Compose)** (Target: Q3 2026)
  - Docker Compose stack with ComplianceOracle MCP server and local web UI.
  - Per-project posture views and interactive assessment sessions.

- **4.0 – Multi-tenant deployment** (Target: Q4 2026)
  - Multi-tenant and user model with roles.
  - Asset inventory model scoped to controls.
  - Delegation and approval flows.
  - Secure deployment with authentication/authorization.

## License

MIT © Zerostate-IO

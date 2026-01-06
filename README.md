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
      "command": ["uv", "--directory", "/Users/legend/projects/ComplianceOracle", "run", "python", "-m", "compliance_oracle.server"],
      "enabled": true,
      "environment": {
        "PYTHONPATH": "/Users/legend/projects/ComplianceOracle/src"
      }
    }
  }
}
```

Replace `/Users/legend/projects/ComplianceOracle` with the actual path to this repository.

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
pytest                 # Run tests (if any)
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

## License

MIT © Zerostate-IO

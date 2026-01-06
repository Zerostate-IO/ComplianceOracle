# ComplianceOracle – Project Knowledge Base

Generated for developers and agents working with the Compliance Oracle MCP server.

## Overview

ComplianceOracle is a Python-based MCP server that provides compliance framework tooling
(NIST CSF 2.0, NIST SP 800-53 Rev. 5) for OpenCode/OhMyOpenCode and other MCP-compatible
clients. It focuses on semantic search, documentation state, evidence management, and
cross-framework mappings.

## Structure (high level)

```text
./
├── src/compliance_oracle/
│   ├── server.py              # MCP server entrypoint and tool registration
│   ├── cli.py                 # CLI entrypoint (compliance-oracle)
│   ├── frameworks/            # Framework catalogs and crosswalk mapper
│   ├── documentation/         # Compliance state management and export
│   ├── tools/                 # MCP tools (lookup, search, documentation, mappings, assessment)
│   ├── rag/                   # Semantic search / RAG integration
│   └── models/                # Pydantic schemas and domain models
├── data/frameworks/           # NIST CPRT JSON data (fetched)
├── data/mappings/             # Cross-framework mapping files (if present)
├── data/chroma/               # ChromaDB index data (generated)
├── scripts/                   # Utility scripts (e.g., NIST data fetch)
├── tests/                     # Test modules (currently minimal)
├── pyproject.toml             # Project, tooling, and type-checker configuration
└── README.md                  # User documentation and setup instructions
```

## Where to look

| Task / Question                               | Location                                      | Notes |
|----------------------------------------------|-----------------------------------------------|-------|
| Start MCP server                              | `src/compliance_oracle/server.py`             | FastMCP server, tool registration            |
| See MCP tool definitions                      | `src/compliance_oracle/tools/`                | Lookup, search, documentation, framework, assessment |
| Inspect framework catalogs                    | `src/compliance_oracle/frameworks/`           | Uses NIST CPRT JSON under `data/frameworks` |
| Understand documentation state format         | `src/compliance_oracle/documentation/state.py`| `.compliance-oracle/state.json` structure    |
| Search/embedding behavior                     | `src/compliance_oracle/rag/`                  | RAG index integration                        |
| Data models and enums                         | `src/compliance_oracle/models/schemas.py`     | ControlStatus, mappings, assessment models   |
| Scripts for fetching NIST data                | `scripts/`                                    | Used by CLI `fetch`                          |

## Conventions (project-specific)

- Python 3.12+, managed via `uv` (see `pyproject.toml`).
- Strict typing enabled (mypy strict mode); avoid suppressing type errors.
- Ruff is configured as the primary linter; follow its style output.
- Compliance state is stored per project in `.compliance-oracle/state.json`.
- Framework data is sourced from official NIST CPRT catalogs and stored in `data/frameworks/`.

## MCP agent configuration template

This repository ships an example TypeScript agent configuration you can copy into
Opencode/OhMyOpenCode projects:

```typescript
// AGENTS.md - Compliance Oracle Agent (add to your project)

export const complianceOracleAgent: AgentConfig = {
  name: "compliance-oracle",
  description: "NIST CSF 2.0 & 800-53 compliance auditing, gap analysis, documentation",
  mcp: "complianceoracle",
  tools: true,  // Auto-discover 12+ compliance tools
  icon: "🔒",
  trigger: [/compliance/i, /nist/i, /csf|800-53/i, /audit/i],
};
```

For OpenCode 1.0, the README also documents a Markdown subagent configuration that
binds the `complianceoracle_*` MCP tools to `@compliance-oracle`.

## Commands (common)

```bash
# Install dependencies
uv sync

# Fetch NIST framework data
uv run compliance-oracle fetch

# Build RAG index for semantic search
uv run compliance-oracle index

# Check MCP server status
uv run compliance-oracle status

# Run the MCP server directly (HTTP transport example)
uv run python -m compliance_oracle.server --transport http --port 8001

# Development helpers
uv sync --dev
pytest
ruff check --fix
mypy src/
```

## Notes / gotchas

- Ensure `compliance-oracle fetch` has been run before relying on search or guidance tools;
  framework JSON must be present under `data/frameworks`.
- RAG indices live under `data/chroma`; if you change framework data, rebuild the index with
  `compliance-oracle index`.
- MCP integration is designed to be explicit; other agents should delegate to the
  `@compliance-oracle` subagent rather than binding `complianceoracle_*` tools directly.

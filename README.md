# Compliance Oracle MCP Server {#readme}

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/package%20manager-uv-orange.svg)](https://docs.astral.sh/uv/)

**MCP server providing compliance framework tools (NIST CSF 2.0, NIST SP 800-53 Rev. 5)** for OpenCode/OhMyOpenCode agents.

- 🔍 **Semantic search** across 100+ controls via RAG/ChromaDB
- 📋 **Documentation mode** - track implementation status + evidence links
- 🔄 **Gap analysis** - CSF → 800-53 mappings
- 🛠️ **CLI** - fetch/index/validate/export

## 🎯 Quickstart (Users)

Get up and running in minutes. Requires [uv](https://docs.astral.sh/uv/).

### 1. Setup Environment
```bash
git clone <repo> && cd ComplianceOracle
uv sync
```

### 2. Prepare NIST Framework Data
```bash
# Fetch NIST data (~10MB JSON)
uv run compliance-oracle fetch

# Index for semantic search (uses sentence-transformers)
uv run compliance-oracle index

# Verify status
uv run compliance-oracle status
```
*Troubleshooting: If `compliance-oracle` command is not found, always prefix with `uv run`.*

### 3. Connect to OpenCode
Add the following to your `~/.config/opencode/opencode.json`:

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
*Note: Replace `/Users/legend/projects/ComplianceOracle` with your actual repository path.*

### 4. Setup Agent
Copy `AGENTS.md` to your project's root to enable the dedicated compliance agent:
```bash
cp AGENTS.md /path/to/your/project/
```

### 5. Test Usage
In your OpenCode chat, mention `@compliance-oracle`:
```
@compliance-oracle list all frameworks
@compliance-oracle search "data encryption"
@compliance-oracle list CSF 2.0 controls for PR.DS
```

## 🔍 How It Works

### MCP Server vs Agent

| Component | Purpose | How to Enable |
|-----------|---------|---------------|
| **MCP Server** | Provides tools (list_controls, search_controls, etc.) | Already loaded via `opencode.json` |
| **Agent** | Auto-delegates compliance tasks to MCP | Add to your `AGENTS.md` (see below) |

The `AGENTS.md` in this repo is a **template** for you to copy into YOUR project. It shows how to configure a compliance agent that uses the `complianceoracle` MCP server.

### For This Session

**Option A: Use Built-in Triggers (No config needed)**

Sisyphus (the default agent) has built-in triggers for compliance keywords:

```
compliance: review this code
nist: what controls apply here?
audit: check our CSF compliance
```

Just prefix your request with these keywords and Sisyphus auto-delegates.

**Option B: Dedicated Agent (Explicit @mentions)**

Create `~/AGENTS.md` with:

```typescript
export const complianceOracleAgent: AgentConfig = {
  name: "compliance-oracle",
  description: "NIST CSF 2.0 & 800-53 compliance auditing",
  mcp: "complianceoracle",
  tools: true,
  icon: "🔒",
  trigger: [/compliance/i, /nist/i, /csf|800-53/i, /audit/i],
};
```

Then you can use `@compliance-oracle` explicitly:

```
@compliance-oracle list all PROTECT controls
```

## 🛠️ MCP Tools Catalog {#tools}

| Tool | Purpose | Example |
|------|---------|---------|
| `list_frameworks()` | Available frameworks | `list_frameworks()` |
| `list_controls("nist-csf-2.0", "PR")` | Browse hierarchy | PR.AC, PR.DS... |
| `search_controls("MFA")` | Semantic RAG search | Returns top matches + scores |
| `get_control_details("PR.AC-01")` | Full spec + mappings | Impl examples, refs |
| `document_compliance(...)` | Track status | implemented/partial/planned |
| `link_evidence(...)` | Link code/config | `link_evidence("PR.DS-02", "config", "docker-compose.yml", "Secrets mounted", line_start=10, line_end=15)` |
| `get_documentation()` | Current state + summary | 42% complete |
| `export_documentation("markdown")` | Reports | MD/JSON exports |
| `compare_frameworks("PR.AC-01")` | Cross-framework | CSF → 800-53 |
| `get_guidance("PR.AC-01")` | Implementation advice | Step-by-step checklist |\n| `get_control_context("PR.DS-01")` | Hierarchy/Siblings | Find related controls |
| `get_framework_gap(...)` | Migration gaps | What's missing? |

**Full schemas:** `src/compliance_oracle/models/schemas.py`

## 🚀 Advanced Usage {#advanced}

### Export Compliance Report
```bash
compliance-oracle export --format markdown > compliance-report.md
```

### Custom MCP Endpoint
```bash
uv run python -m compliance_oracle.server --transport http --port 8001
```

### LLM Agent Prompt Template {#llm-template}
```
Role: Compliance Auditor using Compliance Oracle MCP

1. list_frameworks()
2. search_controls("[requirement]")
3. For each relevant control:
   - get_control_details()
   - get_guidance()
   - document_compliance() if evidence found
4. get_documentation() → export_documentation("markdown")

Framework: NIST CSF 2.0
Project: [describe codebase]
```

## 🧪 Development {#dev}

```bash
uv sync --dev          # + pytest/ruff/mypy
pytest                 # Unit tests
ruff check --fix       # Lint
mypy src/              # Types
```

**Missing data?** `compliance-oracle fetch --framework all`

## 📚 Data Sources {#data}

- NIST CSF 2.0: [CPRT Catalog](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/CSF_2_0_0/home)
- NIST 800-53 R5: [CPRT Catalog](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home)
- Embeddings: `all-MiniLM-L6-v2` (sentence-transformers)
- State: `.compliance-oracle/state.json` (per-project)

## 🔒 License

MIT © Zerostate-IO","filePath">/Users/legend/projects/ComplianceOracle/README.md
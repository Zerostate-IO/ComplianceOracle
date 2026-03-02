# Changelog

All notable changes to Compliance Oracle will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-02-28

### Added

- MCP server with 13 tools for compliance framework operations
- NIST CSF 2.0 and NIST SP 800-53 Rev. 5 framework support
- Semantic search via RAG/ChromaDB using sentence-transformers
- Documentation mode for tracking implementation status and evidence
- Cross-framework gap analysis with relationship-aware mappings
- Assessment interview templates via `get_assessment_questions`
- CLI for fetching, indexing, validating, and exporting data

### MCP Tools

| Tool | Description |
|------|-------------|
| `list_frameworks` | List available frameworks |
| `list_controls` | Browse controls in a framework |
| `search_controls` | Semantic search over controls |
| `get_control_details` | Retrieve full control details |
| `get_control_context` | Show hierarchy and related controls |
| `document_compliance` | Record direct implementation status |
| `link_evidence` | Attach evidence to a control |
| `get_documentation` | Retrieve current documentation state |
| `export_documentation` | Export documentation as JSON/Markdown |
| `compare_frameworks` | Show cross-framework mappings |
| `get_guidance` | Provide implementation guidance |
| `get_framework_gap` | Relationship-aware migration gaps |
| `get_assessment_questions` | Generate interview-style questions |

## [Unreleased]

### Planned

- `evaluate_compliance` tool for automated compliance evaluation
- Support for additional frameworks (800-171, SOC2, ISO 27001)
- Local web UI for posture visualization
- Multi-tenant deployment model

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 0.1.3 | 2025-02-28 | Assessment/interview API, relationship-aware mappings |
| 0.1.0 | - | Initial MCP server with core tools |

---

## How to Update This Changelog

**When to update:**
- Before every release (even patch releases)
- When adding, changing, fixing, or removing any user-facing feature
- When making breaking changes to APIs or configuration

**What to include:**
- Added: New features
- Changed: Changes to existing features
- Deprecated: Features scheduled for removal
- Removed: Features removed in this version
- Fixed: Bug fixes
- Security: Security-related changes

**Ownership:** Maintainers must update CHANGELOG.md as part of every PR that changes user-facing behavior. CI should fail if CHANGELOG is not updated alongside code changes.

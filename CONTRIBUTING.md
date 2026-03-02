# Contributing to Compliance Oracle

Thanks for contributing. This document covers setup, verification, and the rules that keep the project healthy.

## Development Setup

Prerequisites:
- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) package manager

```bash
# Clone and enter the repo
git clone <repo-url> && cd ComplianceOracle

# Install all dependencies (including dev tools)
uv sync --dev

# Fetch NIST framework data (required for testing)
uv run compliance-oracle fetch

# Build the RAG index (required for search tools)
uv run compliance-oracle index
```

## Verification Command Sequence

Run these commands before every commit. They are mandatory, not optional.

```bash
# 1. Lint check
ruff check --fix

# 2. Type check (strict mode enabled)
mypy src/

# 3. Run tests
pytest
```

If any command fails, fix the issue before committing. Do not suppress errors.

## Coverage Policy

### Current Baseline

- **Overall coverage**: 32% (47 tests)
- This is the initial baseline as of the coverage guardrails establishment.

### Ratchet Policy

Coverage should not decrease below the baseline. When adding new code:

1. Run `pytest --cov=src/compliance_oracle --cov-report=term-missing` to check coverage
2. New code should include tests that maintain or improve coverage
3. If coverage drops significantly, add tests before merging

### High-Risk Modules

These modules have high complexity or critical functionality and should be prioritized for test coverage:

| Module | Current Coverage | Priority |
|--------|------------------|----------|
| `tools/lookup.py` | 100% | HIGH (maintain) |
| `tools/search.py` | 100% | HIGH (maintain) |
| `tools/documentation.py` | 66% | HIGH (improve) |
| `rag/search.py` | 17% | MEDIUM |
| `frameworks/mapper.py` | 11% | MEDIUM |
| `frameworks/manager.py` | 10% | MEDIUM |
| `documentation/state.py` | 15% | MEDIUM |
| `cli.py` | 0% | LOW (CLI tested via integration) |

### Coverage Goals

- Short-term: Maintain 32% baseline, improve high-risk modules
- Medium-term: Target 50% overall coverage
- Long-term: Target 70% overall coverage for production readiness

## Pull Request Guidelines

### Before Opening a PR

1. Run the full verification sequence above
2. Update documentation if you changed user-facing behavior
3. Update CHANGELOG.md under `[Unreleased]` or a new version section
4. Ensure your branch is up to date with `main`

### PR Title Format

Use conventional commits style:

- `feat: add support for ISO 27001`
- `fix: correct control mapping for PR.AC-01`
- `docs: clarify MCP tool usage in README`
- `refactor: simplify framework loader`
- `test: add coverage for gap analysis`

### PR Description Must Include

- What changed and why
- How to verify the change works
- Any breaking changes or migration steps

### Review Requirements

- At least one approval from a maintainer
- All CI checks passing
- No unresolved conversations

## Commit Guidelines

- Write clear, descriptive commit messages
- Reference issues when applicable: `fix: resolve #42`
- Keep commits atomic: one logical change per commit
- Squash fixup commits before merging

## Documentation Update Requirements

Documentation is not optional. If you touch code, you touch docs.

### What Requires Documentation Updates

| Change Type | Files to Update |
|-------------|-----------------|
| New MCP tool | README.md (tools table), CHANGELOG.md |
| Modified tool signature | README.md (example column) |
| New CLI command | README.md (if user-facing) |
| New framework support | README.md, AGENTS.md, CHANGELOG.md |
| Breaking API change | README.md, CHANGELOG.md |
| New configuration option | README.md |

### Documentation Verification

After updating documentation:

1. Check that README.md tools table matches runtime tools
2. Run: `uv run python -c "import asyncio; from compliance_oracle.server import mcp; print([t for t in asyncio.run(mcp.get_tools())])"`
3. Compare output to README table

## Ownership and Update Triggers

### Who Updates What

| Document | Owner | Update Trigger |
|----------|-------|----------------|
| README.md | Any contributor | User-facing changes |
| CHANGELOG.md | PR author | Every PR with user-facing changes |
| AGENTS.md | Maintainers | Architecture changes, new tool categories |
| PROJECT_DESIGN_DRAFT.md | Maintainers | Major feature additions |
| pyproject.toml | Maintainers | Version bumps, dependency changes |

### Update Triggers

Update documentation immediately when:

- Adding, removing, or modifying any MCP tool
- Changing CLI command names or arguments
- Adding support for a new framework
- Modifying the configuration format
- Changing installation or setup steps

## Drift Prevention Checklist

Before every release, verify:

- [ ] README.md tools table matches `mcp.get_tools()` output
- [ ] CHANGELOG.md has entries for all user-facing changes
- [ ] Version in pyproject.toml matches CHANGELOG version
- [ ] AGENTS.md reflects current tool categories
- [ ] No claims of features that do not exist

### Common Drift Patterns to Avoid

1. **Ghost tools**: Documenting tools that don't exist at runtime
2. **Missing tools**: Implementing tools but not documenting them
3. **Stale examples**: Code examples that no longer work
4. **Framework mismatch**: Docs claim more frameworks than implemented

### Automated Verification (Future)

Consider adding CI checks for:

- Tool count comparison (README table vs runtime)
- Version consistency (pyproject.toml vs CHANGELOG)
- Link checking for external URLs

## Questions?

Open an issue with the `question` label, or start a discussion in the repository.

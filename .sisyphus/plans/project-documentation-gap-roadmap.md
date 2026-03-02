# ComplianceOracle Documentation, Gap Analysis, and 90-Day Remediation Roadmap

## TL;DR
> **Summary**: Build a code-grounded documentation map, close purpose/behavior drift, and execute a risk-first 90-day roadmap that stabilizes trust, testing, and delivery readiness before larger feature expansions.
> **Deliverables**:
> - Verified documentation-to-code traceability matrix
> - Purpose/behavior gap register with dispositions
> - Corrected and consistent documentation/metadata narrative
> - Test+CI baseline with measurable quality gates
> - Prioritized now/next/later enhancement roadmap with dependency gates
> **Effort**: Large
> **Parallel**: YES - 3 waves
> **Critical Path**: Task 1 -> Task 3 -> Task 4 -> Task 10 -> Task 12

## Context
### Original Request
Map project documentation, run a gap analysis on purpose vs intended behavior, and produce a strong roadmap of fixes and enhancements.

### Interview Summary
- Documentation should align to current implementation reality first.
- Deliverable must include implementation epics, not analysis-only output.
- Testing policy for execution is tests-after baseline.
- Prioritization must be risk-first.
- Roadmap horizon is 90 days, sequenced in phases.

### Metis Review (gaps addressed)
- Added guardrail to resolve false "evaluate designs/code" claims before feature expansion.
- Added explicit drift reconciliation for README vs design draft vs runtime tool surface.
- Added quality uplift track (tests/CI/coverage) to reduce execution risk.
- Added scope guardrails to prevent unapproved expansion into large new feature builds.

## Work Objectives
### Core Objective
Produce and execute a decision-complete, evidence-backed remediation plan that makes ComplianceOracle documentation truthful, complete, and operationally actionable while establishing a quality baseline for future enhancements.

### Deliverables
- `docs-mapping` artifact (claim -> source -> implementation evidence -> status).
- `gap-register` artifact (expected vs observed, risk class, disposition, owner).
- Updated canonical documentation/metadata set aligned to current tool behavior.
- CI + test baseline with reproducible verification commands.
- 90-day risk-weighted roadmap with milestones and dependency gates.

### Definition of Done (verifiable conditions with commands)
- Documentation claims and tool inventory are internally consistent:
  - `uv run python -c "from compliance_oracle.server import mcp; print(sorted([t.name for t in mcp._tools.keys()]))"`
- Quality baseline executes in CI-equivalent local sequence:
  - `ruff check`
  - `mypy src/`
  - `pytest`
- Roadmap artifacts exist and include priority/disposition fields:
  - `test -f README.md`
  - `test -f PROJECT_DESIGN_DRAFT.md`
  - `test -f .sisyphus/plans/project-documentation-gap-roadmap.md`

### Must Have
- Every major documentation claim mapped to executable code evidence.
- Every identified gap assigned a disposition (`fix now`, `schedule`, `accept`, `defer with trigger`).
- Risk-ranked backlog with clear dependencies and milestone exits.
- Tests-after QA scenarios attached to every execution task.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No speculative claims about unimplemented features.
- No silent addition of major product features during documentation remediation.
- No broad refactors unrelated to mapped gaps.
- No ambiguous backlog items without acceptance criteria.
- No roadmap items lacking owner category, dependency, and verification path.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: tests-after with `pytest` (existing config in `pyproject.toml`).
- QA policy: every task includes happy-path and failure/edge scenario.
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`.

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. Shared dependencies are extracted into Wave 1.

Wave 1: Baseline mapping and drift classification (Tasks 1-6)
Wave 2: Documentation correction and quality foundations (Tasks 7-11)
Wave 3: Enhancement shaping and final prioritized roadmap (Tasks 12-14)

### Dependency Matrix (full, all tasks)
- 1: none
- 2: none
- 3: 1,2
- 4: 3
- 5: 3
- 6: 3
- 7: 4,5,6
- 8: 2,3
- 9: 8
- 10: 9
- 11: 10
- 12: 4,7,11
- 13: 12
- 14: 7,12,13

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 6 tasks -> `writing`, `deep`, `unspecified-high`
- Wave 2 -> 5 tasks -> `writing`, `quick`, `unspecified-high`
- Wave 3 -> 3 tasks -> `deep`, `writing`, `unspecified-high`

## TODOs
> Implementation + Test = ONE task.
> Every task includes recommended agent profile, references, acceptance criteria, and QA scenarios.

- [x] 1. Build Documentation Surface Inventory and Claim Map

  **What to do**: Create a complete inventory of documentation-bearing artifacts and extract explicit claims (purpose, capabilities, scope, roadmap, quality expectations) into a traceability table with claim IDs.
  **Must NOT do**: Do not edit source code in this task; do not classify claims yet.

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: heavy synthesis and structured documentation output.
  - Skills: `[]` - no special skill required.
  - Omitted: `git-master` - no git operation required.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 3 | Blocked By: none

  **References**:
  - Pattern: `README.md:7` - canonical product description currently exposed to users.
  - Pattern: `AGENTS.md:7` - internal project purpose and operational focus.
  - Pattern: `PROJECT_DESIGN_DRAFT.md:11` - original architectural intent and claim set.
  - API/Type: `pyproject.toml:4` - package-level purpose statement.

  **Acceptance Criteria**:
  - [ ] Inventory includes every top-level documentation artifact and claim IDs in a single table.
  - [ ] Each claim row includes source file and line anchor.
  - [ ] Artifact is reproducibly generated from repository state (no external assumptions).

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path inventory generation
    Tool: Bash
    Steps: Run `ls` at repo root, then `grep -n "Compliance Oracle" README.md AGENTS.md PROJECT_DESIGN_DRAFT.md pyproject.toml`
    Expected: All four files appear and at least one claim anchor per file is captured.
    Evidence: .sisyphus/evidence/task-1-doc-surface.txt

  Scenario: Missing-claim edge case
    Tool: Bash
    Steps: Run `grep -n "evaluate" README.md AGENTS.md PROJECT_DESIGN_DRAFT.md pyproject.toml`
    Expected: Any absent claim is recorded explicitly as "not present" in the map, not silently skipped.
    Evidence: .sisyphus/evidence/task-1-doc-surface-error.txt
  ```

  **Commit**: YES | Message: `docs(mapping): inventory documentation claims with source anchors` | Files: `[README.md, AGENTS.md, PROJECT_DESIGN_DRAFT.md, pyproject.toml, docs artifacts]`

- [x] 2. Extract Runtime Tool Contract Baseline

  **What to do**: Enumerate actual MCP tool registrations and CLI command surface from code, producing a machine-verifiable "implemented contract" baseline.
  **Must NOT do**: Do not infer tools from design docs; only runtime/code evidence.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: code contract extraction with correctness sensitivity.
  - Skills: `[]` - no external integration skill required.
  - Omitted: `playwright` - no browser interactions.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 3,8 | Blocked By: none

  **References**:
  - Pattern: `src/compliance_oracle/server.py:21` - runtime tool registration entrypoints.
  - Pattern: `src/compliance_oracle/server.py:25` - assessment tools registration.
  - Pattern: `src/compliance_oracle/cli.py:16` - CLI root and command declarations.
  - API/Type: `README.md:131` - documented MCP tools table to compare against runtime.

  **Acceptance Criteria**:
  - [ ] Baseline lists all registered MCP tools with source module.
  - [ ] Baseline lists all CLI commands with command names.
  - [ ] Output is reproducible via commands committed in evidence.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path contract extraction
    Tool: Bash
    Steps: Run `uv run python -c "from compliance_oracle.server import mcp; print(sorted(mcp._tools.keys()))"` and `grep -n "@main.command" src/compliance_oracle/cli.py`
    Expected: MCP tool list and CLI command anchors are both captured.
    Evidence: .sisyphus/evidence/task-2-contract-baseline.txt

  Scenario: Failure path for import/runtime issue
    Tool: Bash
    Steps: Run the same Python extraction command with `PYTHONPATH=src`; capture non-zero exit if dependency/runtime fails.
    Expected: Failure details are logged and baseline is flagged blocked, not approximated.
    Evidence: .sisyphus/evidence/task-2-contract-baseline-error.txt
  ```

  **Commit**: YES | Message: `docs(contract): capture runtime MCP and CLI capability baseline` | Files: `[src/compliance_oracle/server.py, src/compliance_oracle/cli.py, docs artifacts]`

- [x] 3. Produce Purpose/Behavior Gap Register with Risk Disposition

  **What to do**: Join Task 1 and Task 2 outputs into a gap register (`expected vs observed`) classified by risk (`correctness`, `semantic drift`, `operability`, `trust`) and disposition (`fix now`, `schedule`, `accept`, `defer with trigger`).
  **Must NOT do**: Do not leave any high-risk gap without disposition.

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: cross-source reasoning and risk classification.
  - Skills: `[]` - standard analysis.
  - Omitted: `frontend-ui-ux` - not relevant.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 4,5,6,8 | Blocked By: 1,2

  **References**:
  - Pattern: `src/compliance_oracle/server.py:17` - potentially stale "evaluating designs and code" claim.
  - Pattern: `pyproject.toml:4` - package metadata purpose claim.
  - Pattern: `README.md:239` - roadmap/current-state narrative anchor.
  - Pattern: `PROJECT_DESIGN_DRAFT.md:187` - planned `evaluate_compliance` contract.

  **Acceptance Criteria**:
  - [ ] Every identified gap has risk class and disposition.
  - [ ] High-risk trust gaps are marked `fix now` unless explicitly accepted with trigger.
  - [ ] Register includes evidence link back to source line anchors.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path gap classification
    Tool: Bash
    Steps: Verify source anchors with `grep -n "evaluating designs and code" src/compliance_oracle/server.py pyproject.toml` and compare against runtime tool baseline.
    Expected: Gap register includes this mismatch with explicit risk class and disposition.
    Evidence: .sisyphus/evidence/task-3-gap-register.txt

  Scenario: Edge case unresolved disposition
    Tool: Bash
    Steps: Run validation check on gap register for empty disposition fields.
    Expected: Validation fails if any gap has blank disposition; task remains incomplete.
    Evidence: .sisyphus/evidence/task-3-gap-register-error.txt
  ```

  **Commit**: YES | Message: `docs(gaps): classify purpose-behavior drift with risk dispositions` | Files: `[gap register artifacts]`

- [x] 4. Define and Apply Canonical Purpose Narrative (Reality-First)

  **What to do**: Update primary purpose statements so top-level metadata and docs consistently reflect currently implemented capabilities; preserve future aspirations in roadmap sections only.
  **Must NOT do**: Do not claim unimplemented Agent Mode evaluation as current capability.

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: precision wording and consistency across docs/metadata.
  - Skills: `[]` - no specialty required.
  - Omitted: `deep` - this is execution of prior decisions, not new analysis.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 7,12 | Blocked By: 3

  **References**:
  - Pattern: `README.md:7` - user-facing product statement.
  - Pattern: `AGENTS.md:7` - internal project narrative.
  - Pattern: `src/compliance_oracle/server.py:17` - FastMCP instructions string.
  - Pattern: `pyproject.toml:4` - package description shown in package metadata.

  **Acceptance Criteria**:
  - [ ] Purpose text in these files describes implemented capability set accurately.
  - [ ] Future features are clearly marked as roadmap/future, not present tense.
  - [ ] No conflicting purpose statements remain among the four canonical files.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path narrative consistency
    Tool: Bash
    Steps: Run `grep -n "evaluating designs and code" README.md AGENTS.md src/compliance_oracle/server.py pyproject.toml`
    Expected: Either phrase is removed or explicitly scoped as future roadmap where applicable.
    Evidence: .sisyphus/evidence/task-4-purpose-alignment.txt

  Scenario: Failure path stale claim remains
    Tool: Bash
    Steps: Re-run grep after edits.
    Expected: If stale claim remains in any canonical file, task fails and is reopened.
    Evidence: .sisyphus/evidence/task-4-purpose-alignment-error.txt
  ```

  **Commit**: YES | Message: `docs(purpose): align canonical project narrative to implemented behavior` | Files: `[README.md, AGENTS.md, src/compliance_oracle/server.py, pyproject.toml]`

- [x] 5. Reconcile README Tool Catalog with Runtime Registration

  **What to do**: Update README MCP tools table so it exactly matches runtime registrations (including `get_assessment_questions` if present) and remove/flag non-existent tools.
  **Must NOT do**: Do not silently keep stale tool names for marketing completeness.

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: table/document precision.
  - Skills: `[]` - none needed.
  - Omitted: `ultrabrain` - low algorithmic complexity.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 7,12 | Blocked By: 3

  **References**:
  - Pattern: `README.md:135` - current tools table start.
  - Pattern: `src/compliance_oracle/server.py:21` - runtime registration set.
  - Pattern: `src/compliance_oracle/tools/assessment.py:1` - assessment tool module presence.
  - API/Type: `AGENTS.md:21` - tool group categories used in internal docs.

  **Acceptance Criteria**:
  - [ ] README tool list equals runtime registration set.
  - [ ] Every table row has accurate purpose wording aligned to code behavior.
  - [ ] Any non-implemented design-doc-only tools are explicitly labeled future or removed.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path table reconciliation
    Tool: Bash
    Steps: Extract runtime tools with Python command and compare to markdown tool code ticks in README.
    Expected: Set difference is empty.
    Evidence: .sisyphus/evidence/task-5-readme-tools.txt

  Scenario: Failure path orphaned doc tool
    Tool: Bash
    Steps: Introduce/scan for a known non-runtime tool token such as `evaluate_compliance` in README tools table.
    Expected: Validation flags mismatch and task fails until corrected.
    Evidence: .sisyphus/evidence/task-5-readme-tools-error.txt
  ```

  **Commit**: YES | Message: `docs(readme): reconcile MCP tool catalog with runtime registration` | Files: `[README.md]`

- [x] 6. Reframe PROJECT_DESIGN_DRAFT as Vision/History with Explicit Status

  **What to do**: Keep the design draft but add clear status markers that distinguish implemented, partially implemented, and future concepts to prevent it being treated as current contract.
  **Must NOT do**: Do not delete useful architectural rationale.

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: historical documentation curation.
  - Skills: `[]` - none required.
  - Omitted: `quick` - this needs careful cross-referencing.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 7,12 | Blocked By: 3

  **References**:
  - Pattern: `PROJECT_DESIGN_DRAFT.md:3` - draft version/date marker.
  - Pattern: `PROJECT_DESIGN_DRAFT.md:187` - `evaluate_compliance` spec anchor.
  - Pattern: `PROJECT_DESIGN_DRAFT.md:1515` - historical phased implementation timeline.
  - Pattern: `README.md:231` - active roadmap context to align against.

  **Acceptance Criteria**:
  - [ ] Document header clearly states status (historical vision vs current implementation).
  - [ ] Tool sections include status badges/labels (implemented/partial/future).
  - [ ] No reader could reasonably mistake the draft as authoritative runtime contract.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path status annotation
    Tool: Bash
    Steps: Run `grep -n "Status" PROJECT_DESIGN_DRAFT.md` and inspect labeled sections for major tool families.
    Expected: Status markers exist for core tool groups.
    Evidence: .sisyphus/evidence/task-6-design-draft-status.txt

  Scenario: Failure path unlabeled high-risk section
    Tool: Bash
    Steps: Check anchors for `evaluate_compliance` and phase timeline sections.
    Expected: If either section lacks explicit status context, task fails.
    Evidence: .sisyphus/evidence/task-6-design-draft-status-error.txt
  ```

  **Commit**: YES | Message: `docs(design): annotate draft status against implemented reality` | Files: `[PROJECT_DESIGN_DRAFT.md]`

- [x] 7. Publish Documentation Governance Pack

  **What to do**: Add/refresh governance docs (`CHANGELOG`, `CONTRIBUTING`, `docs quality checklist`) and define update ownership so drift does not recur.
  **Must NOT do**: Do not create governance docs without explicit update rules and triggers.

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: policy/process documentation.
  - Skills: `[]` - none.
  - Omitted: `deep` - decision already made.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 14 | Blocked By: 4,5,6

  **References**:
  - Pattern: `README.md:209` - current development practices section.
  - Pattern: `AGENTS.md:45` - conventions section to align contributor rules.
  - Pattern: `pyproject.toml:3` - versioning anchor used for changelog entries.
  - External: `https://keepachangelog.com/en/1.1.0/` - changelog format baseline.

  **Acceptance Criteria**:
  - [ ] Governance pack defines who updates what and when.
  - [ ] Changelog schema is adopted and seeded with current release baseline.
  - [ ] CONTRIBUTING includes mandatory verification command sequence.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path governance validation
    Tool: Bash
    Steps: Verify governance files exist and contain sections for owner, cadence, and validation commands.
    Expected: All required sections present.
    Evidence: .sisyphus/evidence/task-7-governance-pack.txt

  Scenario: Failure path missing ownership
    Tool: Bash
    Steps: Run text check for owner/cadence keywords in new governance docs.
    Expected: Missing ownership/cadence fails task.
    Evidence: .sisyphus/evidence/task-7-governance-pack-error.txt
  ```

  **Commit**: YES | Message: `docs(governance): add changelog contributing and drift-prevention policy` | Files: `[CHANGELOG.md, CONTRIBUTING.md, docs checklist files]`

- [x] 8. Create Test Architecture Baseline and Prioritized Test Matrix

  **What to do**: Define test scope by module/tool criticality, then create/expand baseline tests for highest-risk paths first (lookup/search/documentation/gap tools).
  **Must NOT do**: Do not aim for broad but shallow tests; prioritize critical-path depth.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: test architecture decisions and module prioritization.
  - Skills: `[]` - none.
  - Omitted: `writing` - this is test implementation-centric.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 9,10 | Blocked By: 2,3

  **References**:
  - Pattern: `pyproject.toml:62` - pytest configuration baseline.
  - Pattern: `tests/__init__.py:1` - current minimal test surface.
  - Pattern: `src/compliance_oracle/tools/lookup.py:1` - candidate critical module.
  - Pattern: `src/compliance_oracle/tools/documentation.py:1` - documentation-state critical module.

  **Acceptance Criteria**:
  - [ ] Test matrix ranks modules/tools by risk and impact.
  - [ ] Baseline suite includes executable tests for top-priority tools.
  - [ ] Test commands run without manual setup beyond documented prerequisites.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path test matrix + baseline execution
    Tool: Bash
    Steps: Run `pytest --collect-only` and `pytest -q` after creating baseline tests.
    Expected: Non-zero collected tests and successful run.
    Evidence: .sisyphus/evidence/task-8-test-baseline.txt

  Scenario: Failure path malformed test setup
    Tool: Bash
    Steps: Run `pytest -q` with intentionally missing fixture/import path check.
    Expected: Failure is captured with actionable traceback and fixed before completion.
    Evidence: .sisyphus/evidence/task-8-test-baseline-error.txt
  ```

  **Commit**: YES | Message: `test(baseline): add risk-prioritized test matrix and initial suite` | Files: `[tests/*, test matrix artifact]`

- [x] 9. Implement CI Workflow for Lint, Typecheck, and Tests

  **What to do**: Add CI automation that executes `ruff`, `mypy`, and `pytest` on pull requests/pushes with deterministic Python/uv setup.
  **Must NOT do**: Do not introduce non-reproducible local-only CI steps.

  **Recommended Agent Profile**:
  - Category: `quick` - Reason: focused workflow configuration task.
  - Skills: `[]` - no special skills required.
  - Omitted: `deep` - low architectural uncertainty.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 10,11 | Blocked By: 8

  **References**:
  - Pattern: `README.md:212` - expected development command sequence.
  - Pattern: `AGENTS.md:93` - project-standard validation commands.
  - API/Type: `pyproject.toml:48` - Ruff config.
  - API/Type: `pyproject.toml:56` - MyPy strict configuration.

  **Acceptance Criteria**:
  - [ ] CI workflow exists and triggers on PR + push.
  - [ ] Workflow runs ruff, mypy, pytest in order.
  - [ ] Failure in any stage marks workflow failed.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path CI dry verification
    Tool: Bash
    Steps: Validate workflow syntax and run local command parity: `ruff check && mypy src/ && pytest`.
    Expected: All commands pass locally and workflow YAML parses.
    Evidence: .sisyphus/evidence/task-9-ci-baseline.txt

  Scenario: Failure path stage gate enforcement
    Tool: Bash
    Steps: Introduce a known lint/type error in a temp branch and simulate CI command sequence.
    Expected: Sequence fails at first violating stage.
    Evidence: .sisyphus/evidence/task-9-ci-baseline-error.txt
  ```

  **Commit**: YES | Message: `ci(baseline): enforce lint typecheck and tests on changes` | Files: `[.github/workflows/*]`

- [x] 10. Add Tool-Contract Smoke Tests for Runtime-Documented Features

  **What to do**: Implement smoke/integration tests validating that documented core tools execute and return schema-conformant shape for representative inputs.
  **Must NOT do**: Do not overfit tests to mock-only behavior that bypasses runtime registration.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: integration-level testing and schema assertions.
  - Skills: `[]` - none.
  - Omitted: `quick` - requires careful contract coverage.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 11,12 | Blocked By: 9

  **References**:
  - Pattern: `src/compliance_oracle/server.py:20` - unified registration surface.
  - Pattern: `src/compliance_oracle/models/schemas.py:1` - response model contracts.
  - Pattern: `README.md:135` - tool list to validate against.
  - Test: `tests/__init__.py:1` - existing test package anchor.

  **Acceptance Criteria**:
  - [ ] Smoke tests cover all runtime-documented tools or documented rationale for exclusions.
  - [ ] Tests assert required keys/types, not brittle full payload snapshots.
  - [ ] `pytest` passes in clean environment after prerequisites.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path contract smoke
    Tool: Bash
    Steps: Run targeted smoke suite (`pytest -k "tool_contract or smoke" -q`).
    Expected: All selected tests pass with schema-shape assertions.
    Evidence: .sisyphus/evidence/task-10-contract-smoke.txt

  Scenario: Failure path contract drift
    Tool: Bash
    Steps: Execute smoke tests after altering/omitting expected field in controlled fixture.
    Expected: Test fails with explicit missing-field assertion.
    Evidence: .sisyphus/evidence/task-10-contract-smoke-error.txt
  ```

  **Commit**: YES | Message: `test(contract): add smoke tests for documented runtime tools` | Files: `[tests/*, src/compliance_oracle/models/schemas.py references]`

- [x] 11. Establish Coverage and Regression Guardrails

  **What to do**: Introduce coverage measurement and an initial floor suitable for current maturity; add regression policy for high-risk modules.
  **Must NOT do**: Do not set unrealistic threshold that blocks all progress.

  **Recommended Agent Profile**:
  - Category: `quick` - Reason: configuration and policy guardrails.
  - Skills: `[]` - none.
  - Omitted: `deep` - bounded decision.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 12 | Blocked By: 10

  **References**:
  - Pattern: `pyproject.toml:30` - dev dependency section for test tooling.
  - Pattern: `README.md:209` - development workflow section to extend.
  - Pattern: `AGENTS.md:74` - commands section where quality gates are documented.
  - External: `https://coverage.readthedocs.io/` - coverage configuration reference.

  **Acceptance Criteria**:
  - [ ] Coverage command integrated into local verification flow.
  - [ ] Initial threshold and ratchet policy documented.
  - [ ] Regression-critical modules are explicitly listed.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path coverage reporting
    Tool: Bash
    Steps: Run `pytest --cov=src/compliance_oracle --cov-report=term-missing`.
    Expected: Coverage report is produced and threshold rule evaluated.
    Evidence: .sisyphus/evidence/task-11-coverage-guardrails.txt

  Scenario: Failure path threshold breach
    Tool: Bash
    Steps: Execute coverage command with a threshold higher than current baseline in a dry check.
    Expected: Command fails and emits threshold breach reason.
    Evidence: .sisyphus/evidence/task-11-coverage-guardrails-error.txt
  ```

  **Commit**: YES | Message: `quality(coverage): add baseline threshold and regression guardrails` | Files: `[pyproject.toml, README.md, AGENTS.md, coverage config]`

- [x] 12. Build 90-Day Risk-First Roadmap Backlog (Now/Next/Later)

  **What to do**: Convert validated gaps into a prioritized 90-day execution backlog with weighted scoring (risk, trust impact, effort, dependency) and explicit milestone exits.
  **Must NOT do**: Do not include items without risk score or dependency mapping.

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: multi-factor prioritization and sequencing.
  - Skills: `[]` - none.
  - Omitted: `quick` - not a trivial planning pass.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: 13,14 | Blocked By: 4,7,11

  **References**:
  - Pattern: `README.md:231` - existing roadmap anchor to update/align.
  - Pattern: `PROJECT_DESIGN_DRAFT.md:1515` - historical phase model to reframe.
  - Pattern: `AGENTS.md:99` - operational gotchas and dependency constraints.
  - Pattern: `.sisyphus/plans/project-documentation-gap-roadmap.md:1` - governing execution plan.

  **Acceptance Criteria**:
  - [ ] Every backlog item has priority tier (P0/P1/P2), effort band, and dependencies.
  - [ ] Milestones include objective exit criteria.
  - [ ] Backlog includes fixes and enhancements with separate labels.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path roadmap scoring
    Tool: Bash
    Steps: Validate roadmap table columns include risk score, effort, dependency, milestone.
    Expected: No blank fields in prioritized items.
    Evidence: .sisyphus/evidence/task-12-roadmap-backlog.txt

  Scenario: Failure path unscored backlog item
    Tool: Bash
    Steps: Run checklist script/text scan for missing P-tier or dependency field.
    Expected: Any missing field fails validation.
    Evidence: .sisyphus/evidence/task-12-roadmap-backlog-error.txt
  ```

  **Commit**: YES | Message: `roadmap(prioritization): publish 90-day risk-first execution backlog` | Files: `[README.md roadmap sections, planning artifacts]`

- [x] 13. Define Enhancement Epics with Entry Gates (Not Immediate Build)

  **What to do**: Shape medium-term enhancement epics (for example `evaluate_compliance`, richer assessment flows, additional framework support) with explicit entry criteria so they are considered intentionally, not accidentally.
  **Must NOT do**: Do not start implementing large epics in this stabilization cycle unless promoted by roadmap milestone exit.

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: strategic decomposition with guardrails.
  - Skills: `[]` - none.
  - Omitted: `writing` - strategy dominates over prose.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 14 | Blocked By: 12

  **References**:
  - Pattern: `PROJECT_DESIGN_DRAFT.md:187` - `evaluate_compliance` envisioned capability.
  - Pattern: `README.md:245` - richer assessment flows roadmap section.
  - Pattern: `README.md:258` - long-horizon expansion themes.
  - Pattern: `src/compliance_oracle/server.py:17` - current claim boundary to protect.

  **Acceptance Criteria**:
  - [ ] Each enhancement epic includes prerequisites, scope, and non-goals.
  - [ ] Entry gates are measurable (quality baseline, dependency readiness, staffing assumptions).
  - [ ] Epics are linked to roadmap tier and not marked as current capability.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path epic gating
    Tool: Bash
    Steps: Validate each epic section has "entry criteria" and "out of scope" fields.
    Expected: All epics pass completeness check.
    Evidence: .sisyphus/evidence/task-13-enhancement-epics.txt

  Scenario: Failure path scope creep
    Tool: Bash
    Steps: Scan for language implying immediate implementation inside stabilization milestone.
    Expected: Any immediate-implementation language for gated epics fails task.
    Evidence: .sisyphus/evidence/task-13-enhancement-epics-error.txt
  ```

  **Commit**: YES | Message: `roadmap(enhancements): define gated epics for post-stabilization expansion` | Files: `[README.md roadmap, planning artifacts]`

- [x] 14. Run End-to-End Consistency Audit and Publish Final Roadmap Pack

  **What to do**: Execute final audit that checks claim consistency, tool/docs parity, quality gates, and roadmap completeness; publish final pack for execution handoff.
  **Must NOT do**: Do not close task while any high-risk drift remains unresolved or unaccepted.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: broad final verification across docs/code/tests/roadmap.
  - Skills: `[]` - none.
  - Omitted: `quick` - this is a comprehensive closure gate.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: Final Verification Wave | Blocked By: 7,12,13

  **References**:
  - Pattern: `README.md:7` - final purpose statement verification.
  - Pattern: `README.md:135` - final tool table verification.
  - Pattern: `src/compliance_oracle/server.py:17` - runtime instruction claim verification.
  - Pattern: `pyproject.toml:4` - package description parity check.

  **Acceptance Criteria**:
  - [ ] Final audit report includes pass/fail for narrative parity, tool parity, and quality gates.
  - [ ] All failed checks are either fixed or explicitly accepted with trigger and owner.
  - [ ] Roadmap pack is ready for `/start-work` execution without open decisions.

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Happy path end-to-end audit
    Tool: Bash
    Steps: Run `ruff check && mypy src/ && pytest` plus parity grep checks on purpose and tools sections.
    Expected: All checks pass and audit report marks READY.
    Evidence: .sisyphus/evidence/task-14-final-audit.txt

  Scenario: Failure path unresolved high-risk drift
    Tool: Bash
    Steps: Run drift register validation for unresolved high-risk items.
    Expected: Any unresolved high-risk gap blocks READY status.
    Evidence: .sisyphus/evidence/task-14-final-audit-error.txt
  ```

  **Commit**: YES | Message: `roadmap(finalize): publish audited execution-ready roadmap pack` | Files: `[roadmap pack + final audit artifacts]`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [x] F1. Plan Compliance Audit - oracle (issues found: stale evidence, README drift - FIXED)
- [x] F2. Code Quality Review - unspecified-high (APPROVED)
- [x] F3. Real Manual QA - unspecified-high (APPROVED)
- [x] F4. Scope Fidelity Check - deep (issue found: core principle violation - FIXED)

## Commit Strategy
- Use atomic commits by workstream: `docs`, `quality`, `tests`, `roadmap`.
- Do not mix narrative/documentation drift fixes with test/CI infrastructure in the same commit.
- Require passing local verification commands before each commit.

## Success Criteria
- No remaining high-risk claim/behavior mismatches in core project docs.
- Tool surface in docs matches runtime registration.
- CI enforces lint/type/test checks on every change.
- 90-day roadmap is dependency-aware, risk-ranked, and execution-ready.

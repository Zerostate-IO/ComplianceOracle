# Assessment Intelligence Hybrid V1 (Ollama)

## TL;DR
> **Summary**: Build a deterministic-first, Ollama-augmented assessment engine that can run in hybrid mode from day one while hard-degrading to deterministic-only when Ollama is unavailable.
> **Deliverables**:
> - Deterministic/LLM orchestration layer with strict policy guardrails
> - Ollama client integration with hard-degrade metadata and circuit-breaker behavior
> - Assessment and evaluation tool integration using a shared intelligence contract
> - CLI export command (json/markdown) to close current reporting gap and prepare LaTeX follow-on
> - Full unit/integration test suite for parity, outage behavior, and no-fix policy enforcement
> **Effort**: Large
> **Parallel**: YES - 3 waves
> **Critical Path**: T2 -> T3 -> T5 -> T6/T7 -> T11

## Context
### Original Request
User requested next enhancements after completed SOC2 and coverage work, explicitly suggesting report output ideas (including LaTeX), then selected Assessment Intelligence as the next priority.

### Interview Summary
- Priority epic selected: Assessment Intelligence.
- Operating mode selected: Hybrid deterministic + optional LLM from day one.
- LLM provider selected: local Ollama.
- Degrade model selected: hard degrade when Ollama is unavailable.

### Metis Review (gaps addressed)
- Must define provider strategy, deterministic-vs-LLM boundary, fallback behavior, and auditable metadata before implementation.
- Must prevent scope creep into remediation advice; enforce core principle in both deterministic and LLM paths.
- Must define executable acceptance criteria for outage behavior and parity checks.

### Oracle Architecture Review (gaps addressed)
- Adopt deterministic-first pipeline where control status remains deterministic source of truth.
- Use LLM as optional language/context layer only.
- Add output policy guard to block remediation language.
- Implement hard-degrade with stable response shape (`llm_used=false`, `degrade_reason` set).

## Work Objectives
### Core Objective
Deliver a production-safe hybrid assessment architecture that improves context richness without weakening auditability, deterministic correctness, or the "identify gaps only" principle.

### Deliverables
- New intelligence contracts and orchestrator modules under `src/compliance_oracle/assessment/`.
- Ollama adapter with timeout/circuit-breaker handling.
- Integration in `assess_control`, `interview_control`, and `evaluate_compliance` flows.
- Export metadata support in state/documentation surfaces.
- New CLI `export` command supporting `json` and `markdown` parity with MCP behavior.
- Complete automated tests and updated operator documentation.

### Definition of Done (verifiable conditions with commands)
- `uv run pytest tests/test_assessment.py -q` passes with hybrid + degrade coverage.
- `uv run pytest tests/test_framework_mgmt.py tests/test_tool_contracts.py -q` passes.
- `uv run pytest tests/ -q` passes.
- `uv run ruff check src/ tests/` passes.
- `uv run mypy src/` passes (or only pre-existing accepted baseline errors).
- `uv run compliance-oracle export --format json --framework nist-csf-2.0 --output /tmp/co-export.json` succeeds.
- `uv run compliance-oracle export --format markdown --framework nist-csf-2.0 --output /tmp/co-export.md` succeeds.

### Must Have
- Deterministic-first boundary: final control status and control validation remain deterministic.
- Ollama hybrid integration with hard-degrade behavior and explicit metadata in outputs.
- Enforced no-fix language policy for all generated findings/narratives.
- Backward-compatible MCP response envelopes.
- Test evidence for outage, timeout, malformed LLM output, and parity behavior.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No remediation suggestions or imperative fix language in any output path.
- No mandatory dependency on Ollama availability for successful deterministic assessments.
- No schema-breaking changes for existing clients unless explicitly versioned.
- No expansion into PDF compilation or full LaTeX renderer in this epic.
- No framework onboarding rewrite in this epic.

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: tests-after (pytest + targeted integration checks).
- QA policy: Every task includes agent-executed happy + failure scenarios.
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`.

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. Shared dependencies extracted into Wave 1.

Wave 1: Contracts and runtime foundation
- T1 Contracts and schemas for intelligence outputs
- T2 Runtime configuration for hybrid/Ollama/degrade controls
- T3 Ollama client adapter with timeout and circuit breaker
- T4 Output policy guard for no-fix enforcement
- T5 Orchestrator (deterministic-first, optional LLM enrichment)

Wave 2: Product integration
- T6 Integrate orchestrator into `assess_control`
- T7 Integrate orchestrator into `evaluate_compliance`
- T8 Integrate interview flow metadata and policy checks
- T9 Extend state/export metadata and MCP documentation tool parity
- T10 Add CLI `export` command (json/markdown parity)

Wave 3: Confidence hardening and operations
- T11 Hybrid parity and outage test suite
- T12 Documentation and operator runbook
- T13 Deferred LaTeX follow-on spec (scaffold only, no renderer)

### Dependency Matrix (full, all tasks)
| Task | Depends On | Blocks |
|---|---|---|
| T1 | - | T5, T6, T7, T9 |
| T2 | - | T3, T5, T11, T12 |
| T3 | T2 | T5, T11 |
| T4 | T1 | T5, T6, T7, T8, T11 |
| T5 | T1, T2, T3, T4 | T6, T7, T8, T11 |
| T6 | T5 | T11 |
| T7 | T5 | T11 |
| T8 | T5 | T11 |
| T9 | T1, T5 | T10, T11 |
| T10 | T9 | T12, T13 |
| T11 | T3, T4, T6, T7, T8, T9 | Final Verification |
| T12 | T10, T11 | Final Verification |
| T13 | T10, T12 | Final Verification |

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 5 tasks -> deep (3), unspecified-high (1), quick (1)
- Wave 2 -> 5 tasks -> deep (3), unspecified-high (1), quick (1)
- Wave 3 -> 3 tasks -> unspecified-high (2), writing (1)

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.
> Execute tasks by Task ID order (T1..T13) and dependency matrix, not by physical listing order.

- [ ] T10. Add CLI `export` command with JSON/Markdown parity

  **What to do**: Implement `export` command in `src/compliance_oracle/cli.py` that routes to `ComplianceStateManager.export` and supports `--format`, `--framework`, `--include-evidence`, `--include-gaps`, and `--output` options mirroring MCP export behavior.
  **Must NOT do**: Do not implement PDF/LaTeX output in this task; do not duplicate export formatting logic outside state manager.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: additive CLI command leveraging existing export core.
  - Skills: `[]` — click + existing state manager integration.
  - Omitted: `playwright` — no UI.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: T12, T13 | Blocked By: T9

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/cli.py:22` — command declaration conventions.
  - Pattern: `src/compliance_oracle/cli.py:214` — async command implementation pattern.
  - API/Type: `src/compliance_oracle/documentation/state.py:204` — export interface.
  - API/Type: `src/compliance_oracle/tools/documentation.py:171` — MCP export options parity.
  - Test: `tests/test_tool_contracts.py` — expected export behavior shape.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run compliance-oracle export --format json --framework nist-csf-2.0 --output /tmp/co-export.json` succeeds.
  - [ ] `uv run compliance-oracle export --format markdown --framework nist-csf-2.0 --output /tmp/co-export.md` succeeds.
  - [ ] `uv run pytest tests/ -k export -q` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: CLI export happy path
    Tool: interactive_bash
    Steps: Run `uv run compliance-oracle export --format markdown --framework nist-csf-2.0 --output /tmp/co-export.md` then read generated file.
    Expected: Command exits 0; file exists; first line starts with `# Compliance Documentation:`.
    Evidence: .sisyphus/evidence/task-T10-cli-export-happy.txt

  Scenario: CLI invalid format failure path
    Tool: interactive_bash
    Steps: Run `uv run compliance-oracle export --format latex --framework nist-csf-2.0`.
    Expected: CLI exits non-zero with clear validation message for allowed formats.
    Evidence: .sisyphus/evidence/task-T10-cli-export-error.txt
  ```

  **Commit**: YES | Message: `feat(cli): add compliance export command for json and markdown` | Files: `src/compliance_oracle/cli.py`, `tests/test_cli.py`

- [ ] T11. Build hybrid parity, outage, and policy regression suite

  **What to do**: Add/extend tests to verify deterministic-vs-hybrid parity, hard-degrade behavior under Ollama failure, malformed LLM output handling, and explicit no-fix policy enforcement across assessment/evaluation paths.
  **Must NOT do**: Do not rely on live Ollama during CI; all hybrid behavior must be testable with mocks/fixtures.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: broad regression safety across modules.
  - Skills: `[]` — pytest + mocking discipline.
  - Omitted: `frontend-ui-ux` — not needed.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: Final Verification | Blocked By: T3, T4, T6, T7, T8, T9

  **References** (executor has NO interview context — be exhaustive):
  - Test: `tests/test_assessment.py` — current broad unit coverage.
  - Test: `tests/test_evaluation.py` — finding language and evaluation behavior.
  - Test: `tests/test_tool_contracts.py` — cross-tool response contract checks.
  - Pattern: `src/compliance_oracle/tools/assessment.py:915` — assess path integration point.
  - Pattern: `src/compliance_oracle/tools/evaluation.py:427` — evaluation response composition.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_assessment.py tests/test_evaluation.py tests/test_tool_contracts.py -q` passes.
  - [ ] `uv run pytest tests/test_assessment.py -k "hybrid or degrade or policy" -q` passes.
  - [ ] `uv run pytest tests/ -q` passes end-to-end.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Deterministic/hybrid parity happy path
    Tool: Bash
    Steps: Run test that executes same input in deterministic and hybrid modes with mocked LLM enrichment.
    Expected: Control IDs/statuses and gap IDs are identical; hybrid may add rationale text only.
    Evidence: .sisyphus/evidence/task-T11-parity-happy.txt

  Scenario: Malformed LLM output failure path
    Tool: Bash
    Steps: Run test with mocked Ollama returning invalid JSON payload.
    Expected: System degrades cleanly, llm_used=false, degrade_reason='ollama_malformed_response', and response remains valid.
    Evidence: .sisyphus/evidence/task-T11-parity-error.txt
  ```

  **Commit**: YES | Message: `test(assessment): add hybrid parity and outage regression suite` | Files: `tests/test_assessment.py`, `tests/test_evaluation.py`, `tests/test_tool_contracts.py`

- [ ] T12. Publish hybrid operations runbook and developer docs

  **What to do**: Update docs for local Ollama setup, model selection, timeout tuning, hard-degrade semantics, and troubleshooting. Document deterministic boundary and no-fix policy constraints for contributors/operators.
  **Must NOT do**: Do not document speculative production deployment patterns not supported by code.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: operational documentation and guardrail clarity.
  - Skills: `[]` — technical writing only.
  - Omitted: `git-master` — no history surgery required.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: Final Verification | Blocked By: T10, T11

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `README.md` Design Philosophy + MCP tool catalog.
  - Pattern: `src/compliance_oracle/tools/assessment.py:944` — interview tool mode docs.
  - Pattern: `src/compliance_oracle/tools/evaluation.py:373` — evaluation behavior docs.
  - External: `https://github.com/ollama/ollama/blob/main/docs/api.md` — local runtime behavior and parameters.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/ -q` still passes after doc updates.
  - [ ] `uv run ruff check src/ tests/` still passes (no code side effects from docs).
  - [ ] README and/or docs contain explicit section for `hard degrade` behavior and `no remediation suggestions` guardrail.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Operator runbook happy path
    Tool: Bash
    Steps: Follow documented steps to run hybrid assessment with local Ollama reachable (using mocked/local test command path).
    Expected: Documented commands execute as written and produce expected metadata fields.
    Evidence: .sisyphus/evidence/task-T12-runbook-happy.txt

  Scenario: Outage troubleshooting path
    Tool: Bash
    Steps: Simulate Ollama unavailable and follow runbook troubleshooting/degrade verification commands.
    Expected: Runbook leads to deterministic-only operation verification with explicit degrade metadata.
    Evidence: .sisyphus/evidence/task-T12-runbook-error.txt
  ```

  **Commit**: YES | Message: `docs(assessment): add hybrid ollama hard-degrade runbook` | Files: `README.md`, `docs/*assessment*`, `docs/*operations*`

- [ ] T13. Define deferred LaTeX follow-on specification (no implementation)

  **What to do**: Produce a deferred spec document that defines LaTeX-first reporting scope, template contract, metadata mapping, and acceptance gates for a future epic. Keep this task planning-only within implementation branch (no renderer code).
  **Must NOT do**: Do not add `.tex` generation code, pandoc/pdf toolchain, or new runtime dependencies in this epic.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: specification artifact only.
  - Skills: `[]` — concise technical spec drafting.
  - Omitted: `playwright` — irrelevant.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: Final Verification | Blocked By: T10, T12

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/documentation/state.py:204` — canonical export source for future renderer input.
  - Pattern: `src/compliance_oracle/tools/documentation.py:171` — export tool options and behavior.
  - Pattern: `src/compliance_oracle/cli.py` — newly added export command behavior from T10.
  - Test: `tests/test_documentation.py` — current export assumptions that LaTeX work must preserve.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Spec file exists with sections: scope, data contract, template contract, non-goals, acceptance gates.
  - [ ] Spec explicitly states deferred status and no code implementation in current epic.
  - [ ] Cross-reference from README roadmap section is added.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Spec completeness happy path
    Tool: Bash
    Steps: Validate document contains required headings and references to JSON/Markdown export sources.
    Expected: All required sections present and internally consistent.
    Evidence: .sisyphus/evidence/task-T13-latex-spec-happy.txt

  Scenario: Scope-bleed failure path
    Tool: Bash
    Steps: Scan changed files for LaTeX runtime code additions (*.tex generation, pandoc invocation, pdf libs).
    Expected: No runtime/report renderer code introduced; only specification/docs changes.
    Evidence: .sisyphus/evidence/task-T13-latex-spec-scope-check.txt
  ```

  **Commit**: YES | Message: `docs(roadmap): add deferred latex reporting specification` | Files: `docs/*latex*`, `README.md`

- [ ] T7. Integrate intelligence orchestrator into `evaluate_compliance`

  **What to do**: Update `src/compliance_oracle/tools/evaluation.py` to use orchestrator-enriched analysis while preserving deterministic gap detection as source of truth. Ensure returned findings remain gap-only and policy-guarded.
  **Must NOT do**: Do not let LLM change evaluated control set or severity mapping derived from deterministic logic.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: evaluation flow spans search, control details, and output policy.
  - Skills: `[]` — standard backend integration.
  - Omitted: `dev-browser` — no browser use case.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: T11 | Blocked By: T5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/tools/evaluation.py:270` — `_evaluate_against_controls` deterministic core.
  - Pattern: `src/compliance_oracle/tools/evaluation.py:365` — `evaluate_compliance` assembly path.
  - Pattern: `src/compliance_oracle/tools/evaluation.py:218` — `_generate_finding` no-fix wording.
  - API/Type: `src/compliance_oracle/rag/search.py:64` — indexed control retrieval assumptions.
  - Test: `tests/test_evaluation.py` — baseline for no-fix and content scoring behavior.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_evaluation.py -q` passes.
  - [ ] `uv run pytest tests/test_tool_contracts.py -k evaluate_compliance -q` passes.
  - [ ] `uv run mypy src/compliance_oracle/tools/evaluation.py` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: evaluate_compliance hybrid happy path
    Tool: Bash
    Steps: Run test with representative design-doc content, mocked healthy Ollama, and indexed framework fixture.
    Expected: findings_count > 0 when gaps exist; llm_used=true metadata present; finding language remains non-prescriptive.
    Evidence: .sisyphus/evidence/task-T7-evaluate-happy.txt

  Scenario: framework-not-indexed failure path
    Tool: Bash
    Steps: Run test where index attempt returns 0 controls.
    Expected: Error response includes framework-not-found/no-controls message and no uncaught exception.
    Evidence: .sisyphus/evidence/task-T7-evaluate-error.txt
  ```

  **Commit**: YES | Message: `feat(evaluation): add hybrid enrichment with deterministic guardrails` | Files: `src/compliance_oracle/tools/evaluation.py`, `tests/test_evaluation.py`, `tests/test_tool_contracts.py`

- [ ] T8. Extend `interview_control` submit flow with hybrid metadata and policy enforcement

  **What to do**: Integrate orchestrator metadata into submit-mode outputs in `src/compliance_oracle/tools/assessment.py` while preserving existing interview lifecycle (`start`, `submit`, `skip`). Apply policy guard to generated summaries that include LLM-enriched language.
  **Must NOT do**: Do not change existing mode names, and do not require Ollama for `start`/`skip` paths.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: multi-mode API compatibility with state write behavior.
  - Skills: `[]` — follow existing interview patterns.
  - Omitted: `playwright` — no UI surface.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: T11 | Blocked By: T5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/tools/assessment.py:672` — `_interview_start` path.
  - Pattern: `src/compliance_oracle/tools/assessment.py:716` — `_interview_submit` current summary/evidence behavior.
  - Pattern: `src/compliance_oracle/tools/assessment.py:937` — `interview_control` mode router.
  - API/Type: `src/compliance_oracle/documentation/state.py:82` — document control write path.
  - Test: `tests/test_assessment.py` — interview mode coverage.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_assessment.py -k interview_control -q` passes.
  - [ ] `uv run pytest tests/test_assessment.py -k interview_submit -q` passes.
  - [ ] `uv run ruff check src/compliance_oracle/tools/assessment.py tests/test_assessment.py` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: interview submit hybrid happy path
    Tool: Bash
    Steps: Submit q1-q4 answers with evidence link and mocked healthy Ollama.
    Expected: Response includes documented status, evidence count, llm_used=true metadata, and policy_violation=false.
    Evidence: .sisyphus/evidence/task-T8-interview-submit-happy.txt

  Scenario: invalid mode failure path
    Tool: Bash
    Steps: Call interview_control with mode='invalid-mode'.
    Expected: Error dict states allowed values start/submit/skip.
    Evidence: .sisyphus/evidence/task-T8-interview-submit-error.txt
  ```

  **Commit**: YES | Message: `feat(assessment): add hybrid metadata to interview submit flow` | Files: `src/compliance_oracle/tools/assessment.py`, `tests/test_assessment.py`

- [ ] T9. Extend state/export metadata and documentation tool parity

  **What to do**: Add optional hybrid metadata persistence and export in `src/compliance_oracle/documentation/state.py` and `src/compliance_oracle/tools/documentation.py`, ensuring JSON/Markdown outputs include mode/degrade/policy fields when available.
  **Must NOT do**: Do not break existing export structure for clients that ignore new keys.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: persistence and export behavior affects compatibility.
  - Skills: `[]` — state and export pipeline updates.
  - Omitted: `frontend-ui-ux` — backend-only changes.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: T10, T11 | Blocked By: T1, T5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/documentation/state.py:204` — export dispatcher.
  - Pattern: `src/compliance_oracle/documentation/state.py:234` — JSON export assembly.
  - Pattern: `src/compliance_oracle/documentation/state.py:263` — Markdown export assembly.
  - API/Type: `src/compliance_oracle/tools/documentation.py:171` — `export_documentation` MCP tool.
  - API/Type: `src/compliance_oracle/models/schemas.py:150` — `ControlDocumentation` extension point.
  - Test: `tests/test_documentation.py` — existing export behavior baseline.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_documentation.py -q` passes.
  - [ ] `uv run python -c "from compliance_oracle.documentation.state import ComplianceStateManager; print('ok')"` succeeds.
  - [ ] `uv run pytest tests/test_tool_contracts.py -k export_documentation -q` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Export metadata happy path
    Tool: Bash
    Steps: Run export_documentation(format='json') after creating a documented control that includes llm_used=false and degrade_reason.
    Expected: JSON output contains metadata keys under control/export payload without removing prior keys.
    Evidence: .sisyphus/evidence/task-T9-export-metadata-happy.json

  Scenario: Backward-compatibility path
    Tool: Bash
    Steps: Export a control documented without hybrid metadata.
    Expected: Export succeeds; metadata keys are absent or null; no serialization errors.
    Evidence: .sisyphus/evidence/task-T9-export-metadata-compat.json
  ```

  **Commit**: YES | Message: `feat(documentation): export hybrid metadata with backward compatibility` | Files: `src/compliance_oracle/documentation/state.py`, `src/compliance_oracle/tools/documentation.py`, `src/compliance_oracle/models/schemas.py`, `tests/test_documentation.py`

- [ ] T4. Implement policy guard that blocks remediation language

  **What to do**: Add `src/compliance_oracle/assessment/policy.py` with deterministic checks/sanitization for forbidden recommendation patterns (e.g., "should implement", "deploy", "configure"). Apply guard to both deterministic narrative templates and LLM-enriched text outputs.
  **Must NOT do**: Do not rely on prompt-only controls; do not silently pass forbidden phrases.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: this enforces the project’s core safety principle.
  - Skills: `[]` — Regex/policy implementation only.
  - Omitted: `dev-browser` — no browser workflows.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: T5, T6, T7, T8, T11 | Blocked By: T1

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/tools/assessment.py:265` — `_generate_recommendations` currently gap-focused language baseline.
  - Pattern: `src/compliance_oracle/tools/evaluation.py:229` — finding text philosophy (no-fix rationale).
  - Pattern: `README.md` Design Philosophy section — canonical principle wording.
  - Test: `tests/test_evaluation.py` — policy-oriented assertions already present.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_assessment.py -k policy_guard -q` passes.
  - [ ] `uv run pytest tests/test_evaluation.py -k no_fix -q` passes.
  - [ ] `uv run python -c "from compliance_oracle.assessment.policy import enforce_no_fix_policy; print(enforce_no_fix_policy('You should implement MFA').policy_violation)"` prints `True`.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Allowed gap-language happy path
    Tool: Bash
    Steps: Pass text "MFA coverage beyond current scope may need assessment" into policy guard.
    Expected: Text preserved, policy_violation=false.
    Evidence: .sisyphus/evidence/task-T4-policy-happy.txt

  Scenario: Forbidden remediation failure path
    Tool: Bash
    Steps: Pass text "You should implement MFA for admins" into policy guard.
    Expected: Forbidden phrase removed or output blocked, policy_violation=true, reason includes matched rule.
    Evidence: .sisyphus/evidence/task-T4-policy-block.txt
  ```

  **Commit**: YES | Message: `feat(assessment): enforce no-fix output policy` | Files: `src/compliance_oracle/assessment/policy.py`, `tests/test_assessment.py`, `tests/test_evaluation.py`

- [ ] T5. Build deterministic-first intelligence orchestrator with hard degrade

  **What to do**: Implement `src/compliance_oracle/assessment/orchestrator.py` to execute deterministic scoring first, then optional Ollama enrichment; on client error/timeout/circuit-open, return deterministic result with stable shape and metadata (`llm_used=false`, `degrade_reason`).
  **Must NOT do**: Do not allow LLM to alter deterministic control status or control validity decisions.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: central architecture and failure semantics.
  - Skills: `[]` — standard async orchestration.
  - Omitted: `frontend-ui-ux` — not applicable.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: T6, T7, T8, T11 | Blocked By: T1, T2, T3, T4

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/tools/assessment.py:300` — deterministic assessment baseline.
  - Pattern: `src/compliance_oracle/tools/evaluation.py:270` — deterministic evaluation flow and control discovery.
  - Pattern: `src/compliance_oracle/tools/assessment.py:917` — current evaluate_response switch handling.
  - API/Type: `src/compliance_oracle/assessment/contracts.py` — contracts from T1.
  - API/Type: `src/compliance_oracle/assessment/llm/ollama_client.py` — client interface from T3.
  - API/Type: `src/compliance_oracle/assessment/policy.py` — no-fix enforcement from T4.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_assessment.py -k orchestrator -q` passes.
  - [ ] `uv run pytest tests/test_assessment.py -k degrade_reason -q` passes.
  - [ ] `uv run python -c "from compliance_oracle.assessment.orchestrator import IntelligenceOrchestrator; print('ok')"` succeeds.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Hybrid enrichment happy path
    Tool: Bash
    Steps: Run mocked orchestrator test where deterministic result is enriched by successful Ollama response.
    Expected: Output keeps deterministic status fields unchanged; llm_used=true; policy_violation=false.
    Evidence: .sisyphus/evidence/task-T5-orchestrator-happy.txt

  Scenario: Hard-degrade outage path
    Tool: Bash
    Steps: Run mocked orchestrator test where Ollama client times out.
    Expected: Output succeeds with deterministic content, llm_used=false, degrade_reason='ollama_timeout'.
    Evidence: .sisyphus/evidence/task-T5-orchestrator-degrade.txt
  ```

  **Commit**: YES | Message: `feat(assessment): add deterministic-first hybrid orchestrator` | Files: `src/compliance_oracle/assessment/orchestrator.py`, `tests/test_assessment.py`

- [ ] T6. Integrate orchestrator into `assess_control` tool path

  **What to do**: Refactor `assess_control` flow in `src/compliance_oracle/tools/assessment.py` to call orchestrator when `evaluate_response=True`, preserving backward-compatible response keys while appending metadata.
  **Must NOT do**: Do not break question-only mode (`evaluate_response=False`) and do not change tool name/arguments unless additive and backward-compatible.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: API compatibility-sensitive integration.
  - Skills: `[]` — existing pattern extension.
  - Omitted: `playwright` — backend-only.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: T11 | Blocked By: T5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/tools/assessment.py:887` — `assess_control` entrypoint.
  - Pattern: `src/compliance_oracle/tools/assessment.py:300` — deterministic evaluator logic.
  - API/Type: `src/compliance_oracle/server.py:26` — tool registration remains stable.
  - Test: `tests/test_assessment.py` — expanded assessment coverage baseline.
  - Test: `tests/test_tool_contracts.py` — response shape invariants.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_assessment.py -k assess_control -q` passes.
  - [ ] `uv run pytest tests/test_tool_contracts.py -k assess_control -q` passes.
  - [ ] `uv run ruff check src/compliance_oracle/tools/assessment.py` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: assess_control hybrid happy path
    Tool: Bash
    Steps: Invoke assess_control test with evaluate_response=true, valid response text, mocked healthy Ollama.
    Expected: Response includes maturity/gaps plus metadata (analysis_mode='hybrid', llm_used=true).
    Evidence: .sisyphus/evidence/task-T6-assess-control-happy.txt

  Scenario: assess_control missing-response failure path
    Tool: Bash
    Steps: Invoke assess_control with evaluate_response=true and no response payload.
    Expected: Error dict returned with required parameter message, no crash.
    Evidence: .sisyphus/evidence/task-T6-assess-control-error.txt
  ```

  **Commit**: YES | Message: `feat(assessment): wire hybrid orchestrator into assess_control` | Files: `src/compliance_oracle/tools/assessment.py`, `tests/test_assessment.py`, `tests/test_tool_contracts.py`

- [ ] T1. Define intelligence contracts and metadata schema

  **What to do**: Add a dedicated contract layer (`src/compliance_oracle/assessment/contracts.py`) for deterministic facts, hybrid enrichment payload, and output metadata (`analysis_mode`, `llm_used`, `degrade_reason`, `policy_violations`). Add only backward-compatible optional fields where existing schemas must expose metadata.
  **Must NOT do**: Do not remove/rename existing response fields in `AssessmentResult` or evaluation response models; do not encode remediation guidance fields.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: shared contract decisions impact multiple tools.
  - Skills: `[]` — No specialized skill required.
  - Omitted: `playwright` — No browser/UI scope.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: T5, T6, T7, T9 | Blocked By: -

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/models/schemas.py:331` — existing `AssessmentResult` contract to preserve.
  - Pattern: `src/compliance_oracle/models/schemas.py:260` — `GapAnalysisResult` style for additive schema changes.
  - API/Type: `src/compliance_oracle/tools/assessment.py:300` — `_evaluate_response` return shape.
  - API/Type: `src/compliance_oracle/tools/evaluation.py:365` — `evaluate_compliance` result assembly path.
  - Test: `tests/test_tool_contracts.py` — existing contract stability checks.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_tool_contracts.py -q` passes with unchanged existing assertions.
  - [ ] `uv run python -c "from compliance_oracle.assessment.contracts import IntelligenceResult; print('ok')"` succeeds.
  - [ ] `uv run mypy src/` reports no new type errors attributable to contract changes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Contract serialization happy path
    Tool: Bash
    Steps: Run a Python snippet constructing IntelligenceResult with llm_used=false and degrade_reason='ollama_timeout', then model_dump(mode='json').
    Expected: JSON includes analysis_mode, llm_used, degrade_reason keys and preserves existing assessment fields.
    Evidence: .sisyphus/evidence/task-T1-contract-serialize.txt

  Scenario: Contract validation failure path
    Tool: Bash
    Steps: Run a Python snippet attempting to construct contract with invalid analysis_mode='genius'.
    Expected: Validation error is raised and process exits non-zero.
    Evidence: .sisyphus/evidence/task-T1-contract-validate-error.txt
  ```

  **Commit**: YES | Message: `feat(assessment): add hybrid intelligence contracts` | Files: `src/compliance_oracle/assessment/contracts.py`, `src/compliance_oracle/models/schemas.py`, `tests/test_tool_contracts.py`

- [ ] T2. Implement hybrid runtime configuration and hard-degrade policy switches

  **What to do**: Add a runtime configuration module (`src/compliance_oracle/assessment/config.py`) with explicit settings for `intelligence_mode`, `ollama_base_url`, `ollama_model`, timeout budget, and `hard_degrade=true` semantics. Wire non-invasive loading into tool/orchestrator entry points.
  **Must NOT do**: Do not hardcode model names inside business logic; do not create settings that allow remediation generation.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: cross-cutting config behavior with low algorithmic complexity.
  - Skills: `[]` — No special skill dependency.
  - Omitted: `frontend-ui-ux` — not relevant.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: T3, T5, T11, T12 | Blocked By: -

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/server.py:24` — registration path where runtime config is eventually consumed.
  - Pattern: `src/compliance_oracle/tools/assessment.py:847` — assessment tool registration entry.
  - Pattern: `src/compliance_oracle/tools/evaluation.py:448` — evaluation tool registration entry.
  - Pattern: `src/compliance_oracle/cli.py:17` — CLI bootstrap conventions for config-aware commands.
  - External: `https://github.com/ollama/ollama/blob/main/docs/api.md` — local API contract.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run python -c "from compliance_oracle.assessment.config import load_intelligence_config; print(load_intelligence_config().intelligence_mode)"` succeeds.
  - [ ] `uv run pytest tests/test_assessment.py -k config -q` passes.
  - [ ] `uv run ruff check src/compliance_oracle/assessment/config.py` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Default config happy path
    Tool: Bash
    Steps: Run Python snippet with no env vars; print config fields.
    Expected: intelligence_mode resolves to hybrid, hard_degrade resolves true, ollama_base_url defaults to local endpoint.
    Evidence: .sisyphus/evidence/task-T2-config-defaults.txt

  Scenario: Invalid mode failure path
    Tool: Bash
    Steps: Set env INTELLIGENCE_MODE=invalid and run loader.
    Expected: Loader raises descriptive validation error; process exits non-zero.
    Evidence: .sisyphus/evidence/task-T2-config-invalid-mode.txt
  ```

  **Commit**: YES | Message: `feat(assessment): add hybrid runtime configuration` | Files: `src/compliance_oracle/assessment/config.py`, `tests/test_assessment.py`

- [ ] T3. Add Ollama adapter with timeout and circuit-breaker behavior

  **What to do**: Implement `src/compliance_oracle/assessment/llm/ollama_client.py` wrapper with strict timeout, structured response parsing, and circuit-breaker state for repeated transport failures. Expose typed result object consumable by orchestrator.
  **Must NOT do**: Do not call Ollama directly from tool modules; do not swallow errors without structured error codes.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: resilience behavior and failure handling are core architecture concerns.
  - Skills: `[]` — Standard Python async + http client patterns.
  - Omitted: `playwright` — non-UI backend task.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: T5, T11 | Blocked By: T2

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/tools/framework_mgmt.py:260` — existing `httpx.AsyncClient` usage style.
  - Pattern: `src/compliance_oracle/tools/framework_mgmt.py:274` — HTTP error handling style.
  - API/Type: `src/compliance_oracle/tools/assessment.py:300` — caller expects typed assessment outcomes.
  - API/Type: `src/compliance_oracle/tools/evaluation.py:270` — async evaluation orchestration context.
  - External: `https://github.com/ollama/ollama/blob/main/docs/api.md` — `/api/generate` request/response format.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_assessment.py -k ollama_client -q` passes.
  - [ ] `uv run python -c "import asyncio; from compliance_oracle.assessment.llm.ollama_client import OllamaClient; print('ok')"` succeeds.
  - [ ] `uv run mypy src/compliance_oracle/assessment/llm/ollama_client.py` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Healthy Ollama response path
    Tool: Bash
    Steps: Run pytest case with mocked Ollama 200 JSON payload containing response text and done=true.
    Expected: Client returns parsed payload with status='ok' and preserves raw model name.
    Evidence: .sisyphus/evidence/task-T3-ollama-happy.txt

  Scenario: Timeout/degrade failure path
    Tool: Bash
    Steps: Run pytest case with simulated timeout and repeated transport errors.
    Expected: Circuit opens after threshold, client returns structured error code, no uncaught exception escapes.
    Evidence: .sisyphus/evidence/task-T3-ollama-timeout.txt
  ```

  **Commit**: YES | Message: `feat(assessment): add resilient ollama client adapter` | Files: `src/compliance_oracle/assessment/llm/ollama_client.py`, `tests/test_assessment.py`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Commit per task or tightly-coupled task pair to keep reverts low-risk.
- Conventional commits:
  - `feat(assessment): add hybrid orchestrator with ollama hard-degrade`
  - `feat(cli): add export command for markdown/json`
  - `test(assessment): add hybrid parity and outage coverage`
  - `docs(assessment): add hybrid mode runbook and limitations`
- Do not bundle unrelated framework-onboarding or renderer work.

## Success Criteria
- Hybrid mode is available and default-capable with local Ollama.
- Deterministic-only behavior remains fully functional under Ollama outage.
- Outputs remain gap-focused and remediation-free under all modes.
- Tool/API contracts remain stable for existing MCP consumers.
- Evidence demonstrates parity, outage handling, and policy guard enforcement.
- Deferred LaTeX follow-on is fully specified for next plan without implementation bleed.

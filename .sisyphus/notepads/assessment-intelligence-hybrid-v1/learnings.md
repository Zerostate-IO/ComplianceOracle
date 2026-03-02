# Learnings: T2 - Hybrid Runtime Configuration

## 2026-03-01

### Project Conventions
- All Pydantic models use `Field()` with descriptions for documentation
- Config models should be frozen/immutable (`model_config = {"frozen": True}`)
- Environment variables use `INTELLIGENCE_` or `OLLAMA_` prefixes
- Config loading should be side-effect free

### Implementation Patterns
- `Literal["deterministic", "hybrid"]` for mode type alias (not StrEnum)
- `field_validator` for enforcing constraints like `hard_degrade` always True
- Helper functions `_get_env_str`, `_get_env_int`, `_get_env_float` for clean env parsing
- Frozen config ensures immutability across the application

### Key Constraints
- `hard_degrade` MUST always be True - core project principle
- System never generates remediation suggestions - only identifies gaps
- Config should be loadable without requiring files (env vars only)

### Test Patterns
- Use `monkeypatch` fixture for environment variable testing
- Test both default values and env override behavior
- Test validation errors for invalid inputs
# Task T1: Intelligence Contracts - Learnings

## Date: 2026-03-01

### Pydantic Forward References
- When adding optional fields that reference types from other modules, use direct imports rather than TYPE_CHECKING
- Pydantic 2.x requires `model_rebuild()` if using forward references via TYPE_CHECKING, but direct imports work without rebuilding
- The error `PydanticUserError: 'Model' is not fully defined` indicates a forward reference issue

### Pattern for Adding Optional Fields
```python
# Instead of TYPE_CHECKING approach:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from other_module import OtherType

# Use direct import:
from other_module import OtherType

class MyModel(BaseModel):
    optional_field: OtherType | None = Field(default=None)
```

### Contract Design Principles
1. All new fields should be optional with defaults to maintain backward compatibility
2. Use StrEnum for structured error codes (DegradeReason) to enable programmatic handling
3. Helper functions (create_deterministic_metadata, create_hybrid_metadata, create_degraded_metadata) improve ergonomics
4. IntelligenceResult as a base class with convenience methods (get_analysis_mode, is_llm_used, etc.)

### Test Contract Patterns
- Test enum values explicitly to catch typos
- Test both with and without metadata for backward compatibility
- Test serialization with model_dump(mode='json') for JSON output verification
- Test validation errors for invalid enum values

### File Structure Created
```
src/compliance_oracle/assessment/
├── __init__.py      # Exports all public symbols
├── config.py        # Pre-existing: IntelligenceConfig
└── contracts.py     # New: IntelligenceMode, DegradeReason, IntelligenceMetadata, IntelligenceResult
```

### Key Integration Points
- AssessmentResult in schemas.py now has optional `metadata: IntelligenceMetadata | None`
- No changes required to existing tools - metadata is completely optional
- Future tasks (T5, T6, T7, T9) will integrate metadata into actual tool responses

## 2026-03-01 (T4 - Policy Guard)

### Implementation Patterns
- Regex-only pattern matching for forbidden phrases (no NLP/ML)
- Use `re.IGNORECASE` for case-insensitive matching
- Group patterns by category (imperative, prescriptive, second-person, fix-oriented, solution)
- Store compiled patterns in `Final[list[re.Pattern[str]]]` for performance

### Policy Design
- `PolicyResult` model includes: original_text, sanitized_text, policy_violation, violations
- Sanitization replaces forbidden phrases with neutral/gap-focused language
- Empty/whitespace-only text returns no violation
- Violations list contains normalized (lowercase) matched phrases

### Pattern Categories
- Imperative: "should implement", "must deploy", "need to configure"
- Prescriptive: "we recommend", "it is recommended", "recommend enabling"
- Second-person: "you should", "you must", "you need to"
- Fix-oriented: "to fix this", "to address this gap", "remediation step"
- Solution: "the solution is", "consider implementing"

### Test Coverage
- Test allowed gap-language passes unchanged
- Test forbidden language detected and flagged
- Test multiple violations in same text
- Test sanitization produces gap-focused output
- Test edge cases: empty text, whitespace, no violations, only violations
- Test case-insensitive detection
- Test integration with evaluation outputs

### Key Constraints
- Only regex-based detection (no ML/NLP dependencies)
- Preserve legitimate gap-identification language
- Structured results for programmatic handling

## 2026-03-01 (T3 - Ollama Client)

### Implementation Patterns
- Use `asyncio.timeout()` for strict timeout enforcement (not httpx timeout alone)
- httpx timeout should be slightly longer than asyncio timeout to avoid double-timeout issues
- Use `time.monotonic()` for circuit-breaker timing (not `time.time()`)
- Store circuit state as `tuple[bool, int, float | None]` for external inspection

### Circuit-Breaker Design
- Track `_consecutive_failures: int` and `_circuit_open_until: float | None`
- Check `_is_circuit_open()` before making network requests
- Reset failure count on success, increment on any error
- Circuit auto-closes when `time.monotonic() >= _circuit_open_until`
- Expose `reset_circuit()` for manual/administrative intervention

### Error Mapping to DegradeReason
- `TimeoutError` -> `OLLAMA_TIMEOUT`
- `httpx.ConnectError` -> `OLLAMA_UNREACHABLE`
- `httpx.HTTPError` (other) -> `OLLAMA_UNREACHABLE`
- HTTP status >= 400 -> `OLLAMA_UNREACHABLE`
- JSON parse error -> `OLLAMA_MALFORMED_RESPONSE`
- Missing 'response' field -> `OLLAMA_MALFORMED_RESPONSE`
- Circuit open (no network call) -> `CIRCUIT_OPEN`

### Test Patterns
- Use `pytest-httpx` for mocking httpx requests
- Use `httpx_mock.add_exception()` for connection errors
- Use `httpx_mock.add_callback()` for delayed/timed responses
- Mock only the number of responses that will actually be used (circuit blocks extra calls)
- Use `httpx_mock.get_requests()` to verify no network calls made
- Respect config constraints (timeout >= 1.0, reset_seconds >= 10.0)

### OllamaResult Model
- Use `Literal["ok", "timeout", "error", "circuit_open"]` for status type
- All fields use `Field()` with descriptions
- `content: str | None` - only populated on success
- `error_code: DegradeReason | None` - structured error for programmatic handling
- `latency_ms: int` - always present, even for errors
- `model: str | None` - preserves Ollama model name on success
- Compatible with DegradeReason.POLICY_VIOLATION

## 2026-03-01 (T9 - Export Metadata Parity)

### Implementation Patterns
- Add optional metadata fields to Pydantic models with `Field(default=None)`
- For JSON export, use `model_dump(mode="json")` and pop None values to maintain backward compatibility
- For Markdown export, check `if doc.intelligence_metadata is not None` before adding section
- Metadata section should include only non-None optional fields

### Backward Compatibility Strategy
- JSON export: Pop `intelligence_metadata` key when value is None (line ~255)
- Markdown export: Only add "Analysis Metadata" section when metadata exists
- Tests verify both "with metadata" and "without metadata" paths

### Test Patterns
- Test JSON export with metadata includes the key
- Test JSON export without metadata excludes the key (backward compat)
- Test Markdown export with metadata includes the section
- Test Markdown export without metadata excludes the section
- Test minimal metadata (only required fields) and full metadata (all fields)
- Test persistence to state.json file

### Files Modified
- `src/compliance_oracle/models/schemas.py` - Added `intelligence_metadata: IntelligenceMetadata | None` to ControlDocumentation
- `src/compliance_oracle/documentation/state.py` - Updated `_export_json` and `_export_markdown` to handle metadata
- `tests/test_documentation.py` - Added 14 new tests for metadata export

### Key Constraints
- Metadata is completely optional - exports work without it
- Never require metadata for export to succeed
- Maintain existing field names and types for backward compatibility
- Never require metadata for export to succeed
- Maintain existing field names and types for backward compatibility

## 2026-03-01 (T6 - Orchestrator Integration into assess_control)

### Implementation Patterns
- Import orchestrator components at module level: `IntelligenceConfig`, `IntelligenceOrchestrator`, `OllamaClient`
- Create fresh config and client instances inside the tool function when `evaluate_response=True`
- Build context dict with `control_name` and `framework_id` from control details
- Call `orchestrator.assess(control_id, response, context)` instead of direct deterministic logic
- Map OrchestratorResult fields to response dict preserving all existing keys

### Backward Compatibility Strategy
- All existing response fields preserved: control_id, control_name, framework_id, maturity_level, strengths, gaps, recommendations
- New metadata fields added: analysis_mode, llm_used, degrade_reason
- Optional LLM enrichment fields only added when present: llm_rationale, llm_context, policy_violations, latency_ms
- Question-only mode (`evaluate_response=False`) completely unchanged

### Control Not Found Handling
- Check control_details before creating orchestrator
- Return error dict with all expected fields on not found: error, control_id, control_name, framework_id, maturity_level, strengths, gaps, recommendations

### Test Patterns
- Test metadata fields are present in response
- Test deterministic-only mode works when Ollama unavailable (mock OllamaClient to fail)
- Test control not found returns error dict
- Test question-only mode unchanged (existing test)
- Test missing response returns error (existing test)

### Files Modified
- `src/compliance_oracle/tools/assessment.py` - Added imports, modified assess_control function
- `tests/test_assessment.py` - Added 3 new tests for orchestrator integration

### Key Constraints
- LLM can NEVER change deterministic control status or gap detection
- Orchestrator always runs deterministic assessment first
- Hard-degrade on any LLM failure returns deterministic result with metadata
- Tool name and arguments unchanged for MCP compatibility


## 2026-03-01 (T8 - Interview Submit with Hybrid Metadata)

### Implementation Patterns
- Use the same orchestrator integration pattern from T6 in `_interview_submit`
- Create config, client, orchestrator inside the submit function
- Build context dict with `control_name` and `framework_id` from control details
- Call `orchestrator.assess(control_id, response, context)` for hybrid enrichment
- Use orchestrator's maturity assessment (more accurate than local heuristic)
- Extract strengths, gaps, recommendations from orchestrator result
- Use LLM-enriched rationale/context when available for implementation summary

### Metadata Fields Added to Submit Response
- `analysis_mode`: "deterministic" or "hybrid" from orchestrator metadata
- `llm_used`: boolean indicating if LLM enrichment was successful
- `degrade_reason`: DegradeReason enum or None if no degradation
- Optional: `llm_rationale`, `llm_context`, `policy_violations`, `latency_ms`

### Backward Compatibility Strategy
- All existing response fields preserved: control_id, status, recorded, evidence_linked, assessed_maturity, follow_up_recommendations
- New metadata fields added at response root level
- `start` and `skip` modes completely unchanged (no Ollama required)
- Only `submit` mode uses orchestrator for enrichment

### Recorded Details Enhancement
- Added `strengths` to recorded dict if present from orchestrator
- Added `gaps` to recorded dict if present from orchestrator
- Implementation summary uses LLM-enriched text when available

### Test Patterns
- Test metadata fields are present in submit response
- Test deterministic-only mode works when Ollama unavailable (mock OllamaClient)
- Test start and skip modes unchanged (existing tests)
- Test invalid mode error handling (existing test)

### Files Modified
- `src/compliance_oracle/tools/assessment.py` - Modified `_interview_submit` function
- `tests/test_assessment.py` - Added 2 new tests for submit with metadata

### Key Constraints
- Policy guard applied automatically by orchestrator via `enforce_no_fix_policy`
- LLM can NEVER change deterministic maturity level or status
- Only enrichment text (rationale, context) can be modified by LLM
- Hard-degrade on any LLM failure returns deterministic result with metadata

## 2026-03-01 (T13 - LaTeX Reporting Spec)

### Spec Document Patterns
- Use "Deferred" status prominently at document top
- Include explicit "No implementation" statement to prevent scope creep
- Define data contract referencing actual source files with line numbers
- Include acceptance gates as checklist format for future verification
- Add non-goals section to document what is explicitly out of scope

### Documentation Structure
- Six core sections: Scope, Data Contract, Template Contract, Non-Goals, Acceptance Gates, Implementation Notes
- Appendices for examples and configuration schemas
- Entry criteria section links to roadmap prerequisites
- Risk factors section documents known challenges

### Cross-Reference Pattern
- Add deferred specs to README roadmap as new subsection
- Use table format with Spec link, Title, Description, Target columns
- Place after Enhancement Epics, before Version Milestones

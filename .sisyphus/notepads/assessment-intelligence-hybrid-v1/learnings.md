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

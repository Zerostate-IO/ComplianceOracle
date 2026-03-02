# Hybrid Operations Runbook

This document describes how to operate ComplianceOracle in hybrid mode with local LLM
enrichment via Ollama. It covers installation, configuration, behavior semantics, and
troubleshooting.

## Overview

ComplianceOracle supports two intelligence modes:

| Mode | Description | LLM Required |
|------|-------------|--------------|
| `deterministic` | Pure rule-based assessment using keyword matching and heuristics | No |
| `hybrid` | Deterministic assessment first, then optional LLM enrichment for rationale/context | Yes (Ollama) |

In hybrid mode, the system **always** runs deterministic assessment first. The LLM can only
add enrichment text like rationale and context. It can never change control status, maturity
levels, or gap detection results.

## Quick Start

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com/download](https://ollama.com/download)

### 2. Start Ollama Server

```bash
ollama serve
```

This starts the Ollama API server at `http://localhost:11434` by default.

### 3. Pull a Model

```bash
ollama pull llama3.2
```

See [Model Selection](#model-selection) for recommendations.

### 4. Configure ComplianceOracle

Set environment variables (optional, defaults work for local setup):

```bash
export INTELLIGENCE_MODE=hybrid
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2
```

### 5. Verify Setup

Run a test assessment to confirm hybrid mode is working:

```bash
uv run python -c "
import asyncio
from compliance_oracle.assessment.config import load_intelligence_config
from compliance_oracle.assessment.orchestrator import IntelligenceOrchestrator
from compliance_oracle.assessment.llm.ollama_client import OllamaClient

async def test():
    config = load_intelligence_config()
    print(f'Mode: {config.intelligence_mode}')
    print(f'Model: {config.ollama_model}')
    
    client = OllamaClient(config)
    orchestrator = IntelligenceOrchestrator(config, client)
    
    result = await orchestrator.assess(
        control_id='PR.AC-01',
        response='We use multi-factor authentication for all users.'
    )
    print(f'LLM used: {result.is_llm_used}')
    print(f'Degrade reason: {result.degrade_reason}')

asyncio.run(test())
"
```

Expected output when Ollama is running:
```
Mode: hybrid
Model: llama3.2
LLM used: True
Degrade reason: None
```

## Model Selection

### Recommended Models

| Model | Size | Best For | Notes |
|-------|------|----------|-------|
| `llama3.2` | 2GB | General compliance assessment | Default, good balance of speed and quality |
| `llama3.2:1b` | 1.3GB | Fast assessments on limited hardware | Faster but less nuanced |
| `mistral` | 4.1GB | Higher quality rationale | Better for detailed compliance analysis |
| `phi3` | 2.2GB | Resource-constrained environments | Small but capable |

### Model Requirements

For compliance assessment work:
- Minimum: 2GB VRAM or 4GB RAM for CPU inference
- Recommended: 4GB+ VRAM for responsive assessments
- The model only generates rationale/context text, not complex reasoning

### Pulling Models

```bash
# Default model
ollama pull llama3.2

# Smaller variant
ollama pull llama3.2:1b

# Alternative models
ollama pull mistral
ollama pull phi3
```

### Switching Models

Set the `OLLAMA_MODEL` environment variable:

```bash
export OLLAMA_MODEL=mistral
```

Or pass directly when loading config (for programmatic use).

## Timeout Tuning

### Environment Variables

| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `OLLAMA_TIMEOUT_BUDGET` | 30.0 | 1.0-300.0 | Maximum seconds to wait for LLM response |
| `OLLAMA_CIRCUIT_BREAKER_THRESHOLD` | 3 | 1-10 | Consecutive failures before circuit opens |
| `OLLAMA_CIRCUIT_BREAKER_RESET` | 60.0 | 10.0-600.0 | Seconds to wait before retrying after circuit opens |

### Tuning Guidance

**Slow Hardware:**
```bash
export OLLAMA_TIMEOUT_BUDGET=60.0
```

**Fast GPU:**
```bash
export OLLAMA_TIMEOUT_BUDGET=15.0
```

**Unstable Network (Ollama on remote host):**
```bash
export OLLAMA_CIRCUIT_BREAKER_THRESHOLD=5
export OLLAMA_CIRCUIT_BREAKER_RESET=120.0
```

### Timeout Behavior

When a timeout occurs:
1. The circuit-breaker failure count increments
2. The system returns deterministic results immediately
3. Metadata shows `degrade_reason: "timeout"`
4. No error is raised to the caller

## Hard-Degrade Semantics

The `hard_degrade` flag is **always True** and cannot be disabled. This is a core project
principle enforced at the configuration level.

### What This Means

On any LLM failure (timeout, unreachable, malformed response, circuit open):
1. **Assessment continues** with deterministic-only results
2. **No exceptions escape** to the caller
3. **Metadata captures** the failure reason for audit

### Response Shape (Always Consistent)

```json
{
  "control_id": "PR.AC-01",
  "control_name": "Identity and Access Control",
  "maturity_level": "intermediate",
  "strengths": ["MFA mentioned"],
  "gaps": ["No SSO coverage"],
  "recommendations": ["Review SSO implementation"],
  "llm_rationale": null,
  "llm_context": null,
  "metadata": {
    "llm_used": false,
    "degrade_reason": "timeout",
    "latency_ms": 30005
  }
}
```

The response always contains all deterministic fields. LLM enrichment fields are `null`
when degraded.

### Degrade Reasons

| Reason | Description |
|--------|-------------|
| `timeout` | LLM response exceeded timeout budget |
| `ollama_unreachable` | Could not connect to Ollama server |
| `ollama_malformed_response` | Ollama returned invalid JSON |
| `circuit_open` | Circuit-breaker blocked the request |
| `policy_violation` | Output blocked by no-fix policy (rare) |

## Deterministic Boundary

The LLM has strict boundaries on what it can and cannot modify.

### LLM Can Modify

- `llm_rationale`: Explanation of why the maturity level was assigned
- `llm_context`: Additional relevant context about the assessment

### LLM Cannot Modify (Enforced)

- `maturity_level`: Always from deterministic keyword analysis
- `strengths`: Always from deterministic pattern matching
- `gaps`: Always from deterministic gap detection
- `recommendations`: Always generated from gaps (gap-focused, not prescriptive)
- `control_id`, `control_name`, `framework_id`: Structural metadata

### Implementation

The orchestrator enforces this by:
1. Running deterministic assessment **first**
2. Building an LLM prompt that explicitly states what deterministic analysis found
3. Instructing the LLM to only provide rationale/context
4. Ignoring any LLM output that attempts to change deterministic fields

## No-Fix Policy Enforcement

All LLM output passes through the `enforce_no_fix_policy` function before being returned.

### Forbidden Patterns (60+ patterns)

The policy guard blocks phrases like:

| Category | Examples |
|----------|----------|
| Imperative | "should implement", "must deploy", "need to configure" |
| Prescriptive | "we recommend", "it is recommended", "recommend enabling" |
| Second-person | "you should", "you must", "you need to" |
| Fix-oriented | "to fix this", "remediation step", "address the gap" |
| Solution | "the solution is", "consider implementing", "consider deploying" |

### What Passes

Gap-identification language is always allowed:
- "This gap indicates a lack of MFA for service accounts"
- "No evidence of encryption at rest was found"
- "The current implementation does not address X"

### Sanitization

When violations are detected:
1. Forbidden phrases are replaced with neutral language
2. Original violations are logged in `metadata.policy_violations`
3. Sanitized text is returned to the user

### Example

**LLM Output (blocked):**
```
You should implement MFA for all service accounts to fix this gap.
```

**Sanitized Output:**
```
It would be appropriate to implementation of MFA for all service accounts regarding this gap.
```

## Circuit-Breaker Behavior

The Ollama client includes a circuit-breaker to prevent cascading failures.

### How It Works

1. Track consecutive failures
2. After `threshold` failures, open the circuit
3. While open, return `circuit_open` immediately (no network call)
4. After `reset_seconds`, attempt to close (allow one request)
5. On success, close circuit; on failure, stay open

### Default Configuration

```python
circuit_breaker_threshold = 3      # Open after 3 failures
circuit_breaker_reset_seconds = 60.0  # Try again after 60 seconds
```

### Manual Reset

For administrative intervention, the circuit can be reset programmatically:

```python
from compliance_oracle.assessment.llm.ollama_client import OllamaClient

client = OllamaClient(config)
client.reset_circuit()  # Force circuit closed
```

## Troubleshooting

### Ollama Not Running

**Symptoms:**
- `degrade_reason: "ollama_unreachable"`
- `llm_used: false` on every request

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

### Model Not Pulled

**Symptoms:**
- `degrade_reason: "ollama_unreachable"` or HTTP 404

**Solution:**
```bash
# List available models
ollama list

# Pull the model
ollama pull llama3.2
```

### Slow Responses

**Symptoms:**
- `degrade_reason: "timeout"` frequently
- Assessments take >30 seconds

**Solutions:**
```bash
# Increase timeout
export OLLAMA_TIMEOUT_BUDGET=60.0

# Or use a smaller model
export OLLAMA_MODEL=llama3.2:1b
```

### Circuit Stuck Open

**Symptoms:**
- `degrade_reason: "circuit_open"` repeatedly
- No network calls to Ollama

**Solution:**
```bash
# Wait for reset (60 seconds by default)
# Or restart the application to reset circuit
```

### High Memory Usage

**Symptoms:**
- System becomes unresponsive during assessments
- OOM errors

**Solutions:**
```bash
# Use smaller model
ollama pull llama3.2:1b
export OLLAMA_MODEL=llama3.2:1b

# Or run deterministic-only mode
export INTELLIGENCE_MODE=deterministic
```

### Policy Violations in Output

**Symptoms:**
- `metadata.policy_violations` contains entries
- Output seems sanitized/unusual

**Solution:**
This is expected behavior. The policy guard blocks prescriptive language.
Check `policy_violations` in metadata to see what was blocked.

### Ollama on Remote Host

**Configuration:**
```bash
export OLLAMA_BASE_URL=http://remote-host:11434
export OLLAMA_TIMEOUT_BUDGET=45.0  # Account for network latency
export OLLAMA_CIRCUIT_BREAKER_THRESHOLD=5  # More tolerant of transient failures
```

## Operating in Deterministic-Only Mode

If you don't want LLM enrichment:

```bash
export INTELLIGENCE_MODE=deterministic
```

Or don't install/configure Ollama at all. The system will automatically operate in
deterministic mode when no Ollama client is available.

## Reference: Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INTELLIGENCE_MODE` | `hybrid` | `deterministic` or `hybrid` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Model name for assessments |
| `OLLAMA_TIMEOUT_BUDGET` | `30.0` | Max seconds for LLM response |
| `OLLAMA_CIRCUIT_BREAKER_THRESHOLD` | `3` | Failures before circuit opens |
| `OLLAMA_CIRCUIT_BREAKER_RESET` | `60.0` | Seconds before circuit retry |

## Reference: Response Metadata Schema

```python
class IntelligenceMetadata(BaseModel):
    llm_used: bool                          # True if LLM enrichment succeeded
    degrade_reason: DegradeReason | None    # Why degradation occurred (if any)
    analysis_mode: str                      # "deterministic" or "hybrid"
    policy_violations: list[str] | None     # Blocked phrases (if any)
    latency_ms: int                         # Total assessment time
```

## Related Documentation

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Project README](../README.md) - Core design philosophy
- [AGENTS.md](../AGENTS.md) - Agent configuration

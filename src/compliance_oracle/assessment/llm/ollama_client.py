"""Resilient Ollama API client with timeout and circuit-breaker behavior.

This module provides a typed client for communicating with Ollama's /api/generate
endpoint. It enforces strict timeouts and implements circuit-breaker semantics
to gracefully degrade when the LLM backend is unavailable or slow.

Design principles:
- All errors are captured as structured error codes, never raised as exceptions
- Circuit-breaker prevents cascading failures during outages
- Timeout enforcement uses asyncio.timeout for precise control
- Error codes map directly to DegradeReason for orchestrator consumption
"""

from __future__ import annotations

import asyncio
import time
from typing import Literal

import httpx
from pydantic import BaseModel, Field

from compliance_oracle.assessment.config import IntelligenceConfig
from compliance_oracle.assessment.contracts import DegradeReason

# Status type for OllamaResult
OllamaStatus = Literal["ok", "timeout", "error", "circuit_open"]


class OllamaResult(BaseModel):
    """Result of an Ollama API call.

    This model captures the outcome of a generate() call, including
    successful responses, timeouts, errors, and circuit-open states.
    It is designed to be consumed by the assessment orchestrator
    without requiring exception handling.

    Attributes:
        status: The outcome status of the API call.
        content: The generated text if status is 'ok', None otherwise.
        error_code: Structured error code mapping to DegradeReason if applicable.
        latency_ms: The request latency in milliseconds.
        model: The model name returned by Ollama (if available).
    """

    status: OllamaStatus = Field(
        description="The outcome status: 'ok', 'timeout', 'error', or 'circuit_open'",
    )
    content: str | None = Field(
        default=None,
        description="The generated text if status is 'ok', None otherwise",
    )
    error_code: DegradeReason | None = Field(
        default=None,
        description="Structured error code mapping to DegradeReason if applicable",
    )
    latency_ms: int = Field(
        description="The request latency in milliseconds",
    )
    model: str | None = Field(
        default=None,
        description="The model name returned by Ollama (if available)",
    )


class OllamaClient:
    """Resilient client for Ollama API with timeout and circuit-breaker.

    This client wraps the Ollama /api/generate endpoint with:
    - Strict timeout enforcement using asyncio.timeout
    - Circuit-breaker pattern to prevent cascading failures
    - Structured error codes for graceful degradation

    Circuit-breaker behavior:
    - Tracks consecutive failures
    - Opens circuit after threshold failures
    - Resets circuit after reset_seconds have elapsed
    - Returns circuit_open status without making requests when open

    Example:
        config = IntelligenceConfig()
        client = OllamaClient(config)
        result = await client.generate("Analyze this control...")
        if result.status == "ok":
            print(result.content)
        else:
            print(f"Degraded: {result.error_code}")
    """

    def __init__(self, config: IntelligenceConfig) -> None:
        """Initialize the Ollama client with configuration.

        Args:
            config: IntelligenceConfig with timeout, circuit-breaker, and
                    Ollama connection settings.
        """
        self._config = config
        self._base_url = config.ollama_base_url.rstrip("/")
        self._model = config.ollama_model
        self._timeout_seconds = config.timeout_budget_seconds
        self._circuit_threshold = config.circuit_breaker_threshold
        self._circuit_reset_seconds = config.circuit_breaker_reset_seconds

        # Circuit-breaker state
        self._consecutive_failures: int = 0
        self._circuit_open_until: float | None = None

    def _is_circuit_open(self) -> bool:
        """Check if the circuit-breaker is currently open.

        Returns:
            True if circuit is open (requests should be blocked),
            False if circuit is closed (requests can proceed).
        """
        if self._circuit_open_until is None:
            return False

        # Check if reset period has elapsed
        if time.monotonic() >= self._circuit_open_until:
            # Reset the circuit
            self._circuit_open_until = None
            self._consecutive_failures = 0
            return False

        return True

    def _record_failure(self) -> None:
        """Record a failure and potentially open the circuit."""
        self._consecutive_failures += 1

        if self._consecutive_failures >= self._circuit_threshold:
            # Open the circuit
            self._circuit_open_until = time.monotonic() + self._circuit_reset_seconds

    def _record_success(self) -> None:
        """Record a success and reset the failure counter."""
        self._consecutive_failures = 0
        self._circuit_open_until = None

    async def generate(self, prompt: str) -> OllamaResult:
        """Generate text from Ollama with timeout and circuit-breaker protection.

        This method makes a request to Ollama's /api/generate endpoint with
        stream=false. It enforces the configured timeout and respects the
        circuit-breaker state.

        Args:
            prompt: The prompt to send to Ollama.

        Returns:
            OllamaResult with:
            - status='ok' and content populated on success
            - status='circuit_open' if circuit-breaker is open
            - status='timeout' if request exceeded timeout
            - status='error' with error_code for other failures
        """
        # Check circuit-breaker first
        if self._is_circuit_open():
            return OllamaResult(
                status="circuit_open",
                error_code=DegradeReason.CIRCUIT_OPEN,
                latency_ms=0,
            )

        start_time = time.monotonic()

        try:
            async with asyncio.timeout(self._timeout_seconds):
                async with httpx.AsyncClient(
                    timeout=self._timeout_seconds + 1.0,  # Slightly longer than asyncio timeout
                ) as client:
                    response = await client.post(
                        f"{self._base_url}/api/generate",
                        json={
                            "model": self._model,
                            "prompt": prompt,
                            "stream": False,
                        },
                    )

                    latency_ms = int((time.monotonic() - start_time) * 1000)

                    # Check for HTTP errors
                    if response.status_code >= 400:
                        self._record_failure()
                        return OllamaResult(
                            status="error",
                            error_code=DegradeReason.OLLAMA_UNREACHABLE,
                            latency_ms=latency_ms,
                        )

                    # Parse JSON response
                    try:
                        data = response.json()
                    except Exception:
                        self._record_failure()
                        return OllamaResult(
                            status="error",
                            error_code=DegradeReason.OLLAMA_MALFORMED_RESPONSE,
                            latency_ms=latency_ms,
                        )

                    # Check for error in response body
                    if "error" in data:
                        self._record_failure()
                        return OllamaResult(
                            status="error",
                            error_code=DegradeReason.OLLAMA_UNREACHABLE,
                            latency_ms=latency_ms,
                        )

                    # Extract response content
                    content = data.get("response")
                    if content is None:
                        self._record_failure()
                        return OllamaResult(
                            status="error",
                            error_code=DegradeReason.OLLAMA_MALFORMED_RESPONSE,
                            latency_ms=latency_ms,
                        )

                    # Success
                    self._record_success()
                    return OllamaResult(
                        status="ok",
                        content=content,
                        latency_ms=latency_ms,
                        model=data.get("model"),
                    )

        except TimeoutError:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            self._record_failure()
            return OllamaResult(
                status="timeout",
                error_code=DegradeReason.OLLAMA_TIMEOUT,
                latency_ms=latency_ms,
            )

        except httpx.ConnectError:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            self._record_failure()
            return OllamaResult(
                status="error",
                error_code=DegradeReason.OLLAMA_UNREACHABLE,
                latency_ms=latency_ms,
            )

        except httpx.HTTPError:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            self._record_failure()
            return OllamaResult(
                status="error",
                error_code=DegradeReason.OLLAMA_UNREACHABLE,
                latency_ms=latency_ms,
            )

    @property
    def circuit_state(self) -> tuple[bool, int, float | None]:
        """Get the current circuit-breaker state.

        Returns:
            Tuple of (is_open, consecutive_failures, open_until_timestamp).
            open_until_timestamp is None if circuit is closed.
        """
        return (
            self._is_circuit_open(),
            self._consecutive_failures,
            self._circuit_open_until,
        )

    def reset_circuit(self) -> None:
        """Manually reset the circuit-breaker.

        This is primarily useful for testing or administrative intervention.
        """
        self._consecutive_failures = 0
        self._circuit_open_until = None

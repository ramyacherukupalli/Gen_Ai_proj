"""LLM provider adapter for Gemini and Groq-backed note generation."""

from typing import Any

from google import genai

from app.config import settings

try:  # pragma: no cover - exercised when Groq dependency is installed.
    from groq import Groq
except Exception:  # pragma: no cover - Groq is optional in the base runtime.
    Groq = None


class ProviderConfigurationError(RuntimeError):
    """Raised when the active provider cannot be configured."""


class ProviderResponseError(RuntimeError):
    """Raised when the provider returns no usable text response."""


class LLMProviderError(RuntimeError):
    """Raised when the provider request itself fails."""


class GeminiLLMService:
    """Small adapter around the supported text-generation SDKs."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key
        self._client = client
        self._provider = self._detect_provider()
        self._model = model or (
            settings.groq_model if self._provider == "groq" else settings.gemini_model
        )

    def _detect_provider(self) -> str:
        if self._client is not None:
            if hasattr(self._client, "chat") and hasattr(self._client.chat, "completions"):
                return "groq"
            if hasattr(self._client, "models") and hasattr(self._client.models, "generate_content"):
                return "gemini"

        if self._api_key and self._api_key == settings.groq_api_key:
            return "groq"
        if self._api_key and self._api_key == settings.gemini_api_key:
            return "gemini"

        if settings.groq_api_key and not settings.gemini_api_key:
            return "groq"
        if settings.gemini_api_key and not settings.groq_api_key:
            return "gemini"
        return settings.llm_provider

    def generate(self, prompt: str) -> str:
        """Generate text and normalize provider failures to service exceptions."""

        client = self._get_client()

        try:
            if self._provider == "groq":
                response = client.chat.completions.create(
                    model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=4096,
                )
                text = self._extract_groq_text(response)
            else:
                response = client.models.generate_content(model=self._model, contents=prompt)
                text = getattr(response, "text", None)
        except Exception as exc:  # Provider SDK exceptions vary by transport/version.
            provider_name = self._provider.title()
            raise LLMProviderError(f"{provider_name} could not generate notes.") from exc

        if not isinstance(text, str) or not text.strip():
            raise ProviderResponseError(f"{self._provider.title()} returned an empty or malformed response.")
        return text.strip()

    def _extract_groq_text(self, response: Any) -> str:
        choices = getattr(response, "choices", None) or []
        if not choices:
            return ""
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, list):
            return "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return str(content) if content is not None else ""

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if self._provider == "groq":
            api_key = self._api_key if self._api_key is not None else settings.groq_api_key
            if not api_key:
                raise ProviderConfigurationError("GROQ_API_KEY is not configured.")
            if Groq is None:
                raise ProviderConfigurationError("The Groq SDK is not installed.")
            try:
                self._client = Groq(api_key=api_key)
            except Exception as exc:  # Keep SDK setup failures out of route handlers.
                raise LLMProviderError("Groq could not be initialized.") from exc
            return self._client

        api_key = self._api_key if self._api_key is not None else settings.gemini_api_key
        if not api_key:
            raise ProviderConfigurationError("GEMINI_API_KEY is not configured.")

        try:
            self._client = genai.Client(api_key=api_key)
        except Exception as exc:  # Keep SDK setup failures out of route handlers.
            raise LLMProviderError("Gemini could not be initialized.") from exc
        return self._client

import logging
import time
from typing import List, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import API_KEY, BASE_URL, MODEL, TIMEOUT, PROVIDER

logger = logging.getLogger(__name__)


class APIClientError(RuntimeError):
    """Base exception for API client errors."""

    def __init__(self, message: str, *, code: Optional[str] = None, status: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.status = status


class ChatClient:
    """
    Thin wrapper for the Mistral chat completion API (OpenAI-style /chat/completions).
    Adds retry/backoff for transient errors and structured exceptions.
    """

    def __init__(self, model: Optional[str] = None, max_retries: int = 3, backoff_factor: float = 0.8) -> None:
        self.model = model or MODEL
        self.session = requests.Session()

        # Configure urllib3 Retry via requests adapter
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _build_url(self) -> str:
        # Mistral uses the /chat/completions endpoint
        return f"{BASE_URL}/chat/completions"

    def send_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a chat completion request and return assistant text.
        Raises APIClientError on failure with structured info.
        """
        url = self._build_url()

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            logger.info("Sending chat request to provider=%s model=%s messages=%d",
                        PROVIDER, self.model, len(messages))
            # Do not log headers/payload with secrets in production logs; keep debug minimal
            logger.debug("Payload keys: %s", list(payload.keys()))

            # Flask forwards the messages to Mistral AI (This is the actual API integration.)
            response = self.session.post(
                url,
                headers=headers,
                json=payload,
                timeout=TIMEOUT,
            )

            # If we receive a non-2xx, try to parse body for details
            if not response.ok:
                body = None
                try:
                    body = response.json()
                except Exception:
                    body = response.text[:1000] if response.text else None
                logger.warning("Non-OK response from provider=%s status=%s body=%s",
                               PROVIDER, getattr(response, "status_code", "?"), body)
                # Map some upstream statuses to our structured errors
                if response.status_code == 401:
                    raise APIClientError("Unauthorized - invalid API key for provider", code="unauthorized", status=401)
                if response.status_code == 429:
                    raise APIClientError("Rate limited by provider", code="rate_limited", status=429)
                # Generic upstream error
                raise APIClientError(f"Upstream API error: {body}", code="upstream_error", status=response.status_code)

            data = response.json()

            # Expect OpenAI-like response: choices[0].message.content
            try:
                content = data["choices"][0]["message"]["content"]  # type: ignore[index]
            except Exception as e:
                logger.exception("Malformed response from provider: %s", data)
                raise APIClientError("Malformed response from provider", code="malformed_response") from e

            logger.info("Received response from provider=%s", PROVIDER)
            return content

        except requests.exceptions.Timeout as e:
            logger.exception("API timeout")
            raise APIClientError("The request to the LLM API timed out.", code="timeout", status=504) from e
        except requests.exceptions.ConnectionError as e:
            logger.exception("Connection error")
            raise APIClientError("Could not connect to the LLM API. Check network.", code="connection_error", status=503) from e
        except APIClientError:
            # Already structured; re-raise
            raise
        except Exception as e:
            logger.exception("Unexpected error when calling LLM API")
            raise APIClientError(
                "Unexpected error when calling the LLM API. Check logs for details.",
                code="unexpected_error",
            ) from e

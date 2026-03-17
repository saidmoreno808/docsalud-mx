"""
Tests unitarios para DOGradientClient.

Mockea el SDK de Gradient para no consumir creditos en CI.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.gradient.do_gradient_client import DOGradientClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_completion_response(content: str = "respuesta", total_tokens: int = 10) -> MagicMock:
    """Crea un mock de respuesta de chat.completions.create."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    response.usage = MagicMock()
    response.usage.total_tokens = total_tokens
    return response


def _make_embedding_response(vectors: list[list[float]]) -> MagicMock:
    """Crea un mock de respuesta de embeddings.create."""
    response = MagicMock()
    response.data = [MagicMock(embedding=v) for v in vectors]
    return response


# ---------------------------------------------------------------------------
# Tests: instanciacion y configuracion
# ---------------------------------------------------------------------------


class TestDOGradientClientInit:
    def test_uses_settings_when_no_args(self) -> None:
        with patch("app.core.gradient.do_gradient_client.settings") as mock_settings:
            mock_settings.do_gradient_api_key = "key-from-settings"
            mock_settings.do_gradient_model = "llama3-3-70b-instruct"
            client = DOGradientClient()
        assert client.model_access_key == "key-from-settings"
        assert client.model == "llama3-3-70b-instruct"

    def test_explicit_args_override_settings(self) -> None:
        client = DOGradientClient(model_access_key="custom-key", model="custom-model")
        assert client.model_access_key == "custom-key"
        assert client.model == "custom-model"

    def test_client_is_lazy(self) -> None:
        client = DOGradientClient(model_access_key="k", model="m")
        assert client._client is None

    def test_client_property_creates_gradient_instance(self) -> None:
        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            MockGradient.return_value = MagicMock()
            client = DOGradientClient(model_access_key="k", model="m")
            _ = client.client
            MockGradient.assert_called_once_with(model_access_key="k")

    def test_client_property_is_cached(self) -> None:
        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            MockGradient.return_value = MagicMock()
            client = DOGradientClient(model_access_key="k", model="m")
            first = client.client
            second = client.client
            assert first is second
            MockGradient.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: complete()
# ---------------------------------------------------------------------------


class TestComplete:
    def _run(self, coro) -> None:
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_complete_returns_string(self) -> None:
        mock_response = _make_completion_response("Hola mundo")
        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.return_value = mock_response
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="test-model")
            result = self._run(client.complete([{"role": "user", "content": "Hola"}]))

        assert result == "Hola mundo"

    def test_complete_prepends_system_message(self) -> None:
        mock_response = _make_completion_response("ok")
        captured: list = []

        def capture_create(**kwargs):
            captured.append(kwargs.get("messages", []))
            return mock_response

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.side_effect = capture_create
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="m")
            self._run(
                client.complete(
                    [{"role": "user", "content": "query"}],
                    system="eres un medico",
                )
            )

        messages = captured[0]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "eres un medico"
        assert messages[1]["role"] == "user"

    def test_complete_no_system_skips_system_message(self) -> None:
        mock_response = _make_completion_response("ok")
        captured: list = []

        def capture_create(**kwargs):
            captured.append(kwargs.get("messages", []))
            return mock_response

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.side_effect = capture_create
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="m")
            self._run(client.complete([{"role": "user", "content": "query"}]))

        messages = captured[0]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"

    def test_complete_passes_max_tokens(self) -> None:
        mock_response = _make_completion_response("ok")
        captured: list = []

        def capture_create(**kwargs):
            captured.append(kwargs)
            return mock_response

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.side_effect = capture_create
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="m")
            self._run(
                client.complete([{"role": "user", "content": "q"}], max_tokens=42)
            )

        assert captured[0]["max_tokens"] == 42

    def test_complete_passes_model_name(self) -> None:
        mock_response = _make_completion_response("ok")
        captured: list = []

        def capture_create(**kwargs):
            captured.append(kwargs)
            return mock_response

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.side_effect = capture_create
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="my-llm")
            self._run(client.complete([{"role": "user", "content": "q"}]))

        assert captured[0]["model"] == "my-llm"


# ---------------------------------------------------------------------------
# Tests: embed()
# ---------------------------------------------------------------------------


class TestEmbed:
    def _run(self, coro) -> None:
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_embed_returns_list_of_vectors(self) -> None:
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_response = _make_embedding_response(vectors)

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.embeddings.create.return_value = mock_response
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="m")
            result = self._run(client.embed(["texto 1", "texto 2"]))

        assert result == vectors

    def test_embed_empty_list(self) -> None:
        mock_response = _make_embedding_response([])

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.embeddings.create.return_value = mock_response
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="m")
            result = self._run(client.embed([]))

        assert result == []


# ---------------------------------------------------------------------------
# Tests: health_check()
# ---------------------------------------------------------------------------


class TestHealthCheck:
    def _run(self, coro) -> None:
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_health_check_connected(self) -> None:
        mock_response = _make_completion_response("pong")

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.return_value = mock_response
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="my-model")
            result = self._run(client.health_check())

        assert result["gradient_ai"] == "connected"
        assert result["model"] == "my-model"

    def test_health_check_error(self) -> None:
        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.side_effect = Exception("connection refused")
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="m")
            result = self._run(client.health_check())

        assert result["gradient_ai"] == "error"
        assert "connection refused" in result["detail"]

    def test_health_check_pings_with_minimal_tokens(self) -> None:
        mock_response = _make_completion_response("ok")
        captured: list = []

        def capture_create(**kwargs):
            captured.append(kwargs)
            return mock_response

        with patch("app.core.gradient.do_gradient_client.Gradient") as MockGradient:
            mock_sdk = MagicMock()
            mock_sdk.chat.completions.create.side_effect = capture_create
            MockGradient.return_value = mock_sdk

            client = DOGradientClient(model_access_key="k", model="m")
            self._run(client.health_check())

        assert captured[0]["max_tokens"] == 5

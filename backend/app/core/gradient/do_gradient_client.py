"""
Cliente oficial para DigitalOcean Gradient AI SDK.

Wrapper async sobre el SDK sincrono de Gradient, compatible con la interfaz
que antes usaba Groq para no romper ningun modulo externo.
"""

import asyncio

import structlog
from gradient import Gradient

from app.config import settings

logger = structlog.get_logger()


class DOGradientClient:
    """Cliente oficial para DigitalOcean Gradient AI SDK."""

    def __init__(self, model_access_key: str | None = None, model: str | None = None):
        self.model_access_key = model_access_key or settings.do_gradient_api_key
        self.model = model or settings.do_gradient_model
        self._client = None

    @property
    def client(self) -> Gradient:
        if self._client is None:
            self._client = Gradient(model_access_key=self.model_access_key)
        return self._client

    async def complete(
        self, messages: list[dict], system: str = "", max_tokens: int = 1500
    ) -> str:
        """
        Chat completion via DO Gradient AI. Compatible con interfaz Groq.

        Args:
            messages: Lista de mensajes en formato {role, content}.
            system: Prompt de sistema opcional.
            max_tokens: Maximo de tokens en la respuesta.

        Returns:
            Texto de respuesta del modelo.
        """
        loop = asyncio.get_event_loop()
        all_messages: list[dict] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                messages=all_messages,
                model=self.model,
                max_tokens=max_tokens,
            ),
        )
        logger.info(
            "gradient_ai_call",
            model=self.model,
            tokens=response.usage.total_tokens,
        )
        return response.choices[0].message.content

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Embeddings via DO Gradient AI GPU.

        Args:
            texts: Lista de textos a embeber.

        Returns:
            Lista de vectores de embedding.
        """
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002",
            ),
        )
        return [d.embedding for d in response.data]

    async def health_check(self) -> dict:
        """
        Verifica conectividad con DO Gradient AI.

        Returns:
            Diccionario con estado de la conexion.
        """
        try:
            await self.complete([{"role": "user", "content": "ping"}], max_tokens=5)
            return {"gradient_ai": "connected", "model": self.model}
        except Exception as e:
            logger.error("gradient_ai_health_failed", error=str(e))
            return {"gradient_ai": "error", "detail": str(e)}

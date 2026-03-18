"""
Cliente para DigitalOcean Gradient AI / GenAI Platform.

Usa el SDK oficial de OpenAI apuntando al endpoint OpenAI-compatible de DO,
compatible con la interfaz que antes usaba Groq para no romper ningun modulo externo.
"""

import structlog
from openai import AsyncOpenAI

from app.config import settings

logger = structlog.get_logger()


class DOGradientClient:
    """Cliente para DigitalOcean GenAI Platform via API OpenAI-compatible."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.do_gradient_api_key
        self.model = model or settings.do_gradient_model
        self.base_url = settings.do_gradient_base_url
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
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
        all_messages: list[dict] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        response = await self.client.chat.completions.create(
            messages=all_messages,  # type: ignore[arg-type]
            model=self.model,
            max_tokens=max_tokens,
        )
        logger.info(
            "gradient_ai_call",
            model=self.model,
            tokens=response.usage.total_tokens if response.usage else None,
        )
        return response.choices[0].message.content or ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Embeddings via DO Gradient AI GPU.

        Args:
            texts: Lista de textos a embeber.

        Returns:
            Lista de vectores de embedding.
        """
        response = await self.client.embeddings.create(
            input=texts,
            model="text-embedding-ada-002",
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

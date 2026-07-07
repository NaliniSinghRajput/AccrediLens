import httpx

from app.core.config import get_settings


class OllamaClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        async with httpx.AsyncClient(base_url=self.settings.ollama_base_url, timeout=120) as client:
            response = await client.post("/api/embed", json={"model": self.settings.embedding_model, "input": texts})
            if response.status_code == 404:
                return [await self.embed_one_legacy(client, text) for text in texts]
            response.raise_for_status()
            data = response.json()
            return data.get("embeddings", [])

    async def embed_one_legacy(self, client: httpx.AsyncClient, text: str) -> list[float]:
        response = await client.post("/api/embeddings", json={"model": self.settings.embedding_model, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]

    async def generate(self, prompt: str, fast: bool = False) -> str:
        model = self.settings.fast_llm_model if fast else self.settings.llm_model
        async with httpx.AsyncClient(base_url=self.settings.ollama_base_url, timeout=240) as client:
            response = await client.post(
                "/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "top_p": 0.8},
                },
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()

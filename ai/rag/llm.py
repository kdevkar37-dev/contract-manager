from __future__ import annotations

from langchain_ollama import ChatOllama

from backend.app.core.config import settings


DEFAULT_LLM_MODEL = "gemma2:2b"


class ContractLLMService:
    """
    Local LLM service used by the Contract Manager RAG pipeline.

    Uses Ollama so that no paid external LLM API is required.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_LLM_MODEL,
        temperature: float = 0.0,
    ) -> None:
        if not model_name or not model_name.strip():
            raise ValueError("LLM model name cannot be empty.")

        if temperature < 0:
            raise ValueError("temperature cannot be negative.")

        self.model_name = model_name.strip()
        self.temperature = temperature

        self.llm = ChatOllama(
            base_url=settings.ollama_base_url,
            model=self.model_name,
            temperature=temperature,
        )

    def invoke(self, prompt: str) -> str:
        """
        Generate a response using the local Ollama model.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.llm.invoke(prompt)

        content = response.content

        if not isinstance(content, str):
            content = str(content)

        return content.strip()
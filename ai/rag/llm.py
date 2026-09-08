from langchain_ollama import ChatOllama


class ContractLLMService:
    def __init__(
        self,
        model_name: str = "gemma2:2b",
        temperature: float = 0.0,
    ):
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
        )

    def invoke(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)

        return response.content
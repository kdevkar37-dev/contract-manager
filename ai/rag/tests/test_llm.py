from unittest.mock import MagicMock, patch

from ai.rag.llm import ContractLLMService


@patch("ai.rag.llm.ChatOllama")
def test_llm_service_invokes_model(mock_chat_ollama):
    mock_llm = MagicMock()

    mock_llm.invoke.return_value.content = "This is the answer."

    mock_chat_ollama.return_value = mock_llm

    service = ContractLLMService()

    result = service.invoke(
        "What are the payment terms?"
    )

    mock_chat_ollama.assert_called_once_with(
        model="gemma2:2b",
        temperature=0.0,
    )

    mock_llm.invoke.assert_called_once_with(
        "What are the payment terms?"
    )

    assert result == "This is the answer."


@patch("ai.rag.llm.ChatOllama")
def test_llm_service_uses_custom_model(mock_chat_ollama):
    service = ContractLLMService(
        model_name="gemma2:2b",
        temperature=0.2,
    )

    mock_chat_ollama.assert_called_once_with(
        model="gemma2:2b",
        temperature=0.2,
    )
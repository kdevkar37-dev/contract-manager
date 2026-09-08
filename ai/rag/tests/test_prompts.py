from ai.rag.prompts import CONTRACT_RAG_PROMPT


def test_contract_rag_prompt_contains_context_and_question():
    context = "Payment must be completed within 30 days."
    question = "What are the payment terms?"

    prompt = CONTRACT_RAG_PROMPT.format(
        context=context,
        question=question,
    )

    assert context in prompt
    assert question in prompt


def test_contract_rag_prompt_contains_missing_information_rule():
    assert (
        "The requested information was not found in the available contract documents."
        in CONTRACT_RAG_PROMPT
    )
from ai.rag.chunking import ContractTextChunker


def test_split_text_creates_multiple_chunks():
    text = "This is contract text. " * 200

    chunker = ContractTextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.split_text(text)

    assert len(chunks) > 1


def test_split_text_preserves_content():
    text = (
        "Payment must be completed within 30 days. "
        "The supplier must provide all required documents."
    )

    chunker = ContractTextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.split_text(text)

    combined_text = " ".join(chunks)

    assert "Payment must be completed within 30 days." in combined_text
    assert "supplier must provide all required documents." in combined_text


def test_empty_text_returns_empty_list():
    chunker = ContractTextChunker()

    chunks = chunker.split_text("")

    assert chunks == []


def test_chunk_size_is_respected():
    text = "A" * 500

    chunker = ContractTextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.split_text(text)

    assert all(len(chunk) <= 100 for chunk in chunks)
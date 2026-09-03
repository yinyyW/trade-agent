from app.rag.models import DocumentInput, KnowledgeCategory, RetrievedChunk


def test_document_input_defaults_are_stable():
    item = DocumentInput(title="t", content="c", category=KnowledgeCategory.MARKET)
    assert item.source_type == "MANUAL"
    assert item.version == "1.0"
    assert item.metadata == {}


def test_category_values_match_knowledge_base_design():
    assert {x.value for x in KnowledgeCategory} == {
        "FINANCIAL", "MACRO", "MARKET", "TECHNICAL", "COMPLIANCE"
    }


def test_retrieved_chunk_can_carry_rerank_score():
    chunk = RetrievedChunk(1, 2, "title", "content", "FINANCIAL", 0.8)
    chunk.rerank_score = 0.95
    assert chunk.rerank_score == 0.95

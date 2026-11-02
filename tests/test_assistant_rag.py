import pytest
from app.ai.assistant.answer_generator import LLMAnswerGenerator
from app.ai.retrieval.context_builder import ContextBuilder, SourceCitation, GroundedContext


@pytest.mark.asyncio
async def test_deterministic_grounded_fallback_no_api_key():
    citation = SourceCitation(
        source_id="SRC-1",
        book_title="قانون فی الطب",
        author_name="ابن سینا",
        manuscript_title="نسخه خطی ملک",
        page_number=1,
        excerpt="الطب علم يتعرف منه احوال بدن الانسان",
    )
    context = GroundedContext(
        formatted_context_text="[SRC-1] قانون فی الطب",
        citations=[citation],
        has_sources=True,
    )

    result = await LLMAnswerGenerator.generate_answer("تعریف طب چیست؟", context)
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source_id"] == "SRC-1"
    # Never invents data; contains excerpt
    assert "الطب علم يتعرف منه احوال بدن الانسان" in result["answer"]


@pytest.mark.asyncio
async def test_zero_sources_fallback():
    empty_context = GroundedContext(
        formatted_context_text="",
        citations=[],
        has_sources=False,
    )
    result = await LLMAnswerGenerator.generate_answer("آیا نسخه خطی در مورد ماشین بخار وجود دارد؟", empty_context)
    assert len(result["sources"]) == 0
    assert "یافت نشد" in result["answer"]

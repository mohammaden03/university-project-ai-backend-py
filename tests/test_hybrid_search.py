import pytest
from app.ai.retrieval.hybrid_search import SearchResultItem, HybridRanker
from app.ai.retrieval.context_builder import ContextBuilder


def test_reciprocal_rank_fusion():
    lexical = [
        SearchResultItem(
            id="doc1",
            text="پزشکی در تمدن اسلامی و ابن سینا",
            manuscript={"title": "قانون"},
            relevance_score=0.9,
            match_type="lexical",
        ),
        SearchResultItem(
            id="doc2",
            text="داروشناسی و گیاهان دارویی ابوریحان",
            manuscript={"title": "الصیدنه"},
            relevance_score=0.8,
            match_type="lexical",
        ),
    ]

    semantic = [
        SearchResultItem(
            id="doc2",
            text="داروشناسی و گیاهان دارویی ابوریحان",
            manuscript={"title": "الصیدنه"},
            relevance_score=0.95,
            match_type="semantic",
        ),
        SearchResultItem(
            id="doc3",
            text="امزجه و ارکان در طب سنتی",
            manuscript={"title": "الحاوی"},
            relevance_score=0.7,
            match_type="semantic",
        ),
    ]

    fused = HybridRanker.rrf_fuse(lexical, semantic)
    assert len(fused) == 3
    # doc2 appeared in both lexical and semantic -> upgraded to hybrid and should rank top
    assert fused[0].id == "doc2"
    assert fused[0].match_type == "hybrid"


def test_context_builder_citations():
    passages = [
        SearchResultItem(
            id="p1",
            text="الطب علم يتعرف منه احوال بدن الانسان",
            book={"id": "b1", "title": "قانون فی الطب"},
            author={"id": "a1", "name": "ابن سینا"},
            manuscript={"title": "نسخه کهن ملک"},
            page_number=1,
            relevance_score=0.92,
            match_type="hybrid",
        )
    ]

    context = ContextBuilder.build_context(passages)
    assert context.has_sources is True
    assert len(context.citations) == 1
    assert context.citations[0].source_id == "SRC-1"
    assert context.citations[0].book_title == "قانون فی الطب"
    assert context.citations[0].page_number == 1
    assert "[SRC-1]" in context.formatted_context_text

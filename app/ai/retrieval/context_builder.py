from typing import Dict, List, Tuple
from pydantic import BaseModel
from app.ai.retrieval.hybrid_search import SearchResultItem


class SourceCitation(BaseModel):
    source_id: str
    book_title: str
    author_name: str
    manuscript_title: str
    page_number: int
    excerpt: str


class GroundedContext(BaseModel):
    formatted_context_text: str
    citations: List[SourceCitation]
    has_sources: bool


class ContextBuilder:
    """
    Constructs strict, citation-grounded context blocks for LLM reasoning.
    Ensures that every claim made by the assistant corresponds to a genuine DB manuscript passage.
    """

    @classmethod
    def build_context(
        cls, retrieved_passages: List[SearchResultItem], max_passages: int = 5
    ) -> GroundedContext:
        if not retrieved_passages:
            return GroundedContext(
                formatted_context_text="هیچ نسخه خطی مرتبطی در پایگاه داده یافت نشد.",
                citations=[],
                has_sources=False,
            )

        context_lines: List[str] = []
        citations: List[SourceCitation] = []

        for idx, item in enumerate(retrieved_passages[:max_passages]):
            source_id = f"SRC-{idx + 1}"
            book_title = item.book.get("title", "نامشخص") if item.book else "نامشخص"
            author_name = item.author.get("name", "نامشخص") if item.author else "نامشخص"
            ms_title = item.manuscript.get("title", "نسخه خطی")
            page_num = item.page_number or 1

            citation = SourceCitation(
                source_id=source_id,
                book_title=book_title,
                author_name=author_name,
                manuscript_title=ms_title,
                page_number=page_num,
                excerpt=item.text.strip(),
            )
            citations.append(citation)

            context_lines.append(
                f"[{source_id}]\n"
                f"کتاب: {book_title}\n"
                f"نویسنده: {author_name}\n"
                f"نسخه: {ms_title} (صفحه/برگ: {page_num})\n"
                f"متن کهن:\n\"{item.text.strip()}\"\n"
            )

        return GroundedContext(
            formatted_context_text="\n---\n".join(context_lines),
            citations=citations,
            has_sources=True,
        )

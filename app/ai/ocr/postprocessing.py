from typing import List
from app.ai.ocr.base import RecognizedLine


class PostProcessor:
    @classmethod
    def assemble_text(cls, lines: List[RecognizedLine]) -> str:
        """Joins line texts with newlines, preserving right-to-left line continuity."""
        cleaned_lines = [line.text.strip() for line in lines if line.text.strip()]
        return "\n".join(cleaned_lines)

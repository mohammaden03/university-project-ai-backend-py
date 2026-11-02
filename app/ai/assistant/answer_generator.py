import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional
import httpx
from app.ai.retrieval.context_builder import GroundedContext, SourceCitation
from app.ai.assistant.prompt_templates import (
    RESEARCH_SYSTEM_PROMPT,
    RESEARCH_USER_TEMPLATE,
    NO_SOURCES_FALLBACK_PERSIAN,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMAnswerGenerator:
    """
    Modular LLM answer generator supporting Gemini, OpenAI-compatible APIs,
    and a zero-hallucination deterministic fallback when no LLM API key is present.
    """

    @classmethod
    async def generate_answer(
        cls,
        query: str,
        grounded_context: GroundedContext,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        if not grounded_context.has_sources:
            return {
                "answer": NO_SOURCES_FALLBACK_PERSIAN,
                "sources": [],
                "provider": "grounded_retrieval_guard",
            }

        provider = settings.LLM_PROVIDER.lower()
        api_key = settings.LLM_API_KEY

        # Check if external LLM is configured
        if not api_key:
            return cls._generate_deterministic_fallback(query, grounded_context)

        if provider == "gemini":
            return await cls._call_gemini(query, grounded_context, chat_history, api_key)
        elif provider in ["openai", "custom"]:
            return await cls._call_openai_compatible(query, grounded_context, chat_history, api_key)
        else:
            return cls._generate_deterministic_fallback(query, grounded_context)

    @classmethod
    async def stream_answer(
        cls,
        query: str,
        grounded_context: GroundedContext,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Yields Server-Sent Event (SSE) formatted events:
        - message_start
        - token
        - source
        - message_complete
        - error
        """
        # 1. message_start
        yield cls._format_sse("message_start", {"query": query})

        # 2. Emit sources first so UI can render citation cards immediately
        for src in grounded_context.citations:
            yield cls._format_sse("source", src.model_dump())

        if not grounded_context.has_sources:
            yield cls._format_sse("token", {"token": NO_SOURCES_FALLBACK_PERSIAN})
            yield cls._format_sse("message_complete", {"full_text": NO_SOURCES_FALLBACK_PERSIAN})
            return

        api_key = settings.LLM_API_KEY
        provider = settings.LLM_PROVIDER.lower()

        if not api_key:
            # Deterministic token streaming
            fallback_res = cls._generate_deterministic_fallback(query, grounded_context)
            full_text = fallback_res["answer"]
            words = full_text.split(" ")
            for w in words:
                yield cls._format_sse("token", {"token": w + " "})
                await asyncio.sleep(0.015)
            yield cls._format_sse("message_complete", {"full_text": full_text})
            return

        try:
            # Call streaming provider
            if provider == "gemini":
                async for token in cls._stream_gemini(query, grounded_context, chat_history, api_key):
                    yield cls._format_sse("token", {"token": token})
            else:
                res = await cls.generate_answer(query, grounded_context, chat_history)
                for w in res["answer"].split(" "):
                    yield cls._format_sse("token", {"token": w + " "})
                    await asyncio.sleep(0.01)

            yield cls._format_sse("message_complete", {"status": "success"})
        except Exception as e:
            logger.error(f"Error streaming LLM response: {str(e)}")
            yield cls._format_sse("error", {"error": str(e)})

    @classmethod
    def _generate_deterministic_fallback(
        cls, query: str, context: GroundedContext
    ) -> Dict[str, Any]:
        """
        Synthesizes a structured, scholarly summary purely from the retrieved manuscript passages.
        Zero hallucination, fully grounded.
        """
        citations_summary = []
        for src in context.citations:
            citations_summary.append(
                f"«{src.excerpt}» [{src.source_id}] (کتاب {src.book_title}، اثر {src.author_name}، برگ {src.page_number})"
            )

        answer_text = (
            f"بر اساس اسناد کهن بازیابی‌شده پیرامون پرسش «{query}»، نکات و عبارات زیر در متون پایگاه داده یافت شد:\n\n"
            + "\n\n".join(citations_summary)
            + "\n\n(توجه: به دلیل عدم تنظیم کلید سرویس هوش مصنوعی، متن دقیق نسخه‌های خطی فوق مستقیماً از پایگاه داده واکشی و بدون تفسیر اضافی تقدیم پژوهشگر گردید.)"
        )

        return {
            "answer": answer_text,
            "sources": [s.model_dump() for s in context.citations],
            "provider": "deterministic_grounded_citations",
        }

    @classmethod
    async def _call_gemini(
        cls,
        query: str,
        context: GroundedContext,
        chat_history: Optional[List[Dict[str, str]]],
        api_key: str,
    ) -> Dict[str, Any]:
        prompt = RESEARCH_USER_TEMPLATE.format(context=context.formatted_context_text, query=query)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={api_key}"

        contents = []
        if chat_history:
            for msg in chat_history[-6:]:
                role = "user" if msg["role"] == "USER" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "systemInstruction": {"parts": [{"text": RESEARCH_SYSTEM_PROMPT}]},
            "contents": contents,
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "maxOutputTokens": settings.LLM_MAX_OUTPUT_TOKENS,
            },
        }

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
                return cls._generate_deterministic_fallback(query, context)

            data = resp.json()
            try:
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return cls._generate_deterministic_fallback(query, context)

            return {
                "answer": answer,
                "sources": [s.model_dump() for s in context.citations],
                "provider": "gemini",
            }

    @classmethod
    async def _stream_gemini(
        cls,
        query: str,
        context: GroundedContext,
        chat_history: Optional[List[Dict[str, str]]],
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        prompt = RESEARCH_USER_TEMPLATE.format(context=context.formatted_context_text, query=query)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:streamGenerateContent?alt=sse&key={api_key}"

        payload = {
            "systemInstruction": {"parts": [{"text": RESEARCH_SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "maxOutputTokens": settings.LLM_MAX_OUTPUT_TOKENS,
            },
        }

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            async with client.stream("POST", url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            chunk = json.loads(data_str)
                            token = chunk["candidates"][0]["content"]["parts"][0]["text"]
                            yield token
                        except Exception:
                            continue

    @classmethod
    async def _call_openai_compatible(
        cls,
        query: str,
        context: GroundedContext,
        chat_history: Optional[List[Dict[str, str]]],
        api_key: str,
    ) -> Dict[str, Any]:
        base_url = settings.LLM_BASE_URL or "https://api.openai.com/v1"
        url = f"{base_url.rstrip('/')}/chat/completions"

        messages = [{"role": "system", "content": RESEARCH_SYSTEM_PROMPT}]
        if chat_history:
            for msg in chat_history[-6:]:
                r = "user" if msg["role"] == "USER" else "assistant"
                messages.append({"role": r, "content": msg["content"]})

        messages.append({
            "role": "user",
            "content": RESEARCH_USER_TEMPLATE.format(context=context.formatted_context_text, query=query),
        })

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": settings.LLM_MODEL,
            "messages": messages,
            "temperature": settings.LLM_TEMPERATURE,
        }

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                return cls._generate_deterministic_fallback(query, context)
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            return {
                "answer": answer,
                "sources": [s.model_dump() for s in context.citations],
                "provider": "openai_compatible",
            }

    @staticmethod
    def _format_sse(event_type: str, data: Any) -> str:
        return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

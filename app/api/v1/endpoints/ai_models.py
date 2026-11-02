from typing import Any, Dict, List
from fastapi import APIRouter
from app.ai.ocr.model_registry import HTRModelRegistry
from app.ai.embeddings.model_loader import EmbeddingModelRegistry
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/ai", tags=["AI & Models"])


@router.get("/models")
async def list_available_ai_models() -> Dict[str, Any]:
    """
    Returns registered HTR/OCR models, multilingual embedding models, and configured LLM provider.
    """
    htr_models = HTRModelRegistry.list_models()
    htr_details = []
    for m in htr_models:
        try:
            model_inst = HTRModelRegistry.get_model(m)
            htr_details.append(model_inst.get_model_info())
        except Exception:
            htr_details.append({"name": m, "status": "registered"})

    emb_model = EmbeddingModelRegistry.get_model()

    return {
        "htr_models": htr_details,
        "default_htr_model": settings.OCR_DEFAULT_MODEL,
        "embeddings": {
            "model_name": settings.EMBEDDING_MODEL_NAME,
            "dimension": emb_model.get_dimension(),
            "device": settings.EMBEDDING_DEVICE,
        },
        "llm_assistant": {
            "provider": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
            "has_api_key": bool(settings.LLM_API_KEY),
            "fallback_mode": "deterministic_grounded_citations" if not settings.LLM_API_KEY else "none",
        },
    }

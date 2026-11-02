import logging
from typing import Dict, Type
from app.ai.ocr.base import HTRModel
from app.ai.ocr.trocr_adapter import TrOCRManuscriptAdapter
from app.ai.ocr.test_adapter import TestMockHTRAdapter
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class HTRModelRegistry:
    """Registry allowing seamless switching between HTR architectures via configuration."""

    _registry: Dict[str, Type[HTRModel]] = {
        "trocr_handwritten_persian": TrOCRManuscriptAdapter,
        "trocr": TrOCRManuscriptAdapter,
        "test_mock": TestMockHTRAdapter,
    }

    _instances: Dict[str, HTRModel] = {}

    @classmethod
    def register(cls, model_key: str, model_class: Type[HTRModel]) -> None:
        cls._registry[model_key] = model_class

    @classmethod
    def get_model(cls, model_key: str = None) -> HTRModel:
        key = model_key or settings.OCR_DEFAULT_MODEL
        if key not in cls._instances:
            if key in cls._registry:
                model_cls = cls._registry[key]
                logger.info(f"Instantiating HTR model adapter for '{key}'")
                cls._instances[key] = model_cls()
            else:
                logger.warning(
                    f"Model key '{key}' not in registry. Falling back to 'trocr_handwritten_persian'."
                )
                cls._instances[key] = TrOCRManuscriptAdapter()

        return cls._instances[key]

    @classmethod
    def list_models(cls) -> list[str]:
        return list(cls._registry.keys())

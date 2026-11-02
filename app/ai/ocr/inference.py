from typing import List, Optional
from PIL import Image
from app.ai.ocr.base import HTRPredictionResult
from app.ai.ocr.model_registry import HTRModelRegistry


class OCRInferenceService:
    @classmethod
    def run_recognition(
        cls, image: Image.Image, model_name: Optional[str] = None
    ) -> HTRPredictionResult:
        model = HTRModelRegistry.get_model(model_name)
        return model.predict(image)

    @classmethod
    def run_batch_recognition(
        cls, images: List[Image.Image], model_name: Optional[str] = None
    ) -> List[HTRPredictionResult]:
        model = HTRModelRegistry.get_model(model_name)
        return model.predict_batch(images)

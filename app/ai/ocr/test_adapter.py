from typing import Any, Dict, List
from PIL import Image
from app.ai.ocr.base import HTRModel, HTRPredictionResult, RecognizedLine, BoundingBox


class TestMockHTRAdapter(HTRModel):
    """
    Deterministically configured HTR adapter for unit tests and local headless evaluation.
    Clearly designated for software testing only; not evidence of model accuracy.
    """

    def __init__(self, model_name: str = "mock-persian-naskh-v1"):
        self.model_name = model_name
        self._loaded = False

    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self) -> None:
        self._loaded = True

    def predict(self, image: Image.Image) -> HTRPredictionResult:
        w, h = image.size
        lines = [
            RecognizedLine(
                line_index=1,
                text="بسم الله الرحمن الرحیم",
                confidence=0.98,
                bounding_box=BoundingBox(x=50, y=30, width=w - 100, height=35),
            ),
            RecognizedLine(
                line_index=2,
                text="قانون فی الطب تألیف شیخ الرئیس ابو علی سینا",
                confidence=0.92,
                bounding_box=BoundingBox(x=40, y=75, width=w - 80, height=40),
            ),
            RecognizedLine(
                line_index=3,
                text="فی بیان حفظ الصحه و مزاج الارکان والامزجه",
                confidence=0.88,
                bounding_box=BoundingBox(x=45, y=125, width=w - 90, height=38),
            ),
        ]
        return HTRPredictionResult(
            text="\n".join(l.text for l in lines),
            language="fa",
            model_name=self.model_name,
            model_version="test-1.0",
            confidence=0.926,
            lines=lines,
            warnings=["Test mock adapter used for automated testing."],
            processing_time_ms=12,
            preprocessing_metadata={"mock": True},
        )

    def predict_batch(self, images: List[Image.Image]) -> List[HTRPredictionResult]:
        return [self.predict(img) for img in images]

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name,
            "architecture": "TestMockAdapter",
            "device": "cpu",
            "is_loaded": self._loaded,
            "is_mock": True,
        }

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from PIL import Image
from pydantic import BaseModel


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class RecognizedLine(BaseModel):
    line_index: int
    text: str
    confidence: Optional[float] = None
    bounding_box: Optional[BoundingBox] = None


class HTRPredictionResult(BaseModel):
    text: str
    language: str
    model_name: str
    model_version: str
    confidence: Optional[float] = None
    lines: List[RecognizedLine] = []
    warnings: List[str] = []
    processing_time_ms: int = 0
    preprocessing_metadata: Dict[str, Any] = {}


class HTRModel(ABC):
    """
    Common abstract interface for all Handwritten Text Recognition (HTR) models.
    Supports vision-encoder-decoder transformers, CRNN, PyLaia, and custom adapters.
    """

    @abstractmethod
    def load_model(self) -> None:
        """Loads model weights into memory/device lazily."""
        pass

    @abstractmethod
    def predict(self, image: Image.Image) -> HTRPredictionResult:
        """Runs inference on a single manuscript image."""
        pass

    @abstractmethod
    def predict_batch(self, images: List[Image.Image]) -> List[HTRPredictionResult]:
        """Runs batch inference."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Returns metadata such as supported scripts, languages, architecture, and limitations."""
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Returns True if weights are loaded into memory."""
        pass

import logging
import time
from typing import Any, Dict, List, Optional
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, AutoProcessor

from app.ai.ocr.base import HTRModel, HTRPredictionResult, RecognizedLine, BoundingBox
from app.ai.ocr.confidence import ConfidenceEvaluator
from app.ai.ocr.preprocessing import ManuscriptPreprocessor
from app.ai.ocr.segmentation import TextLineSegmenter
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TrOCRManuscriptAdapter(HTRModel):
    """
    Vision-Encoder-Decoder (TrOCR) adapter for handwritten manuscripts.
    Uses lazy loading and explicitly documents language & script compatibility.
    """

    def __init__(
        self,
        model_name_or_path: str = "microsoft/trocr-base-handwritten",
        device: Optional[str] = None,
        max_length: int = settings.OCR_MAX_LENGTH,
    ):
        self.model_name_or_path = model_name_or_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = max_length
        self._model: Optional[VisionEncoderDecoderModel] = None
        self._processor: Optional[AutoProcessor] = None
        self._is_loaded = False

    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_model(self) -> None:
        """Loads TrOCR weights lazily to avoid blocking server boot."""
        if self._is_loaded:
            return

        logger.info(f"Loading HTR TrOCR model from {self.model_name_or_path} on {self.device}...")
        try:
            self._processor = AutoProcessor.from_pretrained(self.model_name_or_path)
            self._model = VisionEncoderDecoderModel.from_pretrained(self.model_name_or_path)
            self._model.to(self.device)
            self._model.eval()
            self._is_loaded = True
            logger.info("HTR TrOCR model successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to load TrOCR model: {str(e)}")
            raise e

    def predict(self, image: Image.Image) -> HTRPredictionResult:
        start_time = time.time()
        # 1. Preprocess manuscript image
        preprocessed_img, prep_meta = ManuscriptPreprocessor.preprocess(
            image,
            enhance_contrast=settings.ENABLE_IMAGE_PREPROCESSING,
            denoise=settings.ENABLE_IMAGE_PREPROCESSING,
            deskew=settings.ENABLE_IMAGE_PREPROCESSING,
        )

        # 2. Line Segmentation
        line_crops = TextLineSegmenter.segment_lines(preprocessed_img)

        # Ensure model is loaded
        if not self._is_loaded:
            self.load_model()

        recognized_lines: List[RecognizedLine] = []
        overall_confidences: List[float] = []

        for idx, (crop_img, bbox) in enumerate(line_crops):
            pixel_values = self._processor(crop_img.convert("RGB"), return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)

            with torch.no_grad():
                outputs = self._model.generate(
                    pixel_values,
                    max_length=self.max_length,
                    return_dict_in_generate=True,
                    output_scores=True,
                )

            sequences = outputs.sequences
            line_text = self._processor.batch_decode(sequences, skip_special_tokens=True)[0]

            # Calculate token-level logit confidence
            line_conf: Optional[float] = None
            if hasattr(outputs, "scores") and outputs.scores:
                try:
                    scores = torch.stack(outputs.scores, dim=1)
                    probs = torch.softmax(scores, dim=-1)
                    # Extract probabilities for the generated tokens
                    token_probs = [
                        probs[0, t, sequences[0, t + 1]].item()
                        for t in range(len(outputs.scores))
                        if t + 1 < sequences.shape[1]
                    ]
                    if token_probs:
                        line_conf = sum(token_probs) / len(token_probs)
                        overall_confidences.append(line_conf)
                except Exception:
                    line_conf = None

            recognized_lines.append(
                RecognizedLine(
                    line_index=idx + 1,
                    text=line_text,
                    confidence=round(line_conf, 3) if line_conf is not None else None,
                    bounding_box=bbox,
                )
            )

        avg_confidence = (
            sum(overall_confidences) / len(overall_confidences)
            if overall_confidences
            else None
        )
        conf_score, warnings = ConfidenceEvaluator.evaluate(avg_confidence)

        # Append model limitation warning if using standard Latin-based checkpoint
        if "handwritten" in self.model_name_or_path.lower() and "persian" not in self.model_name_or_path.lower():
            warnings.append(
                f"Notice: Model checkpoint '{self.model_name_or_path}' is a general TrOCR checkpoint. "
                "For historical Persian/Arabic nastaliq or naskh calligraphy, fine-tuning on domain-specific "
                "manuscript datasets (CER < 10%) is recommended."
            )

        total_text = "\n".join(l.text for l in recognized_lines)
        processing_time = int((time.time() - start_time) * 1000)

        return HTRPredictionResult(
            text=total_text,
            language="fa",
            model_name=self.model_name_or_path,
            model_version="1.0.0",
            confidence=conf_score,
            lines=recognized_lines,
            warnings=warnings,
            processing_time_ms=processing_time,
            preprocessing_metadata=prep_meta,
        )

    def predict_batch(self, images: List[Image.Image]) -> List[HTRPredictionResult]:
        return [self.predict(img) for img in images]

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name_or_path,
            "architecture": "VisionEncoderDecoder (TrOCR)",
            "device": self.device,
            "is_loaded": self._is_loaded,
            "supported_languages": ["fa", "ar", "en"],
            "supported_scripts": ["Naskh", "Nastaliq", "Thuluth", "Ruqah", "Latin"],
            "limitations": (
                "Highly ligated, overlapping Shikasteh scripts require manual verification. "
                "Non-fine-tuned checkpoints have limited lexicon coverage for 10th-14th century Arabic/Persian orthography."
            ),
        }

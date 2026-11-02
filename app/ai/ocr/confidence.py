from typing import List, Optional, Tuple
from app.core.config import get_settings

settings = get_settings()


class ConfidenceEvaluator:
    """
    Evaluates confidence metrics from HTR model log-probabilities and token logits.
    Generates research warnings if confidence falls below the reliability threshold.
    """

    CONFIDENCE_THRESHOLD = settings.OCR_CONFIDENCE_THRESHOLD

    @classmethod
    def evaluate(cls, confidence: Optional[float]) -> Tuple[Optional[float], List[str]]:
        """
        Validates confidence score and produces warnings if human verification is required.
        """
        warnings: List[str] = []
        if confidence is None:
            warnings.append("Model did not return log-probability confidence scores.")
            return None, warnings

        # Round to 3 decimal places
        norm_conf = round(max(0.0, min(1.0, float(confidence))), 3)

        if norm_conf < cls.CONFIDENCE_THRESHOLD:
            warnings.append(
                f"Low recognition confidence ({norm_conf * 100:.1f}%). "
                "Historical calligraphic ligatures detected. Human expert verification is strongly recommended."
            )

        return norm_conf, warnings

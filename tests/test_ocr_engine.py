import numpy as np
import pytest
from PIL import Image
from app.ai.ocr.model_registry import HTRModelRegistry
from app.ai.ocr.test_adapter import TestMockHTRAdapter
from app.ai.ocr.preprocessing import ManuscriptPreprocessor
from app.ai.ocr.segmentation import TextLineSegmenter
from app.ai.ocr.confidence import ConfidenceEvaluator


def test_model_registry():
    HTRModelRegistry.register("test_mock", TestMockHTRAdapter)
    assert "test_mock" in HTRModelRegistry.list_models()
    model = HTRModelRegistry.get_model("test_mock")
    assert model.get_model_info()["architecture"] == "TestMockAdapter"


def test_image_preprocessing():
    # Create simple dummy image with text band
    img = Image.new("RGB", (600, 800), color=(240, 230, 210))
    preprocessed, metadata = ManuscriptPreprocessor.preprocess(
        img, enhance_contrast=True, denoise=True, deskew=True
    )
    assert preprocessed is not None
    assert metadata["contrast_enhanced"] is True
    assert "preprocessing_time_ms" in metadata


def test_line_segmenter():
    img = Image.new("RGB", (600, 400), color=(255, 255, 255))
    lines = TextLineSegmenter.segment_lines(img)
    assert len(lines) >= 1
    crop, bbox = lines[0]
    assert bbox.width > 0
    assert bbox.height > 0


def test_confidence_evaluator():
    # High confidence: no warning
    score, warnings = ConfidenceEvaluator.evaluate(0.95)
    assert score == 0.95
    assert len(warnings) == 0

    # Low confidence: triggers warning for human review
    score, warnings = ConfidenceEvaluator.evaluate(0.45)
    assert score == 0.45
    assert len(warnings) == 1
    assert "Low recognition confidence" in warnings[0]

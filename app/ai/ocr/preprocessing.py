import time
from typing import Any, Dict, Tuple
import cv2
import numpy as np
from PIL import Image


class ManuscriptPreprocessor:
    """
    Image preprocessing pipeline specifically tuned for historical manuscripts.
    Avoids aggressive binarization that would obliterate delicate calligraphic ink strokes.
    """

    @classmethod
    def preprocess(
        cls,
        image: Image.Image,
        enhance_contrast: bool = True,
        denoise: bool = True,
        deskew: bool = True,
        target_dpi_height: int = 1600,
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Runs non-destructive preprocessing on the image.
        Returns the preprocessed PIL Image and a metadata dict detailing adjustments.
        """
        start_time = time.time()
        metadata: Dict[str, Any] = {
            "original_size": image.size,
            "contrast_enhanced": enhance_contrast,
            "denoised": denoise,
            "deskewed": deskew,
        }

        # Convert PIL Image to RGB OpenCV format
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)

        # 1. Normalize resolution if excessively large or small
        h, w = cv_img.shape[:2]
        if h > target_dpi_height:
            scale = target_dpi_height / float(h)
            new_w = int(w * scale)
            cv_img = cv2.resize(cv_img, (new_w, target_dpi_height), interpolation=cv2.INTER_AREA)
            metadata["resized_from"] = (w, h)
            metadata["resized_to"] = (new_w, target_dpi_height)

        # 2. Convert to Grayscale for illumination and contrast analysis
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # 3. Deskewing
        deskew_angle = 0.0
        if deskew:
            deskew_angle = cls._compute_skew_angle(gray)
            metadata["skew_angle_degrees"] = round(deskew_angle, 2)
            if abs(deskew_angle) > 0.5:
                cv_img = cls._rotate_image(cv_img, deskew_angle)
                gray = cls._rotate_image(gray, deskew_angle)

        # 4. Contrast Limited Adaptive Histogram Equalization (CLAHE) on L-channel
        if enhance_contrast:
            lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            cv_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # 5. Non-aggressive Denoising (bilateral filter preserves ink boundaries)
        if denoise:
            cv_img = cv2.bilateralFilter(cv_img, d=5, sigmaColor=50, sigmaSpace=50)

        # Convert back to PIL Image (RGB)
        processed_pil = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        metadata["preprocessing_time_ms"] = int((time.time() - start_time) * 1000)

        return processed_pil, metadata

    @classmethod
    def _compute_skew_angle(cls, gray_image: np.ndarray) -> float:
        """Estimates skew angle using Otsu threshold and minimum area rectangle on text contours."""
        try:
            thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 100:
                return 0.0
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle
            # Bound realistic skew for manuscripts to [-15, 15]
            if abs(angle) > 15.0:
                return 0.0
            return float(angle)
        except Exception:
            return 0.0

    @classmethod
    def _rotate_image(cls, image: np.ndarray, angle: float) -> np.ndarray:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        m = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

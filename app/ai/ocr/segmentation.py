from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image
from app.ai.ocr.base import BoundingBox


class TextLineSegmenter:
    """
    Segment historical manuscript pages into discrete lines, preserving
    the traditional Right-to-Left and Top-to-Bottom reading order.
    """

    @classmethod
    def segment_lines(
        cls, image: Image.Image, min_line_height: int = 15, max_gap: int = 20
    ) -> List[Tuple[Image.Image, BoundingBox]]:
        """
        Segments the page image into lines.
        Returns a list of (cropped_line_image, BoundingBox) tuples sorted in reading order.
        """
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Adaptive thresholding to obtain binary ink mask
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10
        )

        # Horizontal projection profile to detect line baselines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w // 15, 3))
        dilated = cv2.dilate(binary, horizontal_kernel, iterations=2)

        # Find line contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        line_boxes: List[BoundingBox] = []
        for c in contours:
            x, y, bw, bh = cv2.boundingRect(c)
            # Filter noise contours that are too small
            if bh >= min_line_height and bw >= w // 10:
                # Add slight vertical padding
                pad_y = 4
                actual_y = max(0, y - pad_y)
                actual_h = min(h - actual_y, bh + 2 * pad_y)
                actual_x = max(0, x - 5)
                actual_w = min(w - actual_x, bw + 10)
                line_boxes.append(BoundingBox(x=actual_x, y=actual_y, width=actual_w, height=actual_h))

        # Sort lines primarily top-to-bottom, secondarily right-to-left
        line_boxes.sort(key=lambda b: (b.y // 20, -b.x))

        # Merge overlapping line boxes
        merged_boxes = cls._merge_boxes(line_boxes, max_gap)

        results: List[Tuple[Image.Image, BoundingBox]] = []
        for box in merged_boxes:
            crop = image.crop((box.x, box.y, box.x + box.width, box.y + box.height))
            results.append((crop, box))

        # If no lines were detected, fallback to whole page
        if not results:
            results.append((image, BoundingBox(x=0, y=0, width=w, height=h)))

        return results

    @classmethod
    def _merge_boxes(cls, boxes: List[BoundingBox], max_vertical_gap: int) -> List[BoundingBox]:
        if not boxes:
            return []
        merged = [boxes[0]]
        for curr in boxes[1:]:
            prev = merged[-1]
            # Check if boxes are vertically on almost the same line
            if abs(curr.y - prev.y) < max_vertical_gap:
                min_x = min(prev.x, curr.x)
                max_x = max(prev.x + prev.width, curr.x + curr.width)
                min_y = min(prev.y, curr.y)
                max_y = max(prev.y + prev.height, curr.y + curr.height)
                merged[-1] = BoundingBox(
                    x=min_x, y=min_y, width=max_x - min_x, height=max_y - min_y
                )
            else:
                merged.append(curr)
        return merged

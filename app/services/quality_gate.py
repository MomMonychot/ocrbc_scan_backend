"""Pre-Flight Document Quality Gate Service.

Architectural and Security Rationale:
- Enforces front-line verification before any heavy OCR or background pipeline computation.
- Prevents resource exhaustion from unreadable, heavily blurred, or improperly exposed images.
- Implements strict Zero-Data-Retention (ZDR): file bytes are processed entirely in-memory
  via numpy and OpenCV memory decoders without temporary disk writes.
- Explicitly tests:
  1. Sharpness/Blur: via the variance of the Laplacian operator.
  2. Brightness/Exposure: via grayscale mean pixel intensity and dynamic range.
- Composite quality confidence score is calculated (0 to 100%).
- If the composite score falls below 40%, the document is rejected with the standardized message:
  "This file has quality issues (blur, dark, or incomplete). Please retake the photo."
"""

import gc
import logging
from typing import Any, Dict, Optional
import cv2
import numpy as np

from app.core.config import app_settings

logger = logging.getLogger("district_ocr_quality_gate")

REJECTION_MESSAGE = "This file has quality issues (blur, dark, or incomplete). Please retake the photo."


def evaluate_document_quality(file_bytes: bytes) -> Dict[str, Any]:
    """Evaluates the sharpness, exposure, and overall readability of a document image in RAM.

    Args:
        file_bytes: Raw binary bytes of the uploaded image file.

    Returns:
        Structured dictionary containing:
        - is_accepted (bool): True if composite score >= threshold (40%).
        - confidence_score (float): Composite quality score (0.0 to 100.0).
        - sharpness_score (float): Sharpness rating (0.0 to 100.0).
        - laplacian_variance (float): Raw Laplacian variance.
        - brightness_score (float): Exposure rating (0.0 to 100.0).
        - mean_brightness (float): Mean pixel value (0 to 255).
        - error_message (Optional[str]): Rejection notice if not accepted.
        - details (Dict[str, Any]): Additional diagnostic metrics.
    """
    if not file_bytes:
        logger.warning("Quality gate received empty file bytes.")
        return {
            "is_accepted": False,
            "confidence_score": 0.0,
            "sharpness_score": 0.0,
            "laplacian_variance": 0.0,
            "brightness_score": 0.0,
            "mean_brightness": 0.0,
            "error_message": REJECTION_MESSAGE,
            "details": {
                "rejection_reason": "Payload is empty (0 bytes).",
            },
        }

    image: Optional[np.ndarray] = None
    gray: Optional[np.ndarray] = None
    laplacian: Optional[np.ndarray] = None

    try:
        # Decode image strictly in-memory from buffer
        np_buffer = np.frombuffer(file_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

        if image is None:
            logger.warning("Failed to decode image from memory buffer. File may be corrupted.")
            return {
                "is_accepted": False,
                "confidence_score": 0.0,
                "sharpness_score": 0.0,
                "laplacian_variance": 0.0,
                "brightness_score": 0.0,
                "mean_brightness": 0.0,
                "error_message": REJECTION_MESSAGE,
                "details": {
                    "rejection_reason": "Image format could not be decoded. File may be corrupted.",
                },
            }

        height, width = image.shape[:2]

        # Convert to single-channel grayscale for analytical metric extraction
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # -----------------------------------------------------------------------
        # 1. Sharpness Analysis (Laplacian Variance Method)
        # -----------------------------------------------------------------------
        # The variance of the Laplacian reflects edge definition.
        # Clean photographed documents typically yield variance > 250-300.
        # Blurry or motion-degraded photos fall well below 100.
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_variance = float(laplacian.var())

        # Map Laplacian variance to a normalized 0-100 score (clamped at 300)
        # 300+ variance achieves a full 100% sharpness score
        sharpness_score = float(np.clip((laplacian_variance / 300.0) * 100.0, 0.0, 100.0))

        # -----------------------------------------------------------------------
        # 2. Brightness & Exposure Analysis (Mean Pixel Intensity)
        # -----------------------------------------------------------------------
        # Administrative paper documents feature high reflectance (white paper, dark ink).
        # Optimum mean luminance is ~120 to 180 (centered at 145).
        # Values < 55 are underexposed/shadowed; values > 225 are washed out/glared.
        mean_brightness = float(np.mean(gray))

        ideal_brightness = 145.0
        max_deviation = 145.0
        brightness_deviation = abs(mean_brightness - ideal_brightness)
        brightness_score = float(
            np.clip((1.0 - (brightness_deviation / max_deviation)) * 100.0, 0.0, 100.0)
        )

        # -----------------------------------------------------------------------
        # 3. Composite Score Calculation
        # -----------------------------------------------------------------------
        # Sharpness is paramount for OCR character segmentation (60% weight).
        # Exposure/Luminance balance provides the supporting 40% weight.
        composite_score = round((sharpness_score * 0.60) + (brightness_score * 0.40), 2)

        # -----------------------------------------------------------------------
        # 4. Quality Gate Acceptance Decision
        # -----------------------------------------------------------------------
        threshold = app_settings.quality_gate_min_score  # default 40.0%
        is_accepted = composite_score >= threshold

        error_message = None if is_accepted else REJECTION_MESSAGE

        is_blurry = laplacian_variance < 80.0
        is_underexposed = mean_brightness < 55.0
        is_overexposed = mean_brightness > 225.0

        logger.info(
            "Quality gate evaluated: score=%.2f (sharpness=%.2f, brightness=%.2f, accepted=%s)",
            composite_score,
            sharpness_score,
            brightness_score,
            is_accepted,
        )

        return {
            "is_accepted": is_accepted,
            "confidence_score": composite_score,
            "sharpness_score": round(sharpness_score, 2),
            "laplacian_variance": round(laplacian_variance, 2),
            "brightness_score": round(brightness_score, 2),
            "mean_brightness": round(mean_brightness, 2),
            "error_message": error_message,
            "details": {
                "image_width": int(width),
                "image_height": int(height),
                "aspect_ratio": round(float(width) / float(height), 2) if height > 0 else 0.0,
                "is_blurry": is_blurry,
                "is_underexposed": is_underexposed,
                "is_overexposed": is_overexposed,
            },
        }

    finally:
        # Zero Data Retention: Explicitly purge image matrices from memory
        del image
        del gray
        del laplacian
        gc.collect()

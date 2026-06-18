# app/core/image_processor.py - OpenCV preprocessing pipeline

import logging

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Improve selected image regions before OCR."""

    @staticmethod
    def preprocess(image: Image.Image, upscale_factor: int = 2, mode: str = "auto") -> Image.Image:
        try:
            mode = (mode or "auto").lower()
            if mode == "raw":
                return image.convert("RGB")

            cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
            height, width = cv_image.shape[:2]
            resized = cv2.resize(
                cv_image,
                (width * upscale_factor, height * upscale_factor),
                interpolation=cv2.INTER_CUBIC,
            )

            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

            if mode == "light":
                result = Image.fromarray(cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB))
                logger.debug("Image preprocessed with light mode: %s -> %s", image.size, result.size)
                return result

            if mode == "invert":
                inverted = cv2.bitwise_not(gray)
                result = Image.fromarray(cv2.cvtColor(inverted, cv2.COLOR_GRAY2RGB))
                logger.debug("Image preprocessed with invert mode: %s -> %s", image.size, result.size)
                return result

            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(filtered)

            if mode == "strong":
                thresholded = cv2.adaptiveThreshold(
                    enhanced,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    31,
                    11,
                )
            else:
                _, thresholded = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
            processed = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
            result = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_GRAY2RGB))

            logger.debug("Image preprocessed with %s mode: %s -> %s", mode, image.size, result.size)
            return result
        except Exception:
            logger.exception("Image preprocessing failed; using original image")
            return image

    @staticmethod
    def enhance_contrast(image: Image.Image) -> Image.Image:
        cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        return Image.fromarray(cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB))

    @staticmethod
    def denoise(image: Image.Image) -> Image.Image:
        cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        denoised = cv2.fastNlMeansDenoisingColored(cv_image, h=10)
        return Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))

    @staticmethod
    def sharpen(image: Image.Image) -> Image.Image:
        cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1],
        ])
        sharpened = cv2.filter2D(cv_image, -1, kernel)
        return Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))

# app/core/image_processor.py - OpenCV Preprocessing Pipeline

import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """OCR öncesi görüntü iyileştirme"""
    
    @staticmethod
    def preprocess(image: Image.Image, target_size: tuple = None) -> Image.Image:
        """
        OCR için görüntüyü işle:
        1. Resize (2-3x)
        2. Grayscale
        3. Bilateral Filter
        4. CLAHE
        5. Adaptive Threshold
        6. Optional Sharpen
        
        Args:
            image: PIL Image
            target_size: Hedef boyut (opsiyonel)
        
        Returns:
            İşlenmiş PIL Image
        """
        try:
            # PIL'i OpenCV format'ına çevir
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            print(f"[ImageProcessor] Step 0 - Original: {cv_image.shape}, min={cv_image.min()}, max={cv_image.max()}")
            
            # 1. Resize (2x upscale)
            height, width = cv_image.shape[:2]
            new_width = width * 2
            new_height = height * 2
            cv_image = cv2.resize(cv_image, (new_width, new_height), 
                                 interpolation=cv2.INTER_CUBIC)
            print(f"[ImageProcessor] Step 1 - Resized: {cv_image.shape}")
            
            # 2. Grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            print(f"[ImageProcessor] Step 2 - Grayscale: {gray.shape}, min={gray.min()}, max={gray.max()}")
            
            # 3. Bilateral Filter (gürültü azalt, kenarları koru)
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            print(f"[ImageProcessor] Step 3 - Bilateral Filter: min={filtered.min()}, max={filtered.max()}")
            
            # 4. CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(filtered)
            print(f"[ImageProcessor] Step 4 - CLAHE: min={enhanced.min()}, max={enhanced.max()}")
            
            # 5. Otsu Threshold (daha hafif)
            _, thresholded = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            black_pixels = np.sum(thresholded == 0)
            white_pixels = np.sum(thresholded == 255)
            total = black_pixels + white_pixels
            print(f"[ImageProcessor] Step 5 - Otsu Threshold: black={black_pixels/total*100:.1f}%, white={white_pixels/total*100:.1f}%")
            
            # 6. Morphology (opsiyonel - sadece çok küçük gürültüyü temizle)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
            processed = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
            black_pixels_after = np.sum(processed == 0)
            white_pixels_after = np.sum(processed == 255)
            print(f"[ImageProcessor] Step 6 - Morphology Open: black={black_pixels_after/total*100:.1f}%, white={white_pixels_after/total*100:.1f}%")
            
            # OpenCV'den PIL'e geri çevir (grayscale -> RGB)
            result = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_GRAY2RGB))
            
            logger.debug(f"Image preprocessed: {image.size} -> {result.size}")
            print(f"[ImageProcessor] Final result size: {result.size}")
            return result
        
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return image
    
    @staticmethod
    def enhance_contrast(image: Image.Image) -> Image.Image:
        """Kontrast artır"""
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Histogram equalization
        equalized = cv2.equalizeHist(gray)
        
        return Image.fromarray(cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB))
    
    @staticmethod
    def denoise(image: Image.Image) -> Image.Image:
        """Gürültü azalt"""
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        denoised = cv2.fastNlMeansDenoisingColored(cv_image, h=10)
        return Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def sharpen(image: Image.Image) -> Image.Image:
        """Keskinleştir"""
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        
        sharpened = cv2.filter2D(cv_image, -1, kernel)
        return Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))

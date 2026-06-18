# app/core/cache_manager.py - Cache Sistemi

import hashlib
import json
from PIL import Image
import io
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Hash-tabanlı cache sistem
    Key: hash(image + position + url + language)
    """
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, dict] = {}
        self.max_size = max_size
    
    def generate_key(self, image: Image.Image, coordinates: dict, request_data: dict) -> Optional[str]:
        """
        Cache key oluştur
        hash(image_hash + coordinates + url + language)
        """
        try:
            # Image hash
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_hash = hashlib.md5(image_bytes.getvalue()).hexdigest()
            
            # Koordinat ve language
            coords_str = json.dumps(coordinates, sort_keys=True)
            source_lang = request_data.get('source_lang', 'auto')
            target_lang = request_data.get('target_lang', 'tr')
            
            # Combined hash
            combined = f"{image_hash}:{coords_str}:{source_lang}:{target_lang}"
            cache_key = hashlib.sha256(combined.encode()).hexdigest()
            
            return cache_key
        
        except Exception as e:
            logger.error(f"Cache key generation error: {e}")
            return None
    
    def get(self, key: Optional[str]) -> Optional[Any]:
        """Cache'ten al"""
        try:
            if not key:
                return None

            if key in self.cache:
                entry = self.cache[key]
                # TTL kontrol et (24 saat)
                if datetime.now() - entry['timestamp'] < timedelta(hours=24):
                    logger.debug(f"Cache hit: {key}")
                    return entry['value']
                else:
                    del self.cache[key]
            
            return None
        
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: Optional[str], value: Any) -> bool:
        """Cache'e kaydet"""
        try:
            if not key:
                return False

            if len(self.cache) >= self.max_size:
                # En eski entry'yi sil
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]
            
            self.cache[key] = {
                'value': value,
                'timestamp': datetime.now()
            }
            
            logger.debug(f"Cache set: {key}")
            return True
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def clear(self) -> None:
        """Cache temizle"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Cache istatistikleri"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'usage_percent': (len(self.cache) / self.max_size) * 100
        }

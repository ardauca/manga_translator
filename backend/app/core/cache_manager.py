# app/core/cache_manager.py - In-memory cache

import hashlib
import io
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from PIL import Image

logger = logging.getLogger(__name__)


class CacheManager:
    """Small TTL cache keyed by selected image, coordinates and languages."""

    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: Dict[str, dict] = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)

    def generate_key(self, image: Image.Image, coordinates: dict, request_data: dict) -> Optional[str]:
        try:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_hash = hashlib.md5(image_bytes.getvalue()).hexdigest()
            coords_hash = json.dumps(coordinates, sort_keys=True)
            source_lang = request_data.get("source_lang", "auto")
            target_lang = request_data.get("target_lang", "tr")
            return hashlib.sha256(f"{image_hash}:{coords_hash}:{source_lang}:{target_lang}".encode()).hexdigest()
        except Exception:
            logger.exception("Cache key generation failed")
            return None

    def get(self, key: Optional[str]) -> Optional[Any]:
        if not key:
            return None

        entry = self.cache.get(key)
        if not entry:
            return None

        if datetime.now() - entry["timestamp"] >= self.ttl:
            del self.cache[key]
            return None

        logger.debug("Cache hit: %s", key)
        return entry["value"]

    def set(self, key: Optional[str], value: Any) -> bool:
        if not key:
            return False

        try:
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda item: self.cache[item]["timestamp"])
                del self.cache[oldest_key]

            self.cache[key] = {
                "value": value,
                "timestamp": datetime.now(),
            }
            logger.debug("Cache set: %s", key)
            return True
        except Exception:
            logger.exception("Cache set failed")
            return False

    def clear(self) -> None:
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "usage_percent": (len(self.cache) / self.max_size) * 100,
        }

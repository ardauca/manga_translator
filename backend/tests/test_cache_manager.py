import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from core.cache_manager import CacheManager


class CacheManagerTests(unittest.TestCase):
    def test_set_and_get_value(self):
        cache = CacheManager(max_size=2)
        self.assertTrue(cache.set("a", {"translation": "Merhaba"}))
        self.assertEqual(cache.get("a"), {"translation": "Merhaba"})

    def test_evicts_oldest_entry(self):
        cache = CacheManager(max_size=1)
        cache.set("a", 1)
        cache.set("b", 2)
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from core.text_cleaner import TextCleaner


class TextCleanerTests(unittest.TestCase):
    def test_joins_hyphenated_english_fragments(self):
        self.assertEqual(
            TextCleaner.clean("YOU'RE MOST PROMIS- ING.", "en"),
            "You're Most Promising.",
        )

    def test_normalizes_punctuation_spacing(self):
        self.assertEqual(
            TextCleaner.clean("hello  ,   world !", "auto"),
            "hello, world!",
        )


if __name__ == "__main__":
    unittest.main()

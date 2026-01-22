"""Main extractor class for gym schedule extraction."""

import os
from typing import Optional
from .ocr_engine import OcrEngine


class GymScheduleExtractor:
    """Extract gym schedules from images and save to files."""
    
    def __init__(self, ocr_engine: Optional[OcrEngine] = None):
        self.ocr_engine = ocr_engine

    def extract(self, image_path):
        """Extract schedule from an image."""
        if self.ocr_engine is None:
            raise ValueError("OCR engine is required for extraction")
        return self.ocr_engine.extract_image_as_json(image_path)

    def save_to_file(self, content, output_path):
        """Saves content to a file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved extracted JSON to {output_path}")

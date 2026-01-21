"""Main extractor class for gym schedule extraction."""

from .ocr_engine import OcrEngine


class GymScheduleExtractor:
    """Extract gym schedules from images and save to files."""
    
    def __init__(self, ocr_engine: OcrEngine):
        self.ocr_engine = ocr_engine

    def extract(self, image_path):
        """Extract schedule from an image."""
        return self.ocr_engine.extract_image_as_json(image_path)

    def save_to_file(self, content, output_path):
        """Saves content to a file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved extracted JSON to {output_path}")

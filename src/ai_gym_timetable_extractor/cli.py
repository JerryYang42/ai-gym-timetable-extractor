"""Command-line interface for the gym timetable extractor."""

import os
import sys
from dotenv import load_dotenv

# Handle both direct execution and module import
if __name__ == "__main__" and __package__ is None:
    # Add the parent directory to sys.path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ai_gym_timetable_extractor.extractor import GymScheduleExtractor
    from ai_gym_timetable_extractor.ocr_engine import GeminiOcrEngine
else:
    from .extractor import GymScheduleExtractor
    from .ocr_engine import GeminiOcrEngine

IMG_DIR = "data"
OUTPUT_DIR = "temp"

def batch_image_info_extraction(img_dir: str, output_dir: str):
    """Batch process all images in the IMG_DIR and save results to OUTPUT_DIR."""
    gemini_ocr_engine = GeminiOcrEngine()
    extractor = GymScheduleExtractor(ocr_engine=gemini_ocr_engine)
    
    # Process images
    for filename in os.listdir(IMG_DIR):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        
        input_path = os.path.join(IMG_DIR, filename)
        output_filename = os.path.splitext(filename)[0] + ".json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        json_result = extractor.extract(input_path)
        extractor.save_to_file(json_result, output_path)
        print(f"Processed {input_path} -> {output_path}")

def main():
    """Main CLI entry point."""
    load_dotenv()
    batch_image_info_extraction(IMG_DIR, OUTPUT_DIR)
    


if __name__ == "__main__":
    main()

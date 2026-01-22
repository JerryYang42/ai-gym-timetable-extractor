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


def main():
    """Main CLI entry point."""
    # Load environment variables from .env file
    load_dotenv()
    
    gemini_ocr_engine = GeminiOcrEngine()
    extractor = GymScheduleExtractor(ocr_engine=gemini_ocr_engine)
    
    # Process images
    filenames = ["IMG_7191"]
    for name in filenames:
        input_path = f"data/{name}.PNG"
        output_path = f"temp/{name}.json"
        
        if not os.path.exists(input_path):
            print(f"Warning: {input_path} not found, skipping...")
            continue
            
        json_result = extractor.extract(input_path)
        extractor.save_to_file(json_result, output_path)


if __name__ == "__main__":
    main()

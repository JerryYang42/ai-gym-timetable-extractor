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
    from ai_gym_timetable_extractor.aggregator import GymScheduleAggregator
else:
    from .extractor import GymScheduleExtractor
    from .ocr_engine import GeminiOcrEngine
    from .aggregator import GymScheduleAggregator

IMG_DIR = "data/img"
JSON_DIR = "data/json"
AGG_JSON_DIR = "data/aggregated"

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
        output_path = os.path.join(JSON_DIR, output_filename)
        
        json_result = extractor.extract(input_path)
        extractor.save_to_file(json_result, output_path)
        print(f"Processed {input_path} -> {output_path}")

def aggregate_results(output_dir: str, aggregated_output: str):
    """Aggregate all JSON results in OUTPUT_DIR into a single database-ready JSON file.
    
    Args:
        output_dir: Directory containing individual JSON extraction results
        aggregated_output: Output filename for the aggregated database
    """
    aggregator = GymScheduleAggregator()
    all_classes = aggregator.aggregate_json_files(output_dir)
    
    # Save aggregated results
    aggregator.save_aggregated_json(all_classes, aggregated_output)
    print(f"\n✓ Aggregated json saved to: {aggregated_output}")

def main():
    """Main CLI entry point."""
    load_dotenv()
    
    # Step 1: Batch extract from images
    print("Step 1: Extracting schedules from images...")
    batch_image_info_extraction(IMG_DIR, JSON_DIR)
    
    # Step 2: Aggregate results
    print("\nStep 2: Aggregating results...")
    aggregate_results(JSON_DIR,  aggregated_output=os.path.join(AGG_JSON_DIR, "aggregated_schedule.json"))
    


if __name__ == "__main__":
    main()

"""Command-line interface for the gym timetable extractor."""

import argparse
import logging
import os
import sys
from dotenv import load_dotenv

log = logging.getLogger(__name__)

# Handle both direct execution and module import
if __name__ == "__main__" and __package__ is None:
    # Add the parent directory to sys.path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ai_gym_timetable_extractor.extractor import GymScheduleExtractor
    from ai_gym_timetable_extractor.ocr_engine import GeminiOcrEngine
    from ai_gym_timetable_extractor.aggregator import GymScheduleAggregator
    from ai_gym_timetable_extractor.database import get_database
else:
    from .extractor import GymScheduleExtractor
    from .ocr_engine import GeminiOcrEngine
    from .aggregator import GymScheduleAggregator
    from .database import get_database

IMG_DIR = "data/img"
JSON_DIR = "data/json"
AGG_JSON_DIR = "data/aggregated"

def configure_logging(log_level: str = None, log_file: str = None):
    """Configure logging with customizable level and output file.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses LOG_FILE env var or 'gym_extractor.log'
    """
    # Determine log level from parameter, env var, or default to INFO
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Determine log file from parameter, env var, or default
    if log_file is None:
        log_file = os.getenv('LOG_FILE', 'gym_extractor.log')
    
    # Configure handlers
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

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
        log.info(f"Processed {input_path} -> {output_path}")

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
    log.info(f"✓ Aggregated json saved to: {aggregated_output}")

def load_aggregated_results_to_db(aggregated_json_path: str):
    """Load aggregated JSON results into the database."""
    db = get_database()
    db.load_delta_from_json_file(aggregated_json_path)
    log.info("✓ Loaded aggregated results into database.")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Extract and aggregate gym timetable schedules from images'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: INFO or LOG_LEVEL env var)'
    )
    parser.add_argument(
        '--log-file',
        help='Path to log file (default: gym_extractor.log or LOG_FILE env var)'
    )
    
    args = parser.parse_args()
    
    load_dotenv()
    configure_logging(log_level=args.log_level, log_file=args.log_file)
    
    # Step 1: Batch extract from images
    log.info("Step 1: Extracting schedules from images...")
    batch_image_info_extraction(IMG_DIR, JSON_DIR)
    
    # Step 2: Aggregate results
    log.info("\nStep 2: Aggregating results...")
    aggregate_results(JSON_DIR,  aggregated_output=os.path.join(AGG_JSON_DIR, "aggregated_schedule.json"))

    # Step 3: Load into database
    log.info("\nStep 3: Loading aggregated results into database...")
    aggregated_json_path = os.path.join(AGG_JSON_DIR, "aggregated_schedule.json")
    load_aggregated_results_to_db(aggregated_json_path)


if __name__ == "__main__":
    main()

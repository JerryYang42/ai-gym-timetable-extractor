from .parser import GymScheduleParser
from .models import GymClass, GymSchedule
from typing import List
import os

class GymScheduleAggregator:

    def __init__(self):
        self.parser = GymScheduleParser()

    def aggregate_json_files(self, directory: str) -> List[GymClass]:
        """Load all JSON files from directory and aggregate into a list of GymClass objects.
        
        Args:
            directory: Path to directory containing JSON files
            
        Returns:
            List of deduplicated GymClass objects
        """
        all_classes: List[GymClass] = []
        
        if not os.path.exists(directory):
            print(f"Warning: Directory {directory} does not exist")
            return all_classes
        
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith('.json'):
                continue
            
            classes = self.parser.parse(os.path.join(directory, filename))
            all_classes.extend(classes)
        
        return all_classes
    
    def save_aggregated_json(self, classes: List[GymClass], output_path: str):
        """Save aggregated classes to a JSON file ready for database import.
        
        Args:
            classes: List of GymClass objects
            output_path: Path to save the aggregated JSON file
        """
        schedule = GymSchedule(classes=classes)
        
        # Create directory if needed (handle both absolute and relative paths)
        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Use model_dump_json for clean JSON output
            f.write(schedule.model_dump_json(indent=2))
        
        print(f"Saved {len(classes)} classes to {output_path}")

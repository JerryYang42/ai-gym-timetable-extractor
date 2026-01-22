import os
from typing import List
import json
from .models import GymSchedule
from .models import GymClass


class GymScheduleParser:
    def parse(self, filepath: str) -> List[GymClass]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            all_classes: List[GymClass] = []

            if 'classes' in data:
                schedule = GymSchedule(**data)
                all_classes.extend(schedule.classes)
            return all_classes

            # Parse the schedule
            # if 'classes' in data:
            #     schedule = GymSchedule(**data)
            #     for gym_class in schedule.classes:
            #         # Create a unique key for deduplication
            #         # A class is unique by: date, timeslot, activity, and venue
            #         unique_key = (
            #             gym_class.date,
            #             gym_class.timeslot,
            #             gym_class.activity,
            #             gym_class.venue
            #         )
                    
            #         if unique_key not in seen_classes:
            #             seen_classes.add(unique_key)
            #             all_classes.append(gym_class)
            #         else:
            #             print(f"Duplicate found: {gym_class.activity} on {gym_class.date} at {gym_class.timeslot}")
                        
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
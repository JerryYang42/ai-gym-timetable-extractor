import os
import certifi

# IMPORTANT: Set SSL environment variables before importing google.genai
# This forces the library to use the certifi bundle for SSL verification
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import dotenv
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import json


class GymClass(BaseModel):
    """Represents a single gym class with all relevant details."""
    date: str = Field(..., description="Date of the class (e.g., '2024-01-15')")
    day_of_week: str = Field(..., description="Day of week (e.g., 'Monday')")
    timeslot: str = Field(..., description="Time slot (e.g., '10:00-11:00')")
    activity: str = Field(..., description="Activity name (e.g., 'Yoga')")
    venue: str = Field(..., description="Venue/location of the class")
    class_type: str = Field(..., description="Type of class (e.g., 'Group', 'Personal')")
    vacancy: int = Field(..., description="Number of available spots")
    modified_at: Optional[datetime] = Field(default_factory=datetime.now, description="Last modification timestamp")


class GymSchedule(BaseModel):
    """Represents a collection of gym classes."""
    classes: List[GymClass] = Field(..., description="List of gym classes in the schedule")


class GymScheduleDatabase:
    """In-memory database for storing and managing gym class schedules."""
    
    def __init__(self):
        # Dictionary with composite key: (date, timeslot, activity) -> GymClass
        self.classes: Dict[tuple, GymClass] = {}
    
    def _get_key(self, gym_class: GymClass) -> tuple:
        """Generate composite key for a gym class."""
        return (gym_class.date, gym_class.timeslot, gym_class.activity)
    
    def add_or_update(self, gym_class: GymClass) -> bool:
        """
        Add a new class or update existing one.
        Returns True if updated, False if newly added.
        """
        key = self._get_key(gym_class)
        is_update = key in self.classes
        
        # Update modified_at timestamp
        gym_class.modified_at = datetime.now()
        
        self.classes[key] = gym_class
        return is_update
    
    def add_or_update_batch(self, gym_classes: List[GymClass]) -> Dict[str, int]:
        """
        Add or update multiple classes.
        Returns statistics about the operation.
        """
        stats = {"added": 0, "updated": 0}
        for gym_class in gym_classes:
            is_update = self.add_or_update(gym_class)
            if is_update:
                stats["updated"] += 1
            else:
                stats["added"] += 1
        return stats
    
    def get_all(self) -> List[GymClass]:
        """Get all classes in the database."""
        return list(self.classes.values())
    
    def get_by_date(self, date: str) -> List[GymClass]:
        """Get all classes for a specific date."""
        return [c for c in self.classes.values() if c.date == date]
    
    # TODO: Add more query methods (by activity, by venue, by availability, etc.)
    # TODO: Add persistence (save to file, load from file)
    # TODO: Add validation for date ranges and conflict detection


class GymScheduleExtractor:
    def __init__(self, model_name="gemini-2.0-flash"):
        dotenv.load_dotenv()
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Initialize client cleanly without passing unsupported http_options
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        
        # Initialize in-memory database
        self.database = GymScheduleDatabase()

    def extract(self, image_path: str) -> GymSchedule:
        """
        Uploads image and extracts schedule details using structured output.
        Returns a validated GymSchedule object.
        """
        print(f"Uploading {image_path}...")
        my_file = self.client.files.upload(file=image_path)

        print("Generating content with structured output...")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                my_file, 
                "This is a screenshot of my gym timetable. Extract out the schedule details, including date, day of week, timeslot, activity, venue, class type, and vacancy for each class."
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": GymSchedule,
            }
        )
        
        # Parse and validate the response using Pydantic
        schedule_data = json.loads(response.text)
        schedule = GymSchedule(**schedule_data)
        
        return schedule
    
    def extract_and_store(self, image_path: str) -> Dict[str, any]:
        """
        Extract schedule from image and store in database.
        Returns statistics about the operation.
        """
        schedule = self.extract(image_path)
        stats = self.database.add_or_update_batch(schedule.classes)
        
        print(f"Processed {len(schedule.classes)} classes: {stats['added']} added, {stats['updated']} updated")
        return {
            "total_classes": len(schedule.classes),
            "stats": stats,
            "schedule": schedule
        }

    def save_to_file(self, content, output_path):
        """Saves content to a file."""
        with open(output_path, "w", encoding="utf-8") as f:
            if isinstance(content, (GymSchedule, GymClass)):
                f.write(content.model_dump_json(indent=2))
            else:
                f.write(content)
        print(f"Saved extracted JSON to {output_path}")
    
    def clean_up_json_markdown(self, text):
        """Cleans up markdown code blocks from JSON text."""
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

if __name__ == "__main__":
    # Example usage with structured output and in-memory database
    extractor = GymScheduleExtractor()
    
    # TODO: Replace with actual image files
    # filenames = ["IMG_7195", "IMG_7196", "IMG_7197"]
    # for name in filenames:
    #     input_path = f"data/{name}.PNG"
    #     output_path = f"output/{name}.json"
    #     
    #     # Extract and store in database
    #     result = extractor.extract_and_store(input_path)
    #     
    #     # Save to file
    #     extractor.save_to_file(result["schedule"], output_path)
    #     
    #     print(f"Database now contains {len(extractor.database.get_all())} classes")
    
    # TODO: Add example for querying the database
    # all_classes = extractor.database.get_all()
    # print(f"Total classes in database: {len(all_classes)}")
    
    # TODO: Add example for date-based queries
    # classes_on_date = extractor.database.get_by_date("2024-01-15")
    # print(f"Classes on 2024-01-15: {len(classes_on_date)}")
    
    print("GymScheduleExtractor initialized with Pydantic models and in-memory database.")
    print("Uncomment the code above to process gym timetable images.")

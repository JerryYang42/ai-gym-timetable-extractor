# ai-gym-timetable-extractor

This is a project that uses AI to extract course timetable from screenshots and format it into an AI-readable JSON file.

## Features

- **OCR Extraction**: Uses Google's Gemini AI to extract gym timetable information from screenshots
- **Structured Output**: Leverages Pydantic models and Gemini's response_schema for guaranteed valid JSON
- **In-Memory Database**: Stores extracted classes with automatic conflict resolution
- **Duplicate Handling**: Automatically updates vacancy information when the same class is uploaded twice

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set up your environment:
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY to the .env file
   ```

## Usage

### Basic Usage

```python
from GymScheduleExtractor import GymScheduleExtractor

# Initialize the extractor
extractor = GymScheduleExtractor()

# Extract schedule from an image
result = extractor.extract_and_store("path/to/gym_timetable.png")

# Access the database
all_classes = extractor.database.get_all()
print(f"Total classes: {len(all_classes)}")

# Query by date
classes_on_date = extractor.database.get_by_date("2024-01-15")
```

### Data Models

The system uses Pydantic models for data validation:

- **GymClass**: Represents a single gym class with fields:
  - `date`: Date of the class (e.g., "2024-01-15")
  - `day_of_week`: Day of week (e.g., "Monday")
  - `timeslot`: Time slot (e.g., "10:00-11:00")
  - `activity`: Activity name (e.g., "Yoga")
  - `venue`: Venue/location of the class
  - `class_type`: Type of class (e.g., "Group", "Personal")
  - `vacancy`: Number of available spots
  - `modified_at`: Last modification timestamp

- **GymSchedule**: Collection of gym classes

### In-Memory Database

The `GymScheduleDatabase` class provides:
- Automatic duplicate detection based on (date, timeslot, activity)
- Conflict resolution by updating existing entries
- Query methods for accessing stored classes

## TODO

The following features are planned but not yet implemented:

- [ ] Advanced query methods (by activity, by venue, by availability)
- [ ] Persistence layer (save to file, load from file)
- [ ] Date range validation
- [ ] Complex conflict detection
- [ ] Batch processing optimizations
- [ ] Export to different formats (CSV, iCal)

## Requirements

- Python >= 3.10
- google-genai >= 0.2.0
- python-dotenv >= 1.0.0
- pydantic >= 2.0.0
- certifi >= 2024.0.0

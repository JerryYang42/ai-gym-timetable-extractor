from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class GymClass(BaseModel):
    """Represents a single gym class with all relevant details."""
    date: str = Field(..., description="Date of the class (e.g., 'YYYY-MM-DD')")
    day_of_week: str = Field(..., description="Day of week (e.g., 'Monday')")
    timeslot: str = Field(..., description="Time slot (e.g., '10:00')")
    activity: str = Field(..., description="Activity name (e.g., 'Yoga')")
    venue: str = Field(..., description="Venue/location of the class")
    class_type: str = Field(..., description="Type of class (e.g., 'Group', 'Personal')")
    vacancy: int = Field(..., description="Number of available spots")
    modified_at: Optional[datetime] = Field(default_factory=datetime.now, description="Last modification timestamp")


class GymSchedule(BaseModel):
    """Represents a collection of gym classes."""
    classes: List[GymClass] = Field(..., description="List of gym classes in the schedule")


if __name__ == "__main__":
    # Example usage
    example_class = GymClass(
        date="2024-01-15",
        day_of_week="Monday",
        timeslot="10:00",
        activity="Yoga",
        venue="Studio A",
        class_type="Group",
        vacancy=5
    )

    schedule = GymSchedule(classes=[example_class])
    print(schedule.model_dump_json(indent=4))


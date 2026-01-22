"""OCR Engine implementations for extracting text from images."""

import os
import certifi
import datetime

from .models import GymSchedule

# IMPORTANT: Set SSL environment variables before importing google.genai
# This forces the library to use the certifi bundle for SSL verification
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
from google import genai

from .constants import ENV_GEMINI_API_KEY, ENV_GEMINI_MODEL_NAME


class OcrEngine:
    """Base class for OCR engines."""
    
    def __init__(self):
        pass

    def extract_image_as_json(self, image_path: str) -> str:
        """Extract text from image and return as JSON string."""
        pass


class GeminiOcrEngine(OcrEngine):
    """OCR engine using Google's Gemini API."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get(ENV_GEMINI_API_KEY)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.model_name = os.environ.get(ENV_GEMINI_MODEL_NAME)
        self.client = genai.Client(api_key=self.api_key)

    def extract_image_as_json(self, image_path: str) -> str:
        """Extract gym timetable from image using Gemini API."""
        my_file = self.client.files.upload(file=image_path)

        print("Sending OCR request to Gemini API...")
        today = datetime.date.today().isoformat()
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                my_file, 
                "This is a screenshot of my gym timetable. Extract out "  +
                "the schedule details, including date, day of week, "     + 
                "timeslot, activity, venue, class type, and vacancy for " +
                f"each class. Date should be in a near future of {today} " +
                "and formatted as 'YYYY-MM-DD'."],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": GymSchedule,
                }
        )
        return self.clean_up_json_markdown(response.text)
    
    def clean_up_json_markdown(self, text):
        """Cleans up markdown code blocks from JSON text."""
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

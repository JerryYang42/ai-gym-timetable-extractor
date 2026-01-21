import os
import certifi

# IMPORTANT: Set SSL environment variables before importing google.genai
# This forces the library to use the certifi bundle for SSL verification
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
from google import genai

from Constants import ENV_GEMINI_API_KEY, ENV_GEMINI_MODEL_NAME

class OcrEngine():
    def __init__(self):
        pass

    def extract_image_as_json(self, image_path: str) -> str:
        pass


class GeminiOcrEngine(OcrEngine):
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get(ENV_GEMINI_API_KEY)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.model_name = os.environ.get(ENV_GEMINI_MODEL_NAME)
        self.client = genai.Client(api_key=self.api_key)

    def extract_image_as_json(self, image_path: str) -> str:
        my_file = self.client.files.upload(file=image_path)

        print("Generating content...")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[my_file, "This is a screenshot of my gym timetable. Extract out the schedule details in json, including date, day of week, timeslot, activity, venue, class type, vacancy."],
        )
        return self.clean_up_json_markdown(response.text)
    
    def clean_up_json_markdown(self, text):
        """Cleans up markdown code blocks from JSON text."""
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
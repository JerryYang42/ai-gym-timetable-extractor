import os
import certifi

# IMPORTANT: Set SSL environment variables before importing google.genai
# This forces the library to use the certifi bundle for SSL verification
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import dotenv
from google import genai

class GymScheduleExtractor:
    def __init__(self, model_name="gemini-2.0-flash"):
        dotenv.load_dotenv()
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Initialize client cleanly without passing unsupported http_options
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def extract(self, image_path):
        """Uploads image and extracts schedule details."""
        print(f"Uploading {image_path}...")
        my_file = self.client.files.upload(file=image_path)

        print("Generating content...")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[my_file, "This is a screenshot of my gym timetable. Extract out the schedule details in json, including date, day of week, timeslot, activity, venue, class type, vacancy."],
        )
            
        return self.clean_up_json_markdown(response.text)

    def save_to_file(self, content, output_path):
        """Saves content to a file."""
        with open(output_path, "w", encoding="utf-8") as f:
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
    extractor = GymScheduleExtractor()
    json_result = extractor.extract("data/IMG_7193.PNG")
    print(json_result)
    extractor.save_to_file(json_result, "output/IMG_7193.json")
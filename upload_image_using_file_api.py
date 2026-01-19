import os
import certifi

# IMPORTANT: Set SSL environment variables before importing google.genai
# This forces the library to use the certifi bundle for SSL verification
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import dotenv
from google import genai

dotenv.load_dotenv()

# Initialize client cleanly without passing unsupported http_options
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

my_file = client.files.upload(file="data/IMG_7191.PNG")

# Generate content
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[my_file, "This is a screenshot of my gym timetable. Extract out the schedule details in json, including date, day of week, timeslot, activity, venue, class type, vacancy."],
)

print(response.text)
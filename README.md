# ai-gym-timetable-extractor

This is a project that uses AI to extract course timetable from screenshots and format it into an AI-readable JSON file.

## Project Structure

```
ai-gym-timetable-extractor/
├── src/
│   └── ai_gym_timetable_extractor/
│       ├── __init__.py
│       ├── cli.py           # Command-line interface
│       ├── constants.py     # Configuration constants
│       ├── extractor.py     # Main extractor logic
│       └── ocr_engine.py    # OCR engine implementations
├── tests/
│   ├── __init__.py
│   └── fixtures/            # Test data (committed to git)
├── data/                    # Development data (gitignored)
├── output/                  # Extracted JSON outputs (gitignored)
├── .env                     # Environment variables (not in git)
├── pyproject.toml           # Project configuration
├── run.sh                   # Convenience script
└── README.md
```

## Setup

1. Install dependencies using uv:
   ```bash
   uv sync
   ```

2. Create a `.env` file with your Gemini API credentials:
   ```
   GEMINI_MODEL_NAME=gemini-2.0-flash
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Using the run script (easiest)

```bash
./run.sh
```

### Direct Execution

```bash
python3 src/ai_gym_timetable_extractor/cli.py
```

### As a Module

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python3 -m ai_gym_timetable_extractor.cli
```

### In Python Code

```python
import sys
sys.path.insert(0, 'src')

from ai_gym_timetable_extractor import GymScheduleExtractor, GeminiOcrEngine

# Initialize the extractor
ocr_engine = GeminiOcrEngine()
extractor = GymScheduleExtractor(ocr_engine=ocr_engine)

# Extract from an image
json_result = extractor.extract("data/image.PNG")

# Save to file
extractor.save_to_file(json_result, "output/result.json")
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
ruff format .
```

Type checking:
```bash
mypy src/ai_gym_timetable_extractor
```

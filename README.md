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

3. (Optional) Configure logging in `.env`:
   ```
   LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
   LOG_FILE=gym_extractor.log        # Path to log file
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

### Using the installed command (after uv sync)

```bash
gym-schedule-extract
```

#### CLI Options

```bash
# Set log level via command line
gym-schedule-extract --log-level DEBUG

# Specify custom log file
gym-schedule-extract --log-file /path/to/custom.log

# Combine options
gym-schedule-extract --log-level WARNING --log-file errors.log
```

#### Logging

The application logs to both console and file (`gym_extractor.log` by default). You can configure logging through:

1. **Environment variables** (in `.env`):
   ```
   LOG_LEVEL=DEBUG
   LOG_FILE=custom_log.log
   ```

2. **Command-line arguments**:
   ```bash
   gym-schedule-extract --log-level DEBUG --log-file debug.log
   ```

3. **Priority**: CLI args > Environment variables > Defaults

**Log levels**:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

##  In Python Code

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

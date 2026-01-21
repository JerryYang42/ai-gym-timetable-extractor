"""AI Gym Timetable Extractor - Extract course timetables from screenshots using AI."""

__version__ = "0.1.0"

from .extractor import GymScheduleExtractor
from .ocr_engine import OcrEngine, GeminiOcrEngine

__all__ = ["GymScheduleExtractor", "OcrEngine", "GeminiOcrEngine"]

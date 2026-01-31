import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
RESULT_FOLDER = BASE_DIR / 'static' / 'results'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

MODEL_NAME = "yolo26s"
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45

HISTORY_FILE = BASE_DIR / 'history.json'

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)
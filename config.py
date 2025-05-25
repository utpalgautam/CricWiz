import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants (add more as needed)
SEARCH_SLEEP_INTERVAL = 5
SEARCH_NUM_RESULTS = 2
SEARCH_TIMEFRAME = "1 month"
OLLAMA_MODEL = "llama3.2"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

# Centralized Logger setup to avoid duplicate logs
logger = logging.getLogger("cricfan")
logger.setLevel(logging.INFO)

# Clear any existing handlers to prevent duplicates
if logger.hasHandlers():
    logger.handlers.clear()

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
ch.setFormatter(formatter)

# Add handler
logger.addHandler(ch)

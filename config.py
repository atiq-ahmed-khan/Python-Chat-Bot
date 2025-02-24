# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables. Please check your .env file.")

PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
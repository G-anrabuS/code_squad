import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# GitHub auth
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
JWT_SECRET = os.getenv("JWT_SECRET")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_DISTANCE = os.getenv("QDRANT_DISTANCE", "Cosine")

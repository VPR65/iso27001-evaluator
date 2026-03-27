import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./iso27001.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-please-use-strong-key")
ALGORITHM = "HS256"
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "8"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
BACKUP_DIR = os.getenv("BACKUP_DIR", "./backups")

# AI Configuration
AI_MODE = os.getenv("AI_MODE", "nvidia")  # nvidia | ollama | anthropic | openai
AI_MODEL = os.getenv("AI_MODEL", "meta/llama-3.1-70b-instruct")
AI_LOCAL_URL = os.getenv("AI_LOCAL_URL", "http://localhost:11434")
AI_LOCAL_MODEL = os.getenv("AI_LOCAL_MODEL", "llama3.2")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
ALLOW_EXTERNAL_AI = os.getenv("ALLOW_EXTERNAL_AI", "false").lower() == "true"

# Available AI models for GUI selection
AVAILABLE_MODELS = [
    {
        "id": "meta/llama-3.1-70b-instruct",
        "name": "Llama 3.1 70B Instruct",
        "provider": "NVIDIA",
    },
    {
        "id": "meta/llama-3.1-405b-instruct",
        "name": "Llama 3.1 405B Instruct",
        "provider": "NVIDIA",
    },
    {
        "id": "mistralai/mistral-large-2",
        "name": "Mistral Large 2",
        "provider": "NVIDIA",
    },
    {
        "id": "mistralai/mixtral-8x22b-instruct-v0.1",
        "name": "Mixtral 8x22B",
        "provider": "NVIDIA",
    },
    {"id": "google/gemma-2-27b-it", "name": "Gemma 2 27B", "provider": "NVIDIA"},
    {"id": "llama3.2", "name": "Llama 3.2 (Local)", "provider": "Ollama"},
    {"id": "mistral", "name": "Mistral 7B (Local)", "provider": "Ollama"},
    {"id": "llama3.1", "name": "Llama 3.1 (Local)", "provider": "Ollama"},
]

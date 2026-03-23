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

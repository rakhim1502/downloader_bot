"""
Loyiha konfiguratsiyasi va sozlamalari.
"""
import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin ID (loglar va xatoliklar uchun)
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Log darajasi
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Telegram limitlari
MAX_FILE_SIZE_MB = 50  # Telegram bot API limiti: 50MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Timeout sozlamalari
REQUEST_TIMEOUT = 60  # soniya

# Ishchi papkalar
DOWNLOAD_DIR = "downloads"
TEMP_DIR = "temp"

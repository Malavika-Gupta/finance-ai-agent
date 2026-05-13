import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

SEND_MODE = os.getenv("SEND_MODE", "DRY_RUN")
'''Lectura de .env y constantes (placeholder)'''
# shared/config.py
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    ENV: str = os.getenv("ENV", "dev")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    TZ: str = os.getenv("TZ", "America/Bogota")

    DB_HOST: str = os.getenv("DB_HOST", "mysql")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))  # interno del contenedor
    DB_NAME: str = os.getenv("DB_NAME", "project_ops")
    DB_USER: str = os.getenv("DB_USER", "project_ops_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "project_ops_pass")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")

settings = Settings()

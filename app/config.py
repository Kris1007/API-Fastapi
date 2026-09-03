# Pydantic models provide to check whether the environment variables are passed with the correct type and hence returns 
# error if not thats what this files does

from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        # Resolves .env relative to this file's location (app/../.env = project root)
        env_file = str(Path(__file__).parent.parent / ".env")

settings = Settings()

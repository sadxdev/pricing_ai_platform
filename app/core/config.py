from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "pricing-ai"
    DATABASE_URL: str
    REDIS_URL: str
    REPORT_EMAIL : str
    REPORT_EMAIL_PASSWORD : str

    class Config:
        env_file = ".env"
        extra = "ignore"
settings = Settings()

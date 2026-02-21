from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "pricing-ai"
    DATABASE_URL: str
    SYNC_DATABASE_URL: str = ""
    REDIS_URL: str
    REPORT_EMAIL: str
    REPORT_EMAIL_PASSWORD: str

    # -----------------------------
    # Keycloak
    # -----------------------------
    KEYCLOAK_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "pricing-ai"
    KEYCLOAK_CLIENT_ID: str = "pricing-backend"
    KEYCLOAK_CLIENT_SECRET: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
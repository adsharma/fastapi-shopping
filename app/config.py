from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


app_config = AppConfig()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic import BaseSettings


class Settings(BaseSettings):

    SERVER_HOST: str = '0.0.0.0'
    SERVER_PORT: int = 4040


settings = Settings()

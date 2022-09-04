from pydantic import BaseSettings


class IOServiceSettings(BaseSettings):

    CLICK_INTERVAL: float = 0.1


class Settings(BaseSettings):

    IO_SERVICE = IOServiceSettings()


settings = Settings()

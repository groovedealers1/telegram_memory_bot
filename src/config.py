from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib


__all__ = 'settings',


class Settings(BaseSettings):
    BOT_TOKEN: str
    REDIS_PORT: int
    REDIS_HOST: str
    MONGO_HOST: str
    MONGO_PORT: int


    @property
    def BOT_TOKEN(self):
        return f'{self.BOT_TOKEN}'


    @property
    def REDIS_PORT(self):
        return self.REDIS_PORT


    @property
    def REDIS_HOST(self):
        return f'{self.REDIS_HOST}'


    @property
    def MONGO_HOST(self):
        return f'{self.MONGO_HOST}'


    @property
    def MONGO_PORT(self):
        return self.MONGO_PORT


    model_config = SettingsConfigDict(env_file=f'{pathlib.Path(__file__).parent.parent}/.env')


settings = Settings()

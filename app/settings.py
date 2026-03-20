from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BOT_CLIENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    id: str = "id"
    secret: str = "secret"
    guild_id: str = "guild_id"
    
class AppSettings(BaseSettings):
    bot: BotConfig = BotConfig()

if __name__ == "__main__":
    settings = AppSettings()
    print(settings)
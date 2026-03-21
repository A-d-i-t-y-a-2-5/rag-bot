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
    
class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = "api_key"
    model_name: str = "minimax-m2.7:cloud"
    
class RAGConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    collection_name: str = "documents"
    vector_size: int = 512
    
class AppSettings(BaseSettings):
    bot: BotConfig = BotConfig()
    llm: LLMConfig = LLMConfig()
    rag: RAGConfig = RAGConfig()

if __name__ == "__main__":
    settings = AppSettings()
    print(settings)
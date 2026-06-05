from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # LLM Settings
    llm_model: str = "ollama/llama3.2" # Using litellm convention
    api_base: Optional[str] = "http://localhost:11434"
    
    # Execution
    max_retries: int = 3
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()

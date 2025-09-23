from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
    # Chave da OpenAI
    OPENAI_API_KEY: str
    
    # Chaves da Evolution API (WhatsApp)
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    EVOLUTION_INSTANCE: str
    
    # Nova chave da Google Gemini API
    GOOGLE_API_KEY: str

settings = Settings()
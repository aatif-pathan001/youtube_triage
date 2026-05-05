from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env")

    # LLM settings
    model: str = "gemini-2.5-flash"
    temperature: float = 0.5

    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector store settings
    search_type: str = "similarity"
    top_k: int = 3

    database_url: str = ""
    gcp_project_id: str = ""
    test_database_url: str = ""


settings = Settings()

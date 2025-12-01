"""
Configuration management using Pydantic BaseSettings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    azure_openai_embedding_deployment: str
    azure_openai_api_version: str = "2025-01-01-preview"
    
    # Azure AI Search Configuration
    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index_name: str = "rag-index"
    
    # Application Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 30
    vector_dimensions: Optional[int] = None
    
    # CORS Origins
    cors_origins: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Global settings instance
settings = Settings()

from typing import List, Optional
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment or defaults."""
    
    PROJECT_NAME: str = "Cloud-Based Student Information Chatbot (CSIC)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment mode: development, test, staging, production
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # CORS Origins (comma-separated string in env, parsed to list)
    ALLOWED_ORIGINS: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:3000,"
        "https://csic-orpin.vercel.app,"
        "https://csic-portal.vercel.app"
    )
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # Supabase Credentials
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # JWT Authentication
    JWT_SECRET: str = "csic-dev-jwt-secret-key-32-chars-long-academic-project"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Google Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS string to a clean list."""
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.ENVIRONMENT.lower() == "production"

    def check_production_safety(self) -> None:
        """Verify production requirements before accepting requests."""
        if self.is_production:
            if not self.DATABASE_URL or not self.DATABASE_URL.startswith("postgres"):
                raise RuntimeError(
                    "Production safety violation: Valid PostgreSQL DATABASE_URL is strictly required."
                )
            if self.JWT_SECRET == "csic-dev-jwt-secret-key-32-chars-long-academic-project":
                raise RuntimeError(
                    "Production safety violation: Default development JWT_SECRET cannot be used in production."
                )


settings = Settings()


"""
Application configuration module.
Manages environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Browser Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # Browser automation
    headless_mode: bool = True
    browser_timeout: int = 30000  # milliseconds
    max_browser_instances: int = 5
    browser_type: str = "chromium"  # chromium, firefox, webkit

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]

    # Security
    max_execution_time: int = 300  # seconds
    allowed_domains: Optional[list] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

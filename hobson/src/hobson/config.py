from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    anthropic_api_key: str = ""
    google_api_key: str = ""
    ollama_base_url: str = "http://192.168.2.71:11434"

    # PostgreSQL
    database_url: str = "postgresql://hobson:password@192.168.2.67:5432/project_data"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Printful
    printful_api_key: str = ""

    # Obsidian
    obsidian_host: str = "192.168.2.140"
    obsidian_port: int = 27124
    obsidian_api_key: str = ""

    # Substack
    substack_cookies: str = ""

    # Uptime Kuma
    uptime_kuma_push_url: str = ""

    # Cost controls
    monthly_cost_cap: float = 50.0
    single_action_cost_threshold: float = 5.0

    # Agent
    brand_guidelines_path: str = "brand/brand_guidelines.md"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

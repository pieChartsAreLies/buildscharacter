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

    # GitHub (for PR-based content workflow)
    github_token: str = ""  # Personal access token with repo scope
    github_repo: str = "pieChartsAreLies/buildscharacter"  # owner/repo

    # Cloudflare Analytics
    cloudflare_api_token: str = ""  # API token with Analytics:Read permission
    cloudflare_zone_id: str = ""  # Zone ID for buildscharacter.com

    # Cloudflare R2 (design image storage)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "hobson-designs"
    r2_public_url: str = ""  # e.g., https://pub-{hash}.r2.dev

    # Uptime Kuma push URLs (one per workflow)
    uptime_kuma_push_morning_briefing: str = ""
    uptime_kuma_push_content_pipeline: str = ""
    uptime_kuma_push_design_batch: str = ""
    uptime_kuma_push_substack_dispatch: str = ""
    uptime_kuma_push_business_review: str = ""

    # Cost controls
    monthly_cost_cap: float = 50.0
    single_action_cost_threshold: float = 5.0

    # Bootstrap mode
    bootstrap_mode: bool = False

    # Agent
    brand_guidelines_path: str = "brand/brand_guidelines.md"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Printful
    printful_api_key: str = ""
    printful_webhook_secret: str = ""

    # Telegram (uses Bob's bot)
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # PostgreSQL (same DB as Hobson)
    database_url: str = "postgresql://hobson:password@192.168.2.67:5432/project_data"

    # Order limits
    order_max_production_cost: float = 50.0
    order_max_item_qty: int = 3
    order_max_hourly_velocity: int = 5

    # Server
    order_guard_port: int = 8100

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

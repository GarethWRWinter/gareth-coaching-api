from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://coaching:coaching@localhost:5432/coaching_db"

    # Auth
    secret_key: str = "change-me-to-a-random-secret-key"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    # Anthropic
    anthropic_api_key: str = ""

    # ElevenLabs (Voice)
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "onwK4e9ZLuTAKqWW03F9"  # "Daniel" — warm, authoritative
    elevenlabs_model_id: str = "eleven_turbo_v2_5"  # Low latency (~300ms)

    # Strava
    strava_client_id: str = ""
    strava_client_secret: str = ""
    strava_redirect_uri: str = "http://localhost:8000/api/v1/integrations/strava/callback"
    strava_webhook_verify_token: str = "coaching-strava-webhook-verify"

    # Dropbox
    dropbox_client_id: str = ""
    dropbox_client_secret: str = ""
    dropbox_redirect_uri: str = "http://localhost:8000/api/v1/integrations/dropbox/callback"

    # Dropbox auto-sync interval in seconds (0 = disabled, default 15 min)
    dropbox_sync_interval: int = 900

    # App
    app_name: str = "Advanced Cycling Coach"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://raizes:raizes@localhost:5433/raizes_do_nordeste"
    jwt_secret: str = "dev-secret-troque-me-com-32-bytes-ou-mais-0000"
    jwt_expires_minutes: int = 60
    jwt_algorithm: str = "HS256"


settings = Settings()

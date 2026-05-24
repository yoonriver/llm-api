from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bedrock Claude FastAPI Server"
    environment: str = "local"
    mock_model_name: str = "mock-claude"

    aws_region: str = "us-east-1"
    bedrock_model_id: str | None = None
    use_bedrock: bool = False

    s3_bucket: str | None = None
    ddb_table: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
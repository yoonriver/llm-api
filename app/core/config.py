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
    use_aws_storage: bool = False

    local_artifacts_dir: str = "local_artifacts"
    local_history_file: str = "local_history.json"

    api_key: str | None = None
    llm_timeout_seconds: int = 30
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
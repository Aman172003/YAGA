from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    agents_config: str = "config/agents.yaml"
    graphs_config: str = "config/graphs.yaml"
    mcps_config: str = "config/mcps.yaml"
    feature_flags_enabled: bool = False
    feature_flags_endpoint: str = ""
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    kafka_brokers: str = ""
    skip_kafka: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

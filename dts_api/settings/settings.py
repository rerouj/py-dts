from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = None
    app_description: str = None
    app_author_infos: dict = None
    app_url: list = [{"url": "http://localhost:8000", "description": "Localhost"}]
    allowed_hosts: list = ["http://localhost:5173"]
    dts_context: str = None
    dts_version: str = None
    app_version: str = None
    root_collection: str = None
    storage: str = None
    indexer: str = None
    base_path: str = None
    metadata_path: str = None
    tei_ns: str = None

    model_config = SettingsConfigDict(
        env_file=".env"
    )

def get_settings():
    return Settings()

settings = get_settings()
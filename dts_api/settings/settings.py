from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
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
        env_file="/Users/rdiaz/coderepos/dts-api-workdir/dts-api/.env"
    )

class OpenapiSettings(BaseModel):

    title: str = "Littérature Apocryphe du Nouveau Testament et de l'Ancien Testament: API-DTS",
    description: str = "API des éditions du projet ENLAC",
    version: str = "0.1",
    servers: list[dict[str, str]] = [
        {"url": "http://localhost:8000", "description": "Localhost"},
        # {"url": "http://ftsr-dev.unil.ch:8082", "description": "ftsr admin server"}
    ],
    contact: str = {"name": "Renato Diaz (FTSR-Unil)", "email": "renato.diaz@unil.ch"},
    openapi_tags: list[dict[str, str]] = [
        {"name": "root", "description": "Root route, returns global infos."},
        {"name": "collection", "description": "Operations on collection entries"},
        {"name": "navigation", "description": "Operations on navigation entries"},
        {"name": "document", "description": "Operations on document entries"},
    ],

def get_settings():
    return Settings()

settings = get_settings()
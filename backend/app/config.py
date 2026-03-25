from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration centralisée via variables d'environnement."""

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "smartshelf_rl"

    # VLM
    vlm_model_id: str = "Qwen/Qwen2-VL-2B-Instruct"
    vlm_device: str = "cpu"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # OpenFoodFacts
    off_base_url: str = "https://world.openfoodfacts.org/api/v2"
    off_timeout: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()

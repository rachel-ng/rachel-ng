from __future__ import annotations

import logging
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr, field_serializer
from pydantic_settings import BaseSettings


class Headers(BaseModel):
    authorization: SecretStr = Field(serialization_alias="Authorization")
    accept: str = Field(serialization_alias="Accept")
    tz: str = Field(serialization_alias="Time-Zone")

    @field_serializer("authorization")
    def serialize_authorization(self, value: SecretStr) -> str:
        return value.get_secret_value()


class Settings(BaseSettings):
    name: str
    token: SecretStr
    username: str
    url: str
    headers: Headers
    branch: str

    readme: Path = Path("README.md")
    template: str = "template"
    _etc: Path = Path("src/_etc")
    img: str = "img.svg"
    colors: str = "colors.json"

    model_config = {
        "env_file": Path(__file__).resolve().parent / "conf",
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",
        "extra": "forbid",
    }


logger = logging.getLogger(__name__)
settings = Settings()
logger.info(settings)

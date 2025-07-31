import os
import logging
from functools import cache

from pydantic import BaseModel, Field, SecretStr, field_serializer
from pydantic_settings import BaseSettings, SettingsConfigDict



class Headers(BaseModel):
    authorization: SecretStr = Field(serialization_alias='Authorization')
    accept: str = Field(serialization_alias='Accept')
    tz: str = Field(serialization_alias='Time-Zone')

    @field_serializer('authorization', 'Authorization', check_fields=False)
    def serialize_secret(self, value: SecretStr) -> str:
        return value.get_secret_value()


class Settings(BaseSettings):
    name: str

    token: SecretStr
    username: str

    url: str
    headers: Headers

    branch: str

    readme: str = "README.md"
    template: str = "template"
    etc: str = "src/etc"
    img: str = "img.svg"
    colors: str = "colors.json"

    class Config(SettingsConfigDict):
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf")
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


logger = logging.getLogger(__name__)


settings = Settings()

logger.info(settings)
# logger.debug(settings.token.get_secret_value())

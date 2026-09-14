import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    cors_allowed_origin: list[str]


def get_settings() -> Settings:
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError('Not specified DATABASE_URL')

    raw_cors = os.getenv('CORS_ALLOWED_ORIGIN', '')

    cors_list = [
        origin.strip() for origin in raw_cors.split(',') if origin.strip()
    ]

    return Settings(
        DATABASE_URL=db_url,
        cors_allowed_origin=cors_list,
    )

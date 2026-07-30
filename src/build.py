from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import logging

import arrow
import requests

from config.config import settings
from util.io import read_file, write_file, read_json
from util.const import DT_FORMAT, LOG_FORMAT

logger = logging.getLogger(__name__)




README_FILE = Path(settings.readme)
TEMPLATE_FILE = Path(settings._etc) / settings.template
IMG_FILE = Path(settings._etc) / settings.img
COLORS = read_json(Path(settings._etc) / settings.colors)


def update_color(img: list[str], color: str) -> list[str]:
    logger.info("updating color...")

    fill_index = next((index for index, line in enumerate(img) if "fill" in line), None)
    if fill_index is None:
        logger.error('"fill" not found in img')
        raise ValueError('"fill" not found in img')

    img[fill_index] = f'         fill="#${color}"\n'
    logger.debug("".join(img))
    return img


def check_account(base_url=settings.url, 
                  headers=settings.headers.model_dump(by_alias=True)
    ) -> tuple[datetime, datetime]:
    logger.debug("checking account...")

    try:
        url = base_url
        logger.debug(url)
        r = requests.get(url, headers=headers)
        data = r.json()
        logger.debug(data)

        created = data.get("created_at", "unknown")
        created = datetime.strptime(created, DT_FORMAT)

        updated = data.get("updated_at", "unknown")
        updated = datetime.strptime(updated, DT_FORMAT)

        assert created != None, "created is none"
        assert updated != None, "updated is none"

    except Exception as err:
        logger.error(err)
        raise Exception(err)

    return created, updated

def check_events(base_url=settings.url, 
                 headers=settings.headers.model_dump(by_alias=True), 
                 params={"per_page":"1"}
    ) -> datetime:
    logger.debug("checking events...")
    last = None

    try:
        url = f"{base_url}/events"
        logger.debug(url)
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        logger.debug(data)

        if len(data) > 0:
            last = data[0].get("created_at", "unknown")
            last = datetime.strptime(last, DT_FORMAT)

        assert last != None, "last is none"

    except Exception as err:
        logger.error(err)
        raise Exception(err)

    return last


def status(seen_at: datetime, n=6) -> tuple[bool, str]:
    # "last seen just now" if you were active in the past n hours
    seen_at = arrow.get(seen_at)

    timeframe = arrow.utcnow().floor('hour')
    timeframe = timeframe.shift(hours=-n)

    # in timeframe -> just now
    # else         -> seen_at
    time_ago = arrow.utcnow() if seen_at.is_between(timeframe, arrow.utcnow()) else seen_at

    time_elapsed = arrow.utcnow() - seen_at
    active = time_elapsed < timedelta(days=4)

    return active, time_ago.humanize()


def update_readme(active: bool, time_ago: str) -> None:
    logger.info("updating readme...")

    template = read_file(TEMPLATE_FILE, False)

    d = {
        "name": settings.name,
        "username": settings.username,
        "branch": settings.branch,
        "img": IMG_FILE,
        "status": "active" if active else "inactive",
        "ago": time_ago
    }

    logger.debug(d)
    template = template.format(**d)
    logger.debug(template)
    write_file(README_FILE, template)

def update_img(active: bool) -> None:
    logger.info("updating img...")
    img = read_file(IMG_FILE)
    img = update_color(img, COLORS["green"] if active else COLORS["grey"])
    # logger.debug(img)
    write_file(IMG_FILE, img)


def main():
    logger.info("building...")

    created, updated = check_account()
    last = check_events()

    seen_at = max(updated, last)
    active, time_ago = status(seen_at)

    logger.info("updating...")
    update_readme(active, time_ago)
    update_img(active)


if __name__ == "__main__":
    main()

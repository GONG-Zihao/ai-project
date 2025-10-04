import json
import logging.config
from pathlib import Path

from .config import settings


def setup_logging() -> None:
    logging_path = Path("configs/logging.json")
    if logging_path.exists():
        with logging_path.open("r", encoding="utf-8") as fp:
            config = json.load(fp)
        if settings.app_debug:
            # In debug we slightly lower the handler level
            config["handlers"]["console"]["level"] = "DEBUG"
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)

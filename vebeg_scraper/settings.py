from logging.config import dictConfig
import os
import logging
import yaml
import pathlib


# Add new config parameter her
VEBEG_URL = os.getenv("VEGEB_URL", default="https://www.vebeg.de")
DEBUG_MODE = os.getenv("False", default="True")
VEBEG_DOWNLOAD_PICUTRES = os.getenv("VEBEG_DOWNLOAD_PICUTRES", default="False")
PROMEHTEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 9111))
logging.error(f"download {VEBEG_DOWNLOAD_PICUTRES}")
PG_USER = os.getenv("PG_USER", default="vebeg")
PG_PASS = os.getenv("PG_PASS", default="vebeg")
PG_DB = os.getenv("PG_DB", default="vebeg")
PG_HOST = os.getenv("PG_HOST", default="database")

JSON_SERIALIZER_OUTPUT_PATH = os.getenv(
    "JSON_SERIALIZER_OUTPUT_PATH", default="/tmp/output"
)

PICTURE_CACHE_PATH = os.getenv("PICTURE_CACHE_PATH", default="/tmp/picture_cache")
# Path to the logging config file in a yml format
LOG_CONFIG_PATH = os.getenv("LOG_CONFIG_PATH", default="./logging.yml")
# Log Level for the root logger
LOG_LEVEL_ROOT = os.getenv("LOG_LEVEL_ROOT", default="INFO")
# Log level for the Project root logger
LOG_LEVEL_VEBEG = os.getenv("LOG_LEVEL_VEBEG", default="INFO")

# Load yml logging config
logging_config_path = pathlib.Path(LOG_CONFIG_PATH)
logging.info(f"Logging cofng path is {LOG_CONFIG_PATH}")
if logging_config_path.is_file():
    with open(logging_config_path, "rt") as file:
        logging_config = yaml.safe_load(file.read())
else:
    logging.error("Couldn't find the logging config", exc_info=True)
    raise ValueError("Error while loading logging config")

logging_config["loggers"]["scraper"]["level"] = LOG_LEVEL_VEBEG
logging_config["root"]["level"] = LOG_LEVEL_ROOT

# load logging config into current state
dictConfig(logging_config)

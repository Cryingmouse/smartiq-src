import os
import platform
from pathlib import Path
from typing import List

from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF

logging.register_options(CONF)

# Each component has its own `resources` path.
# The `resources` path of a component needs to be obtained based on its usage location.
COMMON_CONFIG = lambda resources_path: [
    Path(f"/etc/config/smartiq_srm.conf"),
    Path(resources_path).joinpath("config", "smartiq_srm.conf"),
]


def get_default_log_dir(default_dir):
    if not default_dir or not Path(default_dir).exists():
        if platform.system().lower() == "windows":
            default_dir = Path(os.environ["TEMP"], "log")
        else:
            default_dir = Path("/var/log/smartiq_srm")
    else:
        default_dir = Path(default_dir)
    if not default_dir.exists():
        os.makedirs(default_dir.as_posix())
    return default_dir.as_posix()


def find_first_valid_file(paths: List[Path]) -> str:
    """Return the first valid file path as a string, or raise an error if none are found."""
    for file in paths:
        if file.is_file():
            return file.as_posix()
    raise FileNotFoundError("Configuration file not found.")


def load_config(config_paths: List[Path] = None):
    config_files = []

    # If config paths are provided, search for the first valid one
    if config_paths:
        config_files.append(find_first_valid_file(config_paths))

    # Configure the CONF object
    CONF(args=[], default_config_files=config_files)
    default_log_dir = get_default_log_dir(CONF.log_dir)
    CONF.set_default("log_dir", default_log_dir)

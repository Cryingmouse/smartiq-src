import logging
from pathlib import Path

import click
import uvicorn
from oslo_config import cfg
from oslo_log import log as oslo_logging

from smartiq_srm import CONTEXT_SETTINGS
from smartiq_srm.command import RESOURCE_PATH
from smartiq_srm.config import load_config

CONF = cfg.CONF


@click.group(context_settings=CONTEXT_SETTINGS)
def scheduler():
    """Scheduler CLI.

    This is the main entry point for the scheduler CLI.
    """
    pass


@scheduler.command(context_settings=CONTEXT_SETTINGS)
@click.option("--port", default=8000, help="Port, default is 8000", required=False)
def start(port):
    """Start the scheduler with the scheduled tasks' configuration.

    Args:
        task_config (str): Path to the scheduled tasks' configuration file.
        port (int): Port number to start the web service on. Defaults to 8000.

    This command extends the SEARCH_PATHS list with common configuration file paths and
    uses the specified configuration file to start the scheduler.
    """
    load_config(
        [
            Path(f"/etc/config/smartiq_srm.conf"),
            RESOURCE_PATH.joinpath("config", "smartiq_srm.conf"),
        ],
    )

    oslo_logging.setup(CONF, f"smartiq_srm")

    LOG = logging.getLogger(f"smartiq_srm")

    from smartiq_srm.web_service.app import app
    from smartiq_srm.scheduler.scheduler import Scheduler

    LOG.info("start scheduler service...")

    task_config = RESOURCE_PATH.joinpath("task_config.yaml")

    cluster_scheduler = Scheduler(task_config_file=task_config)
    cluster_scheduler.start()

    LOG.info("start scheduler manager service...")
    app.scheduler = cluster_scheduler
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    scheduler()

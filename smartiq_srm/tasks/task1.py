import logging
import time
from datetime import datetime

from smartiq_srm.scheduler.base_task import AbstractTask

LOG = logging.getLogger("smartiq_srm")


class Task1(AbstractTask):
    @classmethod
    def execute(cls, *args, **kwargs):
        LOG.critical(f"Executing Job1, {datetime.now()}")

        time.sleep(1)  # 模拟长时间运行的任务

        LOG.critical(f"Executing Job1, {datetime.now()} after sleep")

        return "Job1 1 result"

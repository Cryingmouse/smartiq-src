import logging
from collections import defaultdict
from typing import Dict
from typing import List

from smartiq_srm.scheduler.base_task import AbstractTask

LOG = logging.getLogger("smartiq_srm")


class TaskManager:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def execute_and_publish(self, task: AbstractTask, task_args: List = None, task_kwargs: Dict = None):
        task_name = f"{task.__module__}.{task.__name__}"
        task_args = task_args or []
        task_kwargs = task_kwargs or {}
        try:
            result = task.execute(*task_args, **task_kwargs)
            self.publish(task_name, result)
        except Exception as e:
            LOG.exception(f"An exception {e} during the task {task}")
            self.publish(task_name, str(e), is_error=True)

    def publish(self, task_name, result, is_error=False):
        """发布任务结果"""
        for subscriber in self.subscribers[task_name]:
            subscriber.execute(task_name, result, is_error)

    def subscribe(self, task_name, callback):
        """订阅任务结果"""
        if isinstance(callback, list):
            self.subscribers[task_name].extend(callback)
        else:
            self.subscribers[task_name].append(callback)

    def unsubscribe(self, task_name, callback):
        """取消订阅任务结果"""
        if callback in self.subscribers[task_name]:
            self.subscribers[task_name].remove(callback)

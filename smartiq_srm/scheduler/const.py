# -*- coding: utf-8 -*-
# Copyright (c) 2020-present Lenovo. All right reserved.
# Confidential and Proprietary
from enum import IntEnum
from enum import StrEnum
from logging import INFO, WARNING, ERROR

from apscheduler import events
from apscheduler.schedulers.base import STATE_PAUSED
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.schedulers.base import STATE_STOPPED


DB_STORE = "mariadb"


class ExecutorEnum(StrEnum):
    PROCESS = "process"
    THREAD = "thread"


class SchedulerStateEnum(IntEnum):
    STOPPED = STATE_STOPPED
    RUNNING = STATE_RUNNING
    PAUSED = STATE_PAUSED


SCHEDULER_EVENT = "scheduler"
JOB_EVENT = "job"


EVENT_MAPPINGS = {
    events.EVENT_SCHEDULER_STARTED: (SCHEDULER_EVENT, INFO, "Scheduler started"),
    events.EVENT_SCHEDULER_SHUTDOWN: (SCHEDULER_EVENT, WARNING, "Scheduler shut down"),
    events.EVENT_SCHEDULER_PAUSED: (SCHEDULER_EVENT, WARNING, "Scheduler paused"),
    events.EVENT_SCHEDULER_RESUMED: (SCHEDULER_EVENT, INFO, "Scheduler resumed"),
    events.EVENT_EXECUTOR_ADDED: (SCHEDULER_EVENT, INFO, "Executor added"),
    events.EVENT_EXECUTOR_REMOVED: (SCHEDULER_EVENT, INFO, "Executor removed"),
    events.EVENT_JOBSTORE_ADDED: (SCHEDULER_EVENT, INFO, "Job store added"),
    events.EVENT_JOBSTORE_REMOVED: (SCHEDULER_EVENT, INFO, "Job store removed"),
    events.EVENT_ALL_JOBS_REMOVED: (SCHEDULER_EVENT, INFO, "All jobs removed from all job stores"),
    events.EVENT_JOB_ADDED: (JOB_EVENT, INFO, "Job {job_id} added"),
    events.EVENT_JOB_REMOVED: (JOB_EVENT, INFO, "Job {job_id} removed"),
    events.EVENT_JOB_MODIFIED: (JOB_EVENT, INFO, "Job {job_id} modified"),
    events.EVENT_JOB_EXECUTED: (JOB_EVENT, INFO, "Job {job_id} executed"),
    events.EVENT_JOB_ERROR: (JOB_EVENT, ERROR, "Job {job_id} error: {error}"),
    events.EVENT_JOB_MISSED: (JOB_EVENT, INFO, "Job {job_id} missed"),
    events.EVENT_JOB_SUBMITTED: (JOB_EVENT, INFO, "Job {job_id} submitted to executor"),
    events.EVENT_JOB_MAX_INSTANCES: (JOB_EVENT, WARNING, "Job {job_id} max instances"),
}
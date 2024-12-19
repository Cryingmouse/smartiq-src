# -*- coding: utf-8 -*-
# Copyright (c) 2020-present Lenovo. All right reserved.
# Confidential and Proprietary
import importlib
from datetime import datetime
from enum import StrEnum
from typing import Annotated
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union
from apscheduler.util import undefined

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import PositiveInt
from pydantic import ValidationError
from pydantic import field_validator
from pydantic import model_validator

from smartiq_srm.scheduler.const import ExecutorEnum
from smartiq_srm.scheduler.const import SchedulerStateEnum

# 用于next_run_time, undefined 代表自动计算， None 表示禁用
APSCHEDULER_UNDEFINED = "undefined"


class TriggerType(StrEnum):
    DATE = "date"
    CRON = "cron"
    INTERVAL = "interval"


class ScheduleStateResponse(BaseModel):
    state: SchedulerStateEnum = Field(description="0: stopped, 1: running, 2: paused")


class DateTriggerSchema(BaseModel):
    """Triggers once on the given datetime. If ``run_date`` is left empty, current time is used.

    Args:
        run_date (datetime|str): the date/time to run the job at
        timezone (str): time zone for ``run_date`` if it doesn't have one already
    """

    trigger_type: Literal[TriggerType.DATE] = Field(default=TriggerType.DATE)
    run_date: Optional[datetime] = Field(default=None)
    timezone: Optional[str] = Field(default="UTC")

    @model_validator(mode="after")
    def to_trigger(self):
        return DateTrigger(**self.model_dump(exclude={"trigger_type"}))


class CronTriggerSchema(BaseModel):
    """Triggers when current time matches all specified time constraints,
    similarly to how the UNIX cron scheduler works.

    Args:
        year (int|str): 4-digit year
        month (int|str): month (1-12)
        day (int|str): day of month (1-31)
        week (int|str): ISO week (1-53)
        day_of_week (int|str): number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour (int|str): hour (0-23)
        minute (int|str): minute (0-59)
        second (int|str): second (0-59)
        start_date (datetime|str): earliest possible date/time to trigger on (inclusive)
        end_date (datetime|str): latest possible date/time to trigger on (inclusive)
        timezone (str): time zone to use for the date/time calculations (defaults to scheduler timezone)
        jitter (int|None): delay the job execution by ``jitter`` seconds at most

    .. note:: The first weekday is always **monday**.

    Expression types:
        The following table lists all the available expressions for use in the fields from year to second. Multiple
        expression can be given in a single field, separated by commas.

        ==========  =====  ===========
        Expression  Field  Description
        ==========  =====  ===========
        ``*``       any    Fire on every value
        ``*/a``     any    Fire every ``a`` values, starting from the minimum
        ``a-b``     any    Fire on any value within the ``a-b`` range (a must be smaller than b)
        ``a-b/c``   any    Fire every c values within the ``a-b`` range
        ``xth y``   day    Fire on the ``x`` -th occurrence of weekday ``y`` within the month
        ``last x``  day    Fire on the last occurrence of weekday ``x`` within the month
        ``last``    day    Fire on the last day within the month
        ``x,y,z``   any    Fire on any matching expression; can combine any number of any of the above expressions
        ==========  =====  ===========
    """

    trigger_type: Literal[TriggerType.CRON] = Field(default=TriggerType.CRON)
    year: Optional[PositiveInt | str] = Field(default=None)
    month: Optional[PositiveInt | str] = Field(default=None)
    week: Optional[PositiveInt | str] = Field(default=None)
    day_of_week: Optional[int | str] = Field(default=None)
    day: Optional[int | str] = Field(default=None)
    hour: Optional[int | str] = Field(default=None)
    minute: Optional[int | str] = Field(default=None)
    second: Optional[int | str] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    timezone: Optional[str] = Field(default="UTC")
    jitter: Optional[PositiveInt] = Field(default=None)

    @model_validator(mode="after")
    def to_trigger(self):
        return CronTrigger(**self.model_dump(exclude={"trigger_type"}))


class IntervalTriggerSchema(BaseModel):
    """Triggers on specified intervals, starting on ``start_date`` if specified, ``datetime.now(timezone.utc)`` +
    interval otherwise.

    Args:
        weeks (int): number of weeks to wait
        days (int): number of days to wait
        hours (int): number of hours to wait
        minutes (int): number of minutes to wait
        seconds (int): number of seconds to wait
        start_date (datetime|str): starting point for the interval calculation
        end_date (datetime|str): latest possible date/time to trigger on
        timezone (str): time zone to use for the date/time calculations
        jitter (int|None): delay the job execution by ``jitter`` seconds at most
    """

    trigger_type: Literal[TriggerType.INTERVAL] = Field(default=TriggerType.INTERVAL)
    weeks: int = Field(default=0)
    days: int = Field(default=0)
    hours: int = Field(default=0)
    minutes: int = Field(default=0)
    seconds: int = Field(default=0)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    timezone: Optional[str] = Field(default="UTC")
    jitter: Optional[int] = Field(default=None)

    @model_validator(mode="before")  # noqa
    @classmethod
    def validate_before(cls, values):
        if not any([values.get(key) for key in ("weeks", "days", "hours", "minutes", "seconds")]):
            raise ValidationError("Set at least one of 'weeks',' days', 'hours',' minutes', 'seconds'")
        return values

    @model_validator(mode="after")  # noqa
    def to_trigger(self):
        return IntervalTrigger(**self.model_dump(exclude={"trigger_type"}))


TriggerSchema = Annotated[
    Union[DateTriggerSchema, CronTriggerSchema, IntervalTriggerSchema], Field(discriminator="trigger_type")
]


class JobResponse(BaseModel):
    id: str


class JobInfoResponse(BaseModel):
    id: Optional[str] = Field(default=None)
    next_run_time: Optional[datetime] = Field(default=None)


class AddJobRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "migration_1",
                "trigger": {"trigger_type": "interval", "seconds": 5},
                "executor": "thread",
                "task": "smartiq.scheduler.tasks.dummy_task:AddTask",
                "task_args": [5, 3],
                "task_kwargs": {},
            }
        }
    )

    job_id: str
    trigger: Optional[TriggerSchema] = Field(default=None)
    executor: ExecutorEnum
    misfire_grace_time: Optional[int] = Field(default=None)
    next_run_time: datetime | Literal["undefined"] | None = Field(default=APSCHEDULER_UNDEFINED, validate_default=True)

    task: str
    task_args: Optional[List[Any]] = Field(default_factory=list)
    task_kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("task")  # noqa
    @classmethod
    def import_task(cls, task):
        module_path, task_name = task.split(":")
        module = importlib.import_module(module_path)
        task = getattr(module, task_name)
        return task

    @field_validator("next_run_time")  # noqa
    @classmethod
    def build_next_run_time(cls, next_run_time):
        if next_run_time == APSCHEDULER_UNDEFINED:
            return undefined

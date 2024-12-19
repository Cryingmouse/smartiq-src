# -*- coding: utf-8 -*-
# Copyright (c) 2020-present Lenovo. All right reserved.
# Confidential and Proprietary
from typing import List

from apscheduler.jobstores.base import JobLookupError
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status
from starlette.responses import JSONResponse

from smartiq_srm.web_service.schema import AddJobRequest
from smartiq_srm.web_service.schema import JobInfoResponse
from smartiq_srm.web_service.schema import JobResponse
from smartiq_srm.web_service.schema import ScheduleStateResponse
from smartiq_srm.scheduler.const import DB_STORE
from smartiq_srm.scheduler.scheduler import Scheduler

router = APIRouter()


def get_scheduler(request: Request):
    return request.app.scheduler


@router.get(
    "/state",
    status_code=status.HTTP_200_OK,
)
async def state(scheduler: Scheduler = Depends(get_scheduler)) -> ScheduleStateResponse:
    return ScheduleStateResponse(state=scheduler.state)


@router.post(
    "/pause",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def pause(scheduler: Scheduler = Depends(get_scheduler)):
    scheduler.pause()


@router.post(
    "/resume",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def resume(scheduler: Scheduler = Depends(get_scheduler)):
    scheduler.resume()


@router.get(
    "/jobs",
    status_code=status.HTTP_200_OK,
    operation_id="get_jobs",
)
async def list_job(scheduler: Scheduler = Depends(get_scheduler)) -> List[JobResponse]:
    return scheduler.get_jobs(job_store=DB_STORE)


@router.get(
    "/jobs/{job_id}",
    status_code=status.HTTP_200_OK,
    operation_id="get_job",
)
async def job(job_id: str, scheduler: Scheduler = Depends(get_scheduler)) -> JobInfoResponse:
    job = scheduler.get_job(job_id=job_id, job_store=DB_STORE)
    return job if job else {}


@router.post(
    "/jobs",
    status_code=status.HTTP_200_OK,
    description="add a new job or modify an existing job with the same ``id`` (but retain the number of runs from the "
    "existing one)",
)
async def add_job(add_job_request: AddJobRequest, scheduler: Scheduler = Depends(get_scheduler)) -> JobResponse:
    job_id = scheduler.register(
        job_id=add_job_request.job_id,
        trigger=add_job_request.trigger,
        task=add_job_request.task,
        task_args=add_job_request.task_args,
        task_kwargs=add_job_request.task_kwargs,
        executor=add_job_request.executor,
        next_run_time=add_job_request.next_run_time,
        store=DB_STORE,
        misfire_grace_time=add_job_request.misfire_grace_time,
        subscribes=[],
    )
    return JobResponse(id=job_id)


EXAMPLE_404 = {
    "content": {
        "application/json": {
            "example": {
                "code": "e40400000",
                "message": "'No job by the id of migration_1 was found'",
                "data": "",
            }
        }
    }
}


@router.post(
    "/jobs/{job_id}/pause",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: EXAMPLE_404},
)
async def pause_job(job_id: str, scheduler: Scheduler = Depends(get_scheduler)):
    try:
        scheduler.pause_job(job_id, job_store=DB_STORE)
    except JobLookupError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"code": "e40400000", "message": str(e), "data": ""}
        )


@router.post(
    "/jobs/{job_id}/resume",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: EXAMPLE_404},
)
async def resume_job(job_id: str, scheduler: Scheduler = Depends(get_scheduler)):
    try:
        scheduler.resume_job(job_id, job_store=DB_STORE)
    except JobLookupError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"code": "e40400000", "message": str(e), "data": ""}
        )


@router.delete(
    "/jobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: EXAMPLE_404},
)
async def remove_job(job_id: str, scheduler: Scheduler = Depends(get_scheduler)):
    try:
        scheduler.unregister(job_id, job_store=DB_STORE)
    except JobLookupError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"code": "e40400000", "message": str(e), "data": ""}
        )

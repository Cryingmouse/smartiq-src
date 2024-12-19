# -*- coding: utf-8 -*-
# Copyright (c) 2020-present Lenovo. All right reserved.
# Confidential and Proprietary
import logging

from fastapi import FastAPI
from fastapi.routing import APIRoute
from oslo_config import cfg

from smartiq_srm.web_service.api.manager import router

CONF = cfg.CONF
LOG = logging.getLogger("smartiq_srm")


def default_operation_id(route: "APIRoute") -> str:
    return route.name


app = FastAPI(
    title="Scheduler Manager", description="Scheduler RESTFul API", generate_unique_id_function=default_operation_id
)

# ==================== register router ====================

app.include_router(router, prefix=f"/internal/v1/srm/scheduler", tags=["Manager"])

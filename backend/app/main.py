from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.health import router as health_router
from backend.app.api.comparison import router as comparison_router
from backend.app.api.recommendation import router as recommendation_router
from backend.app.api.combined_decision import (
    router as combined_decision_router,
)
from backend.app.api.automatic_decision import (
    router as automatic_decision_router,
)
from backend.app.api.decision_workflow import (
    router as decision_workflow_router,
)
from backend.app.api.contracts import router as contracts_router
from backend.app.api.intake import router as intake_router
from backend.app.api.contract_documents import (
    router as contract_documents_router,
)
from backend.app.api.financial import router as financial_router
from backend.app.api.risk import router as risk_router
from backend.app.api.decision import router as decision_router
from backend.app.api.contract_information import (
    router as contract_information_router,
)
from backend.app.api.contract_decision import (
    router as contract_decision_router,
)
from backend.app.api.auth import router as auth_router

from backend.app.core.config import settings
from backend.app.core.middleware import request_logging_middleware
from backend.app.core.security_headers import security_headers_middleware


logger = logging.getLogger(__name__)


app = FastAPI(
    title="Contract Manager API",
)


# ============================================================
# MIDDLEWARE
# ============================================================

app.middleware("http")(request_logging_middleware)
app.middleware("http")(security_headers_middleware)


@app.exception_handler(Exception)
async def handle_unexpected_exception(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected internal server error occurred."
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTER REGISTRATION
# ============================================================

app.include_router(health_router)

# Static/specific contract routes
app.include_router(comparison_router)
app.include_router(recommendation_router)
app.include_router(combined_decision_router)
app.include_router(automatic_decision_router)
app.include_router(decision_workflow_router)

# Main contract routes
app.include_router(contracts_router)

# Contract services
app.include_router(intake_router)
app.include_router(contract_documents_router)
app.include_router(financial_router)
app.include_router(risk_router)
app.include_router(decision_router)
app.include_router(contract_information_router)
app.include_router(contract_decision_router)

# Authentication
app.include_router(auth_router)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.health import router as health_router
from backend.app.api.comparison import router as comparison_router
from backend.app.api.recommendation import (
    router as recommendation_router,
)
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
from backend.app.api.auth import router as auth_router
from backend.app.api.auth_test import router as auth_test_router

app = FastAPI(
    title="Contract Manager API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Router registration
# ---------------------------------------------------------

app.include_router(health_router)

# ---------------------------------------------------------
# Specific/static contract routes
# These must be registered before /{contract_id}
# ---------------------------------------------------------

app.include_router(comparison_router)
app.include_router(recommendation_router)
app.include_router(combined_decision_router)
app.include_router(automatic_decision_router)
app.include_router(decision_workflow_router)

# ---------------------------------------------------------
# Generic contract routes
# ---------------------------------------------------------

app.include_router(contracts_router)

# ---------------------------------------------------------
# Other contract services
# ---------------------------------------------------------

app.include_router(intake_router)
app.include_router(contract_documents_router)
app.include_router(financial_router)
app.include_router(risk_router)
app.include_router(decision_router)
app.include_router(contract_information_router)
app.include_router(auth_router)
app.include_router(auth_test_router)
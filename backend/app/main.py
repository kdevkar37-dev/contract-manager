from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.contracts import router as contracts_router
from backend.app.api.health import router as health_router
from backend.app.api.contract_documents import router as contract_documents_router
from backend.app.api.intake import router as intake_router

app = FastAPI(title="Contract Manager API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(contracts_router)
app.include_router(intake_router)
app.include_router(contract_documents_router)
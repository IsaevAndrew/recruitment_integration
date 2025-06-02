from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

from src.database import init_db
from src.auth.router import router as auth_router
from src.candidates.router import router as candidates_router
from src.vacancies.router import router as vacancies_router
from src.applications.router import router as applications_router

from src.candidates.models import Candidate  # noqa: F401
from src.vacancies.models import Vacancy  # noqa: F401
from src.applications.models import JobApplication  # noqa: F401

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Candidate Service API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await init_db()


app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(vacancies_router)
app.include_router(applications_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

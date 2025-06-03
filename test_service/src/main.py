from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import init_db
from src.templates.router import router as templates_router
from src.questions.router import router as questions_router
from src.answers.router import router as answers_router
from src.sessions.router import router as sessions_router

from src.templates.models import TestTemplate  # noqa: F401
from src.questions.models import Question  # noqa: F401
from src.answers.models import AnswerOption  # noqa: F401
from src.sessions.models import TestSession, SessionAnswer  # noqa: F401

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Test Service API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await init_db()


app.include_router(templates_router)
app.include_router(questions_router)
app.include_router(answers_router)
app.include_router(sessions_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

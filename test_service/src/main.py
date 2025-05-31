from fastapi import FastAPI
from src.config import settings
from src.database import engine, Base

from src.templates.models import TestTemplate  # noqa: F401
from src.questions.models import Question       # noqa: F401
from src.answers.models import AnswerOption     # noqa: F401
from src.sessions.models import TestSession, SessionAnswer  # noqa: F401

app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health", tags=["Health"])
async def health_check():

    return {"status": "ok", "service": settings.PROJECT_NAME}

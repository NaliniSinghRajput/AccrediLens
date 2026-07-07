from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_answers import router as answers_router
from app.api.routes_auth import router as auth_router
from app.api.routes_papers import router as papers_router
from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(papers_router)
app.include_router(answers_router)

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from redis import Redis
from rq import Queue
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models import Answer, Chunk, Page, Paper, Paragraph, ProcessingJob, User
from app.schemas import AnswerOut, AskRequest, PaperDetail, PaperOut
from app.services.processor import process_paper, process_paper_job
from app.services.rag import answer_question
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/papers", tags=["papers"])


def ensure_owned_paper(db: Session, paper_id: str, user: User) -> Paper:
    paper = db.get(Paper, paper_id)
    if not paper or paper.user_id != user.id:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.post("/upload", response_model=PaperOut)
def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Paper:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    settings = get_settings()
    paper = Paper(user_id=user.id, original_filename=file.filename, storage_path="", status="uploaded")
    db.add(paper)
    db.commit()
    db.refresh(paper)

    target_dir = Path(settings.upload_dir) / user.id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{paper.id}.pdf"
    with target_path.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    paper.storage_path = str(target_path)
    db.commit()
    db.refresh(paper)
    return paper


@router.get("", response_model=list[PaperOut])
def list_papers(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Paper]:
    return list(db.scalars(select(Paper).where(Paper.user_id == user.id).order_by(Paper.created_at.desc())))


@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> PaperDetail:
    paper = ensure_owned_paper(db, paper_id, user)
    page_count = db.scalar(select(func.count(Page.id)).where(Page.paper_id == paper.id)) or 0
    paragraph_count = db.scalar(select(func.count(Paragraph.id)).where(Paragraph.paper_id == paper.id)) or 0
    chunk_count = db.scalar(select(func.count(Chunk.id)).where(Chunk.paper_id == paper.id)) or 0
    return PaperDetail(
        id=paper.id,
        title=paper.title,
        original_filename=paper.original_filename,
        status=paper.status,
        error_message=paper.error_message,
        created_at=paper.created_at,
        processed_at=paper.processed_at,
        page_count=page_count,
        paragraph_count=paragraph_count,
        chunk_count=chunk_count,
    )


@router.delete("/{paper_id}")
def delete_paper(paper_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, str]:
    paper = ensure_owned_paper(db, paper_id, user)
    try:
        VectorStore().delete_paper(paper.id)
    except Exception:
        pass
    storage_path = Path(paper.storage_path)
    db.delete(paper)
    db.commit()
    if storage_path.exists():
        storage_path.unlink()
    return {"status": "deleted"}


@router.post("/{paper_id}/process")
async def start_processing(
    paper_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    paper = ensure_owned_paper(db, paper_id, user)
    job = ProcessingJob(paper_id=paper.id, status="queued", message="Queued for PDF processing")
    db.add(job)
    paper.status = "processing"
    db.commit()
    db.refresh(job)

    settings = get_settings()
    if settings.process_inline:
        await process_paper(paper.id, job.id)
    else:
        queue = Queue("paper-processing", connection=Redis.from_url(settings.redis_url))
        queue.enqueue(process_paper_job, paper.id, job.id, job_timeout=1800)
    return {"paper_id": paper.id, "job_id": job.id, "status": "queued"}


@router.get("/{paper_id}/status")
def paper_status(paper_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, str | None]:
    paper = ensure_owned_paper(db, paper_id, user)
    return {"paper_id": paper.id, "status": paper.status, "error_message": paper.error_message}


@router.post("/{paper_id}/ask", response_model=AnswerOut)
async def ask_question(
    paper_id: str,
    payload: AskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Answer:
    paper = ensure_owned_paper(db, paper_id, user)
    if paper.status != "ready":
        raise HTTPException(status_code=409, detail="Paper is not ready for questions")
    return await answer_question(db, paper, user.id, payload.question, mode="qa")


@router.post("/{paper_id}/tutor", response_model=AnswerOut)
async def tutor_question(
    paper_id: str,
    payload: AskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Answer:
    paper = ensure_owned_paper(db, paper_id, user)
    if paper.status != "ready":
        raise HTTPException(status_code=409, detail="Paper is not ready for tutor mode")
    return await answer_question(db, paper, user.id, payload.question, mode="tutor")


@router.get("/{paper_id}/answers", response_model=list[AnswerOut])
def paper_answers(paper_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Answer]:
    paper = ensure_owned_paper(db, paper_id, user)
    return list(
        db.scalars(
            select(Answer).where(Answer.paper_id == paper.id, Answer.user_id == user.id).order_by(Answer.created_at.desc())
        )
    )

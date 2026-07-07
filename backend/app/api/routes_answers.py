from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Answer, AnswerSource, User
from app.schemas import SourceOut

router = APIRouter(prefix="/answers", tags=["answers"])


@router.get("/{answer_id}/sources", response_model=list[SourceOut])
def get_answer_sources(
    answer_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[AnswerSource]:
    answer = db.get(Answer, answer_id)
    if not answer or answer.user_id != user.id:
        raise HTTPException(status_code=404, detail="Answer not found")
    return list(db.scalars(select(AnswerSource).where(AnswerSource.answer_id == answer_id)))

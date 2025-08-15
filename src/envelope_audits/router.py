import asyncio
import time

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..dependencies import get_session
from . import service, schemas

router = APIRouter()

@router.get("/envelope-audits/", response_model=list[schemas.EnvelopeAudits])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    users = service.get_envelope_aduits(db, skip=skip, limit=limit)
    return users


@router.get("/envelope-audits/{id}", response_model=schemas.EnvelopeAudits)
def read_node(id: int, db: Session = Depends(get_session)):
    db_node = service.get_envelope_audit(db, id=id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

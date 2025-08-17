
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..dependencies import get_session
from . import schemas, service

router = APIRouter()


@router.get("/positions/", response_model=list[schemas.Position])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    positions = service.get_positions(db, skip=skip, limit=limit)
    return positions


@router.get("/nodes/{node_id}/positions/", response_model=list[schemas.Position])
def read_node(
    node_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_session)
):
    db_node = service.get_positions(db, skip=skip, limit=limit, node_id=node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

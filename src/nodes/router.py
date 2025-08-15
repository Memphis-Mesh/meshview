import asyncio
import time

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..dependencies import get_session
from . import service, schemas

router = APIRouter()


@router.get("/terrible-ping")
async def terrible_ping():
    time.sleep(
        10
    )  # I/O blocking operation for 10 seconds, the whole process will be blocked

    return {"pong": True}


@router.get("/good-ping")
def good_ping():
    time.sleep(
        10
    )  # I/O blocking operation for 10 seconds, but in a separate thread for the whole `good_ping` route

    return {"pong": True}


@router.get("/perfect-ping")
async def perfect_ping():
    await asyncio.sleep(10)  # non-blocking I/O operation

    return {"pong": True}


@router.post("/nodes/", response_model=schemas.Node)
def create_node(node: schemas.Node, db: Session = Depends(get_session)):
    db_node = service.get_node(db, node_id=node.node_id)
    if db_node:
        raise HTTPException(status_code=400, detail="Node already registered")
    return service.create_node(db=db, node=node)


@router.get("/nodes/", response_model=list[schemas.Node])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    users = service.get_nodes(db, skip=skip, limit=limit)
    return users


@router.get("/nodes/{node_id}", response_model=schemas.Node)
def read_node(node_id: int, db: Session = Depends(get_session)):
    db_node = service.get_node(db, node_id=node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

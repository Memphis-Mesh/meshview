from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine

from .nodes import router as NodesRouter
from .database import engine
from typing import Annotated



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


app.include_router(NodesRouter.router)



@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

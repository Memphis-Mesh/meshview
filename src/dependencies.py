from sqlmodel import Session
from .database import engine

def get_session():
    with Session(engine) as session:
        yield session


# async def valid_post_id(post_id: UUID4) -> dict[str, Any]:
#     post = await service.get_by_id(post_id)
#     if not post:
#         raise PostNotFound()

#     return post

# async def valid_node_id(node_id: )

from .config import settings
from sqlmodel import create_engine

connect_args = {"check_same_thread": False}
engine = create_engine(str(settings.DATABASE_URL), connect_args=connect_args)

from meshview import models
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = None
async_session = None


def init_database(database_connection_string, read_only=False):
    global engine, async_session

    kwargs = {"echo": False}

    if database_connection_string.startswith("sqlite"):
        if read_only:
            # Ensure SQLite is opened in read-only mode
            database_connection_string += "?mode=ro"
            kwargs["connect_args"] = {"uri": True}
        else:
            kwargs["connect_args"] = {"timeout": 60}
    else:
        kwargs["pool_size"] = 20
        kwargs["max_overflow"] = 50

    engine = create_async_engine(database_connection_string, **kwargs)
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

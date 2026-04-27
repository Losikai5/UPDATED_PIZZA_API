import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
async def clear():
    engine = create_async_engine("postgresql+asyncpg://postgres:160061@localhost:5432/mypizza_api")
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM alembic_version"))
        print("Cleared alembic_version")
    await engine.dispose()
asyncio.run(clear())

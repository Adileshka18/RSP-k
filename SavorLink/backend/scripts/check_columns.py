import asyncio
from backend.database.session import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'enterprise_reviews'"))
        columns = [row[0] for row in res.fetchall()]
        print(f"Columns: {columns}")

if __name__ == "__main__":
    asyncio.run(check())

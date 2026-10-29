import asyncio
from backend.database.session import engine
from backend.database.models import Base
from sqlalchemy import text

async def fix():
    async with engine.begin() as conn:
        # We need to drop the table because the schema changed (foreign key and column name)
        await conn.execute(text("DROP TABLE IF EXISTS enterprise_reviews CASCADE;"))
        # We can also use Base.metadata.create_all for just this table or all tables
        # Since I changed EnterpriseReview in models.py, I'll just recreate it.
        await conn.run_sync(Base.metadata.create_all, tables=[Base.metadata.tables['enterprise_reviews']])
    print("Dropped and recreated enterprise_reviews table.")

if __name__ == "__main__":
    asyncio.run(fix())

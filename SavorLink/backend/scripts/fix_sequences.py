"""Fix PostgreSQL sequences that got out of sync."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL")


async def fix_sequences():
    engine = create_async_engine(DATABASE_URL, echo=False)

    tables = ["users", "enterprises", "products", "carts", "cart_items", "favorites", "categories"]

    async with engine.begin() as conn:
        for table in tables:
            try:
                # Get max ID
                result = await conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table}"))
                max_id = result.scalar()
                # Get sequence name directly
                seq_result = await conn.execute(
                    text(f"SELECT pg_get_serial_sequence('{table}', 'id')")
                )
                seq_name = seq_result.scalar()
                if seq_name:
                    next_val = max_id + 1
                    await conn.execute(text(f"SELECT setval('{seq_name}', {next_val}, false)"))
                    print(f"Table {table}: max_id={max_id}, sequence reset to {next_val}")
                else:
                    print(f"Table {table}: no sequence found (might use BIGSERIAL or identity)")
            except Exception as e:
                print(f"Table {table}: error - {e}")

    await engine.dispose()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(fix_sequences())

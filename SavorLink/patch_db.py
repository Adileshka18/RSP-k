import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
async def run():
    engine = create_async_engine('postgresql+asyncpg://postgres:1111@postgres:5432/SavorLink')
    async with engine.connect() as conn:
        try:
            # Create alembic_version and stamp if needed
            await conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) PRIMARY KEY);"))
            await conn.execute(text("DELETE FROM alembic_version"))
            await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('20260420_111111111111')"))
            
            users_cols = (await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users'"))).fetchall()
            ent_cols = (await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='enterprises'"))).fetchall()
            users_cols = [c[0] for c in users_cols]
            ent_cols = [c[0] for c in ent_cols]
            
            if 'token_version' not in users_cols:
                await conn.execute(text('ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 0 NOT NULL'))
            if 'first_name' not in users_cols:
                await conn.execute(text('ALTER TABLE users ADD COLUMN first_name TEXT'))
            if 'last_name' not in users_cols:
                await conn.execute(text('ALTER TABLE users ADD COLUMN last_name TEXT'))
            if 'description' not in ent_cols:
                await conn.execute(text('ALTER TABLE enterprises ADD COLUMN description TEXT'))
            await conn.commit()
            print('DB Schema patched successfully')
        except Exception as e:
            print(f"Error {e}")

if __name__ == "__main__":
    asyncio.run(run())

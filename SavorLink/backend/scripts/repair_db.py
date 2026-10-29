import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from backend.database.models import Enterprise, Product

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/savorlink")

def fix_text(text: str) -> str:
    if not text:
        return text
    try:
        # Пробуем починить кодировку: UTF-8 -> CP1251 -> UTF-8
        # Это исправляет ситуацию, когда UTF-8 байты были интерпретированы как CP1251
        return text.encode('cp1251').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

async def repair():
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        # 1. Починка предприятий
        print("Проверка предприятий...")
        res = await session.execute(select(Enterprise))
        enterprises = res.scalars().all()
        ent_fixed = 0
        for ent in enterprises:
            changed = False
            # Поля: short_name, region
            for attr in ['short_name', 'region']:
                old_val = getattr(ent, attr)
                if old_val:
                    new_val = fix_text(old_val)
                    if old_val != new_val:
                        setattr(ent, attr, new_val)
                        changed = True
            if changed:
                ent_fixed += 1

        # 2. Починка товаров
        print("Проверка товаров...")
        res = await session.execute(select(Product))
        products = res.scalars().all()
        prod_fixed = 0
        for prod in products:
            changed = False
            # Поля: name, description
            for attr in ['name', 'description']:
                old_val = getattr(prod, attr)
                if old_val:
                    new_val = fix_text(old_val)
                    if old_val != new_val:
                        setattr(prod, attr, new_val)
                        changed = True
            if changed:
                prod_fixed += 1

        # 3. Починка категорий
        from backend.database.models import Category
        print("Проверка категорий...")
        res = await session.execute(select(Category))
        categories = res.scalars().all()
        cat_fixed = 0
        for cat in categories:
            old_val = cat.name
            if old_val:
                new_val = fix_text(old_val)
                if old_val != new_val:
                    cat.name = new_val
                    cat_fixed += 1

        if ent_fixed > 0 or prod_fixed > 0 or cat_fixed > 0:
            await session.commit()
            print(f"Исправлено предприятий: {ent_fixed}")
            print(f"Исправлено товаров: {prod_fixed}")
            print(f"Исправлено категорий: {cat_fixed}")
        else:
            print("Поврежденных данных не обнаружено.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(repair())

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from backend.core.config import get_database_url
from backend.database.models import Enterprise

async def main():
    engine = create_async_engine(get_database_url())
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    descriptions = [
        "Надёжный партнер в сфере оптовых поставок продовольственных товаров. Гарантируем высокое качество и своевременную доставку.",
        "Ведущий дистрибьютор свежих продуктов питания. Мы заботимся о свежести и пользе каждого продукта.",
        "Поставщик сертифицированной сельскохозяйственной продукции от фермеров. Прямые поставки от производителя к вам.",
        "Широкий ассортимент качественного сырья и ингредиентов для ресторанов и производств. Многолетний опыт и репутация на рынке.",
        "Оптовые продажи продуктов премиум-класса для розничных сетей и сферы HoReCa. Лучший выбор лучших брендов."
    ]
    
    async with async_session() as session:
        result = await session.execute(select(Enterprise))
        enterprises = result.scalars().all()
        
        for i, ent in enumerate(enterprises):
            if not ent.description:
                ent.description = descriptions[i % len(descriptions)]
                print(f"Updated description for {ent.short_name}")
        
        await session.commit()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())

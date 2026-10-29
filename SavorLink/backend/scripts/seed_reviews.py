import asyncio
import random
from sqlalchemy import select
from backend.database.session import get_session
from backend.database.models import User, UserRole, Enterprise, EnterpriseReview

REVIEWS_POOL = [
    "Отличный поставщик, всё привезли вовремя!",
    "Качество продукции на высоте, будем заказывать еще.",
    "Немного задержали доставку, но в остальном всё супер.",
    "Самые лучшие цены на рынке, рекомендую.",
    "Очень вежливые менеджеры, помогли с оформлением.",
    "Продукция свежая, упаковка надежная.",
    "Всегда на связи, оперативно решают вопросы.",
    "Приятно работать с профессионалами.",
    "Хороший ассортимент, всегда есть из чего выбрать.",
    "Надежный партнер для нашего бизнеса."
]

async def seed():
    session_gen = get_session()
    session = await session_gen.__anext__()

    # 1. Get all buyers
    res = await session.execute(select(User).where(User.role == UserRole.BUYER))
    buyers = res.scalars().all()

    if not buyers:
        print("No buyers found, creating a test buyer...")
        test_buyer = User(
            email="test_buyer@savorlink.ru",
            password_hash="pbkdf2:sha256:260000$...", # dummy
            role=UserRole.BUYER,
            phone="+79991112233"
        )
        session.add(test_buyer)
        await session.flush()
        buyers = [test_buyer]

    # 2. Get all enterprises
    res = await session.execute(select(Enterprise))
    enterprises = res.scalars().all()

    print(f"Found {len(enterprises)} enterprises and {len(buyers)} buyers.")

    count = 0
    for ent in enterprises:
        if ent.short_name == "НапитокСнаб" or "Напиток" in ent.short_name:
            print(f"Skipping {ent.short_name}")
            continue
        
        # Check if already has reviews to avoid duplicates if run multiple times
        res_rev = await session.execute(select(EnterpriseReview).where(EnterpriseReview.target_enterprise_id == ent.id))
        if res_rev.scalars().first():
            continue

        num_reviews = random.randint(2, 5)
        for _ in range(num_reviews):
            author = random.choice(buyers)
            review = EnterpriseReview(
                author_user_id=author.id,
                target_enterprise_id=ent.id,
                rating=random.randint(3, 5),
                comment=random.choice(REVIEWS_POOL)
            )
            session.add(review)
            count += 1

    await session.commit()
    print(f"Seeded {count} reviews.")

if __name__ == "__main__":
    asyncio.run(seed())

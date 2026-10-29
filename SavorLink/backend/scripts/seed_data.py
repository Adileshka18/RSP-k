"""
Скрипт заполнения данных в БД:
- Обновляет описания товаров (у которых нет description)
- Добавляет телефоны и emails поставщикам
- Устанавливает quantity_in_stock = 100 для товаров без остатка
"""

import asyncio
import sys
import os

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/savorlink")

PRODUCT_DESCRIPTIONS = {
    "Овощи и зелень": [
        "Свежие {name}, выращенные в теплицах без использования пестицидов. Поставка ежедневно под заказ.",
        "Отборные {name} высшего качества, собранные в экологически чистых условиях. Идеальны для ресторанного меню.",
        "Сезонные {name} от проверенных фермеров. Гарантированная свежесть и насыщенный вкус.",
    ],
    "Мясо и птица": [
        "{name} охлаждённое, от фермерских хозяйств. Без добавок и антибиотиков, строгий ветеринарный контроль.",
        "Высококачественное {name}, идеально для профессиональной кухни. Разделка по запросу.",
        "{name} от надёжных производителей с полным соблюдением норм хранения и транспортировки.",
    ],
    "Молочные продукты": [
        "{name} из натурального молока. Производство в соответствии с ГОСТом, без консервантов.",
        "Свежее {name} с минимальным сроком хранения и максимальной пользой. Постоянные поставки.",
        "{name} от местных молочных ферм. Контроль качества на каждом этапе производства.",
    ],
    "Бакалея": [
        "{name} высшего сорта, тщательно отобранное и упакованное. Оптовые поставки с доставкой.",
        "Качественное {name} от ведущих производителей. Гарантированный срок годности и сохранность.",
        "{name} для профессиональной кухни. Стабильное качество и выгодные условия сотрудничества.",
    ],
    "Напитки": [
        "{name} — натуральный состав без консервантов и искусственных добавок. Поставки под заказ.",
        "Свежее {name} с производства. Оптимальные условия хранения и доставки.",
        "{name} высокого качества, подходящее для ресторанного обслуживания и барного меню.",
    ],
}

PHONES = [
    "+7 (495) 123-45-67",
    "+7 (812) 234-56-78",
    "+7 (800) 345-67-89",
    "+7 (495) 456-78-90",
    "+7 (495) 567-89-01",
    "+7 (499) 678-90-12",
    "+7 (926) 789-01-23",
]

EMAILS = [
    "sales@agrolog.ru",
    "info@supply-fresh.ru",
    "order@foodpro.ru",
    "contact@farmlink.ru",
    "hello@agrosupply.ru",
    "partner@freshmarket.ru",
    "supply@agrolink.ru",
]


async def seed():
    from backend.database.models import Product, Enterprise

    engine = create_async_engine(DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        # ── 1. Обновляем продукты без описания ────────────────────────────────────
        result = await session.execute(
            select(Product)
        )
        all_products = result.scalars().all()
        print(f"Всего товаров: {len(all_products)}")

        updated_desc = 0
        updated_stock = 0
        for i, product in enumerate(all_products):
            changed = False

            # Описание
            if not product.description:
                # Получаем категорию через ID из уже загруженных данных
                from backend.database.models import Category
                cat_res = await session.execute(select(Category).where(Category.id == product.category_id))
                cat = cat_res.scalars().first()
                cat_name = cat.name if cat else "Бакалея"

                templates = PRODUCT_DESCRIPTIONS.get(cat_name, PRODUCT_DESCRIPTIONS["Бакалея"])
                template = templates[i % len(templates)]
                product.description = template.format(name=product.name.lower())
                updated_desc += 1
                changed = True

            # Остаток
            if product.quantity_in_stock is None:
                product.quantity_in_stock = 100 + (i * 20 % 400)
                updated_stock += 1
                changed = True

        print(f"  Обновлено описаний: {updated_desc}")
        print(f"  Установлен остаток для: {updated_stock} товаров")

        # ── 2. Обновляем предприятия ──────────────────────────────────────────────
        ent_result = await session.execute(select(Enterprise))
        all_enterprises = ent_result.scalars().all()
        print(f"\nВсего предприятий: {len(all_enterprises)}")

        updated_phones = 0
        updated_emails = 0
        for i, ent in enumerate(all_enterprises):
            if not ent.phone:
                ent.phone = PHONES[i % len(PHONES)]
                updated_phones += 1
            if not ent.email:
                ent.email = EMAILS[i % len(EMAILS)]
                updated_emails += 1

        print(f"  Добавлено телефонов: {updated_phones}")
        print(f"  Добавлено email: {updated_emails}")

        await session.commit()
        print("\nДанные успешно обновлены!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

import asyncio
from sqlalchemy import select, func, delete
from backend.database.session import get_session
from backend.database.models import EnterpriseReview

async def cleanup():
    session_gen = get_session()
    session = await session_gen.__anext__()

    # 1. Find duplicate pairs
    stmt = (
        select(EnterpriseReview.author_user_id, EnterpriseReview.target_enterprise_id)
        .group_by(EnterpriseReview.author_user_id, EnterpriseReview.target_enterprise_id)
        .having(func.count() > 1)
    )
    res = await session.execute(stmt)
    duplicates = res.all()

    print(f"Found {len(duplicates)} pairs with duplicates.")

    for author_id, target_id in duplicates:
        # 2. For each pair, find all review IDs ordered by creation date
        stmt_ids = (
            select(EnterpriseReview.id)
            .where(
                EnterpriseReview.author_user_id == author_id,
                EnterpriseReview.target_enterprise_id == target_id
            )
            .order_by(EnterpriseReview.created_at.desc())
        )
        res_ids = await session.execute(stmt_ids)
        ids = res_ids.scalars().all()
        
        # Keep the first (latest) one, delete the rest
        ids_to_delete = ids[1:]
        print(f"Deleting {len(ids_to_delete)} reviews for author {author_id} target {target_id}")
        
        delete_stmt = delete(EnterpriseReview).where(EnterpriseReview.id.in_(ids_to_delete))
        await session.execute(delete_stmt)

    await session.commit()
    print("Cleanup completed.")

if __name__ == "__main__":
    asyncio.run(cleanup())

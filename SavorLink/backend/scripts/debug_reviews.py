import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.database.session import get_session
from backend.database.models import EnterpriseReview
from backend.modules.review.schemas import EnterpriseReviewRead
from pydantic import TypeAdapter
from typing import List

async def test_get_reviews():
    session_gen = get_session()
    session = await session_gen.__anext__()
    
    try:
        stmt = select(EnterpriseReview).options(selectinload(EnterpriseReview.author_user)).limit(5)
        res = await session.execute(stmt)
        reviews = res.scalars().all()
        print(f"Fetched {len(reviews)} reviews")
        
        # Try to validate with Pydantic
        adapter = TypeAdapter(List[EnterpriseReviewRead])
        validated = adapter.validate_python(reviews)
        print("Validation Successful")
        for rv in validated:
            print(f"Review {rv.id} by {rv.author_user}")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_get_reviews())

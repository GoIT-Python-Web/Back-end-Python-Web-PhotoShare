from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User
from src.repositories.users import get_user_by_email

async def create_first_admin(db: AsyncSession):
    admin_email = "admin@example.com"
    existing_admin = await get_user_by_email(db, admin_email)  
    
    if not existing_admin:
        admin = User(
            email=admin_email,
            password="hashed_password",
            role="admin"
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)


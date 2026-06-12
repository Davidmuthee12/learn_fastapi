from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schemas.seller import SellerCreate
from app.database.models import Seller

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    async def add(self, credentials: SellerCreate) -> Seller:
        seller = Seller(
            **credentials.model_dump(exclude=["password"]),
            # Hashed password
            password_hash=password_context.hash(credentials.password),
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller

    async def token(self, email, password) -> str:
        # validate the credentials
        result = await self.session.execute(
            select(Seller).Where(Seller.email == email),
        )
        seller = result.scalar()

        if seller is None:
            raise HTTPException(
                status=status.HTTP_404_NOT_FOUND,
                detail="seller with given email is not found",
            )

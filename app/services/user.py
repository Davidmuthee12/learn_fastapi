from fastapi import HTTPException, status, BackgroundTasks
from passlib.context import CryptContext
from app.utils import generate_access_token, generate_url_safe_token
from learn_python.app.services.notification import NotificationService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.config import app_settings

from .base import BaseService

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(BaseService):
    def __init__(self, model: User, session: AsyncSession, tasks: BackgroundTasks):
        self.model = model
        self.session = session
        self.notification_service = NotificationService(tasks)

    async def _add_user(self, data: dict):
        user = self.model(
            **data,
            password_hash=password_context.hash(data["password"]),
        )
        user = await self._add(user)

        token = generate_url_safe_token(
            {
                "email": user.email,
                "id": user.id,
            }
        )

        self.notification_service.send_email_with_template(
            recipients=[user.email],
            subject="Verify Your Account with FastShip",
            context={
                "username": user.name,
                "verification_url": f"http://{app_settings.APP_DOMAIN}/user/verify?token={token}",
            },
            template_name="mail_email_verify.html",
        )

        return user

    async def _get_by_email(self, email) -> User | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email),
        )

    async def _generate_token(self, email, password) -> str:
        # validate the credentials
        user = await self._get_by_email(email)

        if user is None or not password_context.verify(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified",
            )

        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),
                }
            }
        )

import asyncio

from fastapi_mail import ConnectionConfig, FastMail, MessageType, MessageSchema
from app.config import notification_settings

fastmail = FastMail(
    ConnectionConfig(
        **notification_settings.model_dump(),
    )
)


async def send_message():
    await fastmail.send_message(
        message=MessageSchema(
            recipients=["oyvta@mailto.plus"],
            subject="Your email delivered with fastship... kaboooom",
            body="Things are about to get interesting....",
            subtype=MessageType.plain,
        )
    )
    print("Email sent!")


asyncio.run(send_message())

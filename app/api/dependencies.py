from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from app.utils import decode_access_token
from app.database.models import Seller, DeliveryPartner
from app.database.redis import is_jti_blacklisted
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import oauth2_scheme_seller, oauth2_scheme_partner
from app.database.session import get_session
from app.services.seller import SellerService
from app.services.shipment import ShipmentService


# Asynchronous database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Asynchronous database session dep annotation
async def _get_access_token(token: str):
    data = decode_access_token(token)

    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    return data


async def get_seller_access_token(
    token: Annotated[str, Depends(oauth2_scheme_seller)],
) -> dict:
    return await _get_access_token(token)


async def get_partner_access_token(
    token: Annotated[str, Depends(oauth2_scheme_partner)],
) -> dict:
    return await _get_access_token(token)


# Logged in seller
async def get_current_seller(
    token_data: Annotated[dict, Depends(get_seller_access_token)],
    session: SessionDep,
):
    seller = await session.get(Seller, UUID(token_data["user"]["id"]))

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )

    return seller


# Logged in parner
async def get_current_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
    session: SessionDep,
):
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))

    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_unauthorized,
            detail="Not Authorized",
        )

    return partner


# Shipment service dep
def get_shipment_service(session: SessionDep):
    return ShipmentService(session)


# Seller service dep
def get_seller_service(session: SessionDep):
    return SellerService(session)


# Seller Dep
SellerDep = Annotated[
    Seller,
    Depends(get_current_seller),
]

# Partner Dep
DeliveryPartnerDep = Annotated[
    DeliveryPartner,
    Depends(get_current_partner),
]


# Shipment service dep annotation
ShipmentServiceDep = Annotated[
    ShipmentService,
    Depends(get_shipment_service),
]

# Seller service dep annotation
SellerServiceDep = Annotated[
    SellerService,
    Depends(get_seller_service),
]

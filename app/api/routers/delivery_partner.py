from math import ceil
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import asc, desc, select

from app.api.tag import APITag
from app.core.exceptions import NothingToUpdate
from app.database.models import Shipment
from app.database.redis import add_jti_to_blacklist

from ..dependencies import (
    DeliveryPartnerDep,
    DeliveryPartnerServiceDep,
    SessionDep,
    get_partner_access_token,
)
from ..schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerShipments,
    DeliveryPartnerUpdate,
)
from ..schemas.shipment import ShipmentRead

router = APIRouter(prefix="/partner", tags=[APITag.PARTNER])


### Register a new delivery partner
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    seller: DeliveryPartnerCreate,
    service: DeliveryPartnerServiceDep,
):
    return await service.add(seller)


### Login a delivery partner
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: DeliveryPartnerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token": token,
        "type": "jwt",
    }


### Get logged in delivery partner profile
@router.get("/me", response_model=DeliveryPartnerRead)
async def get_delivery_partner_profile(partner: DeliveryPartnerDep):
    return partner


### This can be used in any endpoint that may require the same!!!😍
class PaginationParams(BaseModel):
    page: int = 1
    pageSize: int = 10
    order: Literal["asc", "desc"] = "asc"


def get_pagination_params(
    page: int = 1,
    pageSize: int = 10,
    order: Literal["asc", "desc"] = "asc",
) -> PaginationParams:
    return PaginationParams(page=page, pageSize=pageSize, order=order)


### Get logged in delivery partner shipments
@router.get("/shipments", response_model=DeliveryPartnerShipments)
async def get_shipments(
    partner: DeliveryPartnerDep,
    session: SessionDep,
    pagination: Annotated[PaginationParams.Depends(get_pagination_params)],
):
    result = await session.scalars(
        select(Shipment)
        .where(Shipment.delivery_partner_id == partner.id)
        .limit(pagination.pageSize)
        .offset((pagination.page - 1) * pagination.pageSize)
        .order_by(
            asc(Shipment.created_at)
            if pagination.order == "asc"
            else desc(Shipment.created_at)
        )
    )

    return {
        "shipments": result.all(),
        "total_shipments": len(partner.shipments),
        "page": pagination.page,
        "total_pages": ceil(len(partner.shipments) / pagination.pageSize),
    }


### Update the logged in delivery partner
@router.post("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: DeliveryPartnerDep,
    service: DeliveryPartnerServiceDep,
):
    # Update data with given fields
    update = partner_update.model_dump(exclude_none=True)

    if not update:
        raise NothingToUpdate()

    return await service.update(
        partner.sqlmodel_update(update),
    )


### Verify delivery partner Email
@router.get("/verify")
async def verify_delivery_partner_email(token: str, service: DeliveryPartnerDep):
    service.verify_email(token)
    return {"detail": "Account verified"}


### Logout a delivery partner
@router.get("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "Successfully logged out"}

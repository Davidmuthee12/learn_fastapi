from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import oauth2_scheme
from app.database.redis import add_jti_to_blacklist

from ..dependencies import DeliveryPartnerDep, get_partner_access_token
from ..schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUpdate,
)

router = APIRouter(prefix="/partner", tags=["Delivery partner"])


### Register a delivery partnet
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_seller(
    seller: DeliveryPartnerCreate,
    service,
):
    return await service.add(seller)


### Login the seller
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service,
):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token": token,
        "type": "jwt",
    }


### Update delivery partner
@router.post("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: DeliveryPartnerRead,
    service,
):
    return await service.update(
        partner.sqlmodel_update(partner_update),
    )


### Logout the delivery partner
@router.get("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully logged out",
    }

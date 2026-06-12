from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import oauth2_scheme

from ..dependencies import SellerServiceDep
from ..schemas.seller import SellerCreate, SellerRead

router = APIRouter(prefix="/seller", tags=["Seller"])


### Register a seller
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


### Login the seller
@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token": token,
        "type": "jwt",
    }


### Logout the seller
@router.get("/logout")
async def logout_seller(
    token_data: Annotated[str, Depends(oauth2_scheme)],
):
    token_data["jti"]

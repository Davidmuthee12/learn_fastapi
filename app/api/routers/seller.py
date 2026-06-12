from fastapi import APIRouter

from ..schemas.seller import SellerCreate

router = APIRouter(prefix="/seller")


@router.post("/signup")
def register_seller(seller: SellerCreate):
    pass

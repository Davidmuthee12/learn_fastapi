from pydantic import BaseModel, EmailStr, Field


class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_handling_capacity: int


class DeliveryPartnerRead(BaseDeliveryPartner):
    pass


class DeliveryPartnerUpdate(BaseModel):
    serviceable_zip_codes: list[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)


class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str


class Shipment(BaseModel):
    content: str


class DeliveryPartnerShipments(BaseModel):
    shipments: list[Shipment]
    total_shipments: int
    page: int
    total_pages: int

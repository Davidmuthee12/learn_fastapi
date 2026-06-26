from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.database.models import Shipment, ShipmentStatus, TagName


class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    destination: int | None = Field(
        default=None,
        description="Instead use location, Location Zipcode",
        examples=[11001, 11002, 11003],
        deprecated=True,
    )
    location: int | None = Field(default=None)


class TagRead(BaseModel):
    name: TagName
    instructions: str


class ShipmentEventRead(BaseModel):
    id: UUID | None = None
    created_at: datetime
    location: int
    status: ShipmentStatus
    description: str | None = None
    shipment_id: UUID | None = None


class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEventRead]
    estimated_delivery: datetime
    tags: list[TagRead]

    @model_validator(mode="before")
    @classmethod
    def ensure_timeline(cls, data: Any):
        if not isinstance(data, Shipment):
            if isinstance(data, dict) and not data.get("timeline"):
                data["timeline"] = cls._fallback_timeline(data)
            return data

        timeline = list(data.timeline)
        if timeline:
            return data

        return {
            "id": data.id,
            "content": data.content,
            "weight": data.weight,
            "destination": data.destination,
            "location": data.destination,
            "timeline": cls._fallback_timeline(data),
            "estimated_delivery": data.estimated_delivery,
            "tags": data.tags,
        }

    @staticmethod
    def _fallback_timeline(data: Any):
        get_value = (
            data.get
            if isinstance(data, dict)
            else lambda key, default=None: getattr(data, key, default)
        )
        return [
            {
                "created_at": get_value("created_at") or datetime.now(),
                "location": get_value("destination"),
                "status": ShipmentStatus.placed,
                "description": "assigned delivery partner",
                "shipment_id": get_value("id"),
            }
        ]


class ShipmentCreate(BaseShipment):
    """Shipment details to create a new shipment"""

    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def sync_location_and_destination(cls, data):
        if not isinstance(data, dict):
            return data

        location = data.get("location")
        destination = data.get("destination")

        if location is None and destination is not None:
            data["location"] = destination
        elif destination is None and location is not None:
            data["destination"] = location

        return data

    @model_validator(mode="after")
    def require_delivery_location(self):
        if self.__dict__.get("destination") is None:
            raise ValueError("location is required")

        return self


class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    verification_code: str | None = Field(default=None)
    description: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)


class ShipmentReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)

from datetime import datetime, timedelta
from uuid import UUID

from httpx import AsyncClient
import pytest
from sqlmodel import select

from app.database.models import DeliveryPartner, Seller, Shipment, ShipmentStatus
from app.tests import example
from app.tests.conftest import test_session as session_factory


@pytest.fixture(autouse=True)
def skip_token_blacklist(monkeypatch):
    async def is_not_blacklisted(jti: str):
        return False

    monkeypatch.setattr("app.api.dependencies.is_jti_blacklisted", is_not_blacklisted)


async def test_get_seller_profile(
    client: AsyncClient,
    seller_token: str,
):
    response = await client.get(
        "/seller/me",
        headers={"Authorization": f"Bearer {seller_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == example.SELLER["email"]


async def test_get_delivery_partner_profile(
    client: AsyncClient,
    partner_token: str,
):
    response = await client.get(
        "/partner/me",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == example.DELIVERY_PARTNER["email"]
    assert response.json()["serviceable_zip_codes"] == example.DELIVERY_PARTNER[
        "serviceable_zip_codes"
    ]


async def test_get_account_shipments(
    client: AsyncClient,
    seller_token: str,
    partner_token: str,
):
    shipment = example.SHIPMENT.copy()
    shipment.pop("destination")

    create_response = await client.post(
        "/shipment/",
        json=shipment,
        headers={"Authorization": f"Bearer {seller_token}"},
    )

    assert create_response.status_code == 201
    shipment_id = create_response.json()["id"]

    seller_response = await client.get(
        "/seller/shipments",
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    partner_response = await client.get(
        "/partner/shipments",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert seller_response.status_code == 200
    assert partner_response.status_code == 200
    assert shipment_id in {shipment["id"] for shipment in seller_response.json()}
    assert shipment_id in {shipment["id"] for shipment in partner_response.json()}


async def test_get_shipments_backfills_empty_timeline(
    client: AsyncClient,
    seller_token: str,
):
    async with session_factory() as session:
        seller = await session.scalar(
            select(Seller).where(Seller.email == example.SELLER["email"])
        )
        partner = await session.scalar(
            select(DeliveryPartner).where(
                DeliveryPartner.email == example.DELIVERY_PARTNER["email"]
            )
        )
        shipment = Shipment(
            content="Legacy package",
            weight=2,
            destination=11004,
            estimated_delivery=datetime.now() + timedelta(days=3),
            client_contact_email="legacy@xmailg.one",
            seller_id=seller.id,
            delivery_partner_id=partner.id,
        )
        session.add(shipment)
        await session.commit()
        await session.refresh(shipment)
        shipment_id = str(shipment.id)

    response = await client.get(
        "/seller/shipments",
        headers={"Authorization": f"Bearer {seller_token}"},
    )

    assert response.status_code == 200
    legacy_shipment = next(
        shipment for shipment in response.json() if shipment["id"] == shipment_id
    )
    assert legacy_shipment["timeline"][-1]["status"] == ShipmentStatus.placed
    assert legacy_shipment["timeline"][-1]["created_at"] is not None

    async with session_factory() as session:
        shipment = await session.get(Shipment, UUID(shipment_id))
        await session.delete(shipment)
        await session.commit()

from sqlalchemy import create_engine
from sqlmodel import SQLModel

engine = create_engine(
    url="sqlite:///sqlite.db",
    echo=True,
    connect_args={"check_same_thread": False},
)


from .models import Shipment

SQLModel.metadata.create_all(bind=engine)

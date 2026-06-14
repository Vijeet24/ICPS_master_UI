import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    READY_TO_SHIP = "READY_TO_SHIP"
    SHIPPED = "SHIPPED"


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(64), nullable=False, index=True)
    buyer_id = Column(String(13), nullable=False, index=True)
    seller_id = Column(String(13), nullable=True)
    correlation_message_id = Column(String(64), nullable=False, unique=True, index=True)
    received_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.RECEIVED, nullable=False, index=True)
    raw_po_json = Column(Text, nullable=False)

    acknowledgement = relationship(
        "Acknowledgement", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    shipment = relationship(
        "Shipment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )


class Acknowledgement(Base):
    __tablename__ = "acknowledgements"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    message_id = Column(String(64), nullable=False, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    raw_855_json = Column(Text, nullable=False)

    order = relationship("Order", back_populates="acknowledgement")


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(64), nullable=False, unique=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    tracking_number = Column(String(64), nullable=False)
    carrier = Column(String(128), nullable=False)
    ship_date = Column(DateTime, nullable=False)
    raw_856_json = Column(Text, nullable=False)

    order = relationship("Order", back_populates="shipment")


class MessageAudit(Base):
    __tablename__ = "message_audit"
    __table_args__ = (UniqueConstraint("message_id", "direction", name="uq_message_audit_id_direction"),)

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(64), nullable=False, index=True)
    message_type = Column(String(64), nullable=False, index=True)
    direction = Column(Enum(MessageDirection), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    payload = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="PROCESSED")
    correlation_id = Column(String(64), nullable=True, index=True)

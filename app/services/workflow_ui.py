import json
import logging
from datetime import datetime

from app.order_models import Order, OrderStatus
from app.schemas_orders import (
    AcknowledgementResponse,
    MessageAuditResponse,
    OrderDetailResponse,
    OrderSummaryResponse,
    ShipmentResponse,
    WorkflowStepResponse,
)

logger = logging.getLogger(__name__)

WORKFLOW_STEPS = [
    (1, "Receive PO (850)", OrderStatus.RECEIVED),
    (2, "Send Acknowledgement (855)", OrderStatus.ACKNOWLEDGED),
    (3, "Fulfillment", OrderStatus.READY_TO_SHIP),
    (4, "Ship ASN (856)", OrderStatus.SHIPPED),
]

STATUS_ORDER = {
    OrderStatus.RECEIVED: 1,
    OrderStatus.ACKNOWLEDGED: 2,
    OrderStatus.READY_TO_SHIP: 3,
    OrderStatus.SHIPPED: 4,
}


def _line_item_count(order: Order) -> int:
    try:
        payload = json.loads(order.raw_po_json)
        return len(payload.get("payload", {}).get("line_items", []))
    except (json.JSONDecodeError, TypeError):
        return 0


def serialize_order_summary(order: Order) -> OrderSummaryResponse:
    return OrderSummaryResponse(
        id=order.id,
        po_number=order.po_number,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        correlation_message_id=order.correlation_message_id,
        received_timestamp=order.received_timestamp,
        status=order.status.value,
        line_item_count=_line_item_count(order),
        has_acknowledgement=order.acknowledgement is not None,
        has_shipment=order.shipment is not None,
    )


def _step_timestamp(order: Order, step_status: OrderStatus) -> datetime | None:
    if step_status == OrderStatus.RECEIVED:
        return order.received_timestamp
    if step_status == OrderStatus.ACKNOWLEDGED and order.acknowledgement:
        return order.acknowledgement.timestamp
    if step_status == OrderStatus.READY_TO_SHIP and order.status in (
        OrderStatus.READY_TO_SHIP,
        OrderStatus.SHIPPED,
    ):
        return order.shipment.ship_date if order.shipment else None
    if step_status == OrderStatus.SHIPPED and order.shipment:
        return order.shipment.ship_date
    return None


def build_workflow_steps(order: Order) -> list[WorkflowStepResponse]:
    current = STATUS_ORDER[order.status]
    steps = []
    for number, name, step_status in WORKFLOW_STEPS:
        completed = current >= STATUS_ORDER[step_status]
        step_state = "completed" if completed else "pending"
        if order.status == step_status:
            step_state = "active"
        steps.append(
            WorkflowStepResponse(
                step=number,
                name=name,
                status=step_state,
                completed=completed,
                timestamp=_step_timestamp(order, step_status),
                description=step_status.value,
            )
        )
    return steps


def serialize_order_detail(order: Order) -> OrderDetailResponse:
    acknowledgement = None
    if order.acknowledgement:
        acknowledgement = AcknowledgementResponse(
            id=order.acknowledgement.id,
            message_id=order.acknowledgement.message_id,
            timestamp=order.acknowledgement.timestamp,
            raw_855_json=order.acknowledgement.raw_855_json,
        )

    shipment = None
    if order.shipment:
        shipment = ShipmentResponse(
            id=order.shipment.id,
            shipment_id=order.shipment.shipment_id,
            tracking_number=order.shipment.tracking_number,
            carrier=order.shipment.carrier,
            ship_date=order.shipment.ship_date,
            raw_856_json=order.shipment.raw_856_json,
        )

    return OrderDetailResponse(
        id=order.id,
        po_number=order.po_number,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        correlation_message_id=order.correlation_message_id,
        received_timestamp=order.received_timestamp,
        status=order.status.value,
        raw_po_json=order.raw_po_json,
        acknowledgement=acknowledgement,
        shipment=shipment,
        workflow_steps=build_workflow_steps(order),
    )


def serialize_audit(entry) -> MessageAuditResponse:
    return MessageAuditResponse(
        id=entry.id,
        message_id=entry.message_id,
        message_type=entry.message_type,
        direction=entry.direction.value,
        timestamp=entry.timestamp,
        payload=entry.payload,
        status=entry.status,
        correlation_id=entry.correlation_id,
    )

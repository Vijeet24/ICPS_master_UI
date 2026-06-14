import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any


def generate_edi_855(
    po_message: dict,
    parsed: dict,
    seller_gln: str,
    seller_name: str,
    buyer_gln: str,
    buyer_name: str,
) -> dict[str, Any]:
    payload = po_message.get("payload", {})
    line_items = payload.get("line_items", [])
    promised_ship_date = (date.today() + timedelta(days=3)).isoformat()

    ack_lines = []
    for item in line_items:
        ack_lines.append(
            {
                "po_line_number": item.get("line_number"),
                "line_status": {"code": "IA"},
                "item_identification": item.get("item_identification", {}),
                "quantity_ordered": item.get("quantity_ordered"),
                "quantity_acknowledged": item.get("quantity_ordered"),
                "unit_of_measure": item.get("unit_of_measure"),
            }
        )

    return {
        "message_id": f"MSG-855-{uuid.uuid4()}",
        "message_type": "EDI_855_PURCHASE_ORDER_ACK",
        "schema_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sender": {"gln": seller_gln, "name": seller_name},
        "receiver": {"gln": buyer_gln, "name": buyer_name},
        "correlation_id": parsed["message_id"],
        "payload": {
            "transaction": {
                "type": "855",
                "control_number": payload.get("transaction", {}).get("control_number", "000000001"),
                "version": "1.0",
            },
            "po_reference": {
                "po_number": parsed["po_number"],
                "original_message_id": parsed["message_id"],
                "acknowledgment_status": {"code": "AC"},
            },
            "parties": {
                "buyer": {"gln": buyer_gln},
                "seller": {"gln": seller_gln},
            },
            "line_items": ack_lines,
            "schedule": {"promised_ship_date": promised_ship_date},
        },
    }

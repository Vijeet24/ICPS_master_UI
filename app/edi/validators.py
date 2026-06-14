from typing import Any


class EdiValidationError(Exception):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field
        self.message = message


def _require_dict(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise EdiValidationError(f"{field} must be an object", field)
    return value


def _require_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EdiValidationError(f"{field} is required", field)
    return value.strip()


def validate_edi_850(message: dict) -> dict:
    root = _require_dict(message, "message")
    _require_str(root.get("message_id"), "message_id")
    message_type = _require_str(root.get("message_type"), "message_type")
    if message_type != "EDI_850_PURCHASE_ORDER":
        raise EdiValidationError("message_type must be EDI_850_PURCHASE_ORDER", "message_type")

    payload = _require_dict(root.get("payload"), "payload")
    transaction = _require_dict(payload.get("transaction"), "payload.transaction")
    if _require_str(transaction.get("type"), "payload.transaction.type") != "850":
        raise EdiValidationError("transaction type must be 850", "payload.transaction.type")

    purchase_order = _require_dict(payload.get("purchase_order"), "payload.purchase_order")
    po_number = _require_str(purchase_order.get("po_number"), "payload.purchase_order.po_number")

    parties = _require_dict(payload.get("parties"), "payload.parties")
    buyer = _require_dict(parties.get("buyer"), "payload.parties.buyer")
    buyer_gln = _require_str(buyer.get("gln"), "payload.parties.buyer.gln")

    line_items = payload.get("line_items")
    if not isinstance(line_items, list) or not line_items:
        raise EdiValidationError("payload.line_items must be a non-empty array", "payload.line_items")

    for index, item in enumerate(line_items, start=1):
        line = _require_dict(item, f"payload.line_items[{index}]")
        _require_str(line.get("unit_of_measure"), f"payload.line_items[{index}].unit_of_measure")
        qty = line.get("quantity_ordered")
        if not isinstance(qty, (int, float)) or qty <= 0:
            raise EdiValidationError(
                f"payload.line_items[{index}].quantity_ordered must be positive",
                f"payload.line_items[{index}].quantity_ordered",
            )

    return {
        "message_id": root["message_id"],
        "po_number": po_number,
        "buyer_id": buyer_gln,
        "seller_id": parties.get("seller", {}).get("gln"),
        "line_items": line_items,
    }

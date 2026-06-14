import json
from pathlib import Path

import pytest

from app.edi.validators import EdiValidationError, validate_edi_850

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def load_sample(name: str) -> dict:
    return json.loads((SAMPLES_DIR / name).read_text(encoding="utf-8"))


def test_validate_edi_850_accepts_sample():
    message = load_sample("inbound_850.json")
    parsed = validate_edi_850(message)
    assert parsed["po_number"] == "PO-20260529-1561"
    assert parsed["buyer_id"] == "1514032003830"
    assert parsed["message_id"] == message["message_id"]


def test_validate_edi_850_rejects_missing_po_number():
    message = load_sample("inbound_850.json")
    del message["payload"]["purchase_order"]["po_number"]
    with pytest.raises(EdiValidationError):
        validate_edi_850(message)


def test_validate_edi_850_rejects_wrong_message_type():
    message = load_sample("inbound_850.json")
    message["message_type"] = "EDI_999_UNKNOWN"
    with pytest.raises(EdiValidationError):
        validate_edi_850(message)

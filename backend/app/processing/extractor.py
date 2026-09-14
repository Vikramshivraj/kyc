import re


def clean_value(value: str) -> str:
    """Clean OCR extracted values."""
    return re.sub(r"\s+", " ", value).strip()


def extract_fields(text: str) -> dict:
    normalized_text = text.strip()

    fields = {
        "name": None,
        "document_number": None,
        "date_of_birth": None,
    }

    # -----------------------------
    # Full Name
    # -----------------------------
    name_match = re.search(
        r"(?:Full\s+Name|Name)\s*[:\-]?\s*(.+)",
        normalized_text,
        re.IGNORECASE,
    )

    if name_match:
        fields["name"] = clean_value(name_match.group(1))

    # -----------------------------
    # Document Number
    # -----------------------------
    document_number_match = re.search(
        r"Document\s+Number\s*[:\-]?\s*([A-Za-z0-9-]+)",
        normalized_text,
        re.IGNORECASE,
    )

    if document_number_match:
        fields["document_number"] = clean_value(
            document_number_match.group(1)
        )

    # -----------------------------
    # Date of Birth
    # Supports:
    # 15-08-1998
    # 15/08/1998
    # -----------------------------
    dob_match = re.search(
        r"(?:Date\s+of\s+Birth|DOB)\s*[:\-]?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
        normalized_text,
        re.IGNORECASE,
    )

    if dob_match:
        fields["date_of_birth"] = (
            dob_match.group(1)
            .replace("/", "-")
            .strip()
        )

    return fields


def identify_document_type(text: str) -> str:
    normalized_text = text.lower()

    if "synthetic kyc document" in normalized_text:
        return "KYC_DOCUMENT"

    if "sample kyc document" in normalized_text:
        return "KYC_DOCUMENT"

    if "kyc / identity proof" in normalized_text:
        return "KYC_DOCUMENT"

    if "pan" in normalized_text:
        return "PAN"

    if "passport" in normalized_text:
        return "PASSPORT"

    return "UNKNOWN"
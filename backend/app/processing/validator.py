from datetime import datetime


def validate_fields(fields: dict) -> dict:
    errors = []

    name = fields.get("name")
    document_number = fields.get("document_number")
    date_of_birth = fields.get("date_of_birth")

    # Name validation
    if not name:
        errors.append("Name is missing")

    # Document number validation
    if not document_number:
        errors.append("Document number is missing")
    elif len(document_number) < 6:
        errors.append("Document number is too short")

    # Date of birth validation
    if not date_of_birth:
        errors.append("Date of birth is missing")
    else:
        try:
            datetime.strptime(date_of_birth, "%d-%m-%Y")
        except ValueError:
            errors.append("Invalid date of birth format")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }
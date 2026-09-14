def calculate_confidence(
    fields: dict,
    validation: dict,
) -> float:
    score = 0

    if fields.get("name"):
        score += 30

    if fields.get("document_number"):
        score += 30

    if fields.get("date_of_birth"):
        score += 20

    if validation["valid"]:
        score += 20

    return float(score)

def calculate_risk(confidence: float, validation: dict) -> dict:
    reasons = []

    if not validation["valid"]:
        reasons.extend(validation["errors"])

    if confidence >= 90:
        risk_level = "LOW"
    elif confidence >= 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    if risk_level == "HIGH":
        reasons.append("Manual review required")

    return {
        "risk_level": risk_level,
        "reasons": reasons,
    }
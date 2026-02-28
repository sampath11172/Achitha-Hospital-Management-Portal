from datetime import datetime


def patient_risk_score(age: int, diagnosis: str, history: str) -> int:
    score = 0
    if age >= 60:
        score += 30
    elif age >= 45:
        score += 20

    risk_terms = ["cardiac", "hypertension", "diabetes", "stroke", "cancer"]
    for term in risk_terms:
        if term in (diagnosis or "").lower() or term in (history or "").lower():
            score += 15

    if "smoker" in (history or "").lower():
        score += 10

    return min(score, 100)


def triage_priority(vitals: dict) -> str:
    bpm = vitals.get("heart_rate", 75)
    spo2 = vitals.get("spo2", 98)
    bp_sys = vitals.get("bp_sys", 120)

    if spo2 < 88 or bpm > 130 or bp_sys > 180:
        return "Critical"
    if spo2 < 93 or bpm > 110 or bp_sys > 150:
        return "High"
    return "Moderate"


def drug_interaction_alert(drugs: list[str]) -> list[str]:
    alerts = []
    pairs = {
        frozenset(["warfarin", "aspirin"]): "Bleeding risk increase",
        frozenset(["metformin", "contrast"]): "Lactic acidosis risk",
        frozenset(["insulin", "beta blockers"]): "Masked hypoglycemia signs",
    }
    norm = [d.strip().lower() for d in drugs]
    for combo, message in pairs.items():
        if combo.issubset(set(norm)):
            alerts.append(message)
    return alerts


def inventory_restock_alert(quantity: int, threshold: int, expiry_date: str) -> str:
    days_left = 365
    try:
        days_left = (datetime.fromisoformat(expiry_date) - datetime.now()).days
    except ValueError:
        pass

    if quantity < threshold and days_left < 60:
        return "Urgent restock and replace expiring stock"
    if quantity < threshold:
        return "Restock recommended"
    if days_left < 60:
        return "Expiry approaching"
    return "Stock healthy"


def emergency_severity_rank(severity: int, age: int) -> int:
    rank = severity * 10
    if age >= 65:
        rank += 5
    return min(rank, 100)


def reminder_schedule(appointment_date: str) -> list[str]:
    return [
        f"Send SMS 24h before {appointment_date}",
        f"Send Email 2h before {appointment_date}",
        f"Push reminder 15m before {appointment_date}",
    ]

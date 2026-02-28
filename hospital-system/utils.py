from datetime import datetime


def generate_patient_uid(seq: int) -> str:
    year = datetime.now().year
    return f"P-{year}-{seq:03d}"


def html_table(rows, columns):
    header = "".join(f"<th>{col}</th>" for col in columns)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{row[col]}</td>" for col in columns) + "</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def pseudo_pdf_invoice(bill):
    lines = [
        "SHMS INVOICE",
        "=" * 36,
        f"Patient: {bill['patient_uid']}",
        f"Treatment: ${bill['treatment_cost']:.2f}",
        f"Medicine: ${bill['medicine_cost']:.2f}",
        f"Room: ${bill['room_cost']:.2f}",
        f"Total: ${bill['treatment_cost'] + bill['medicine_cost'] + bill['room_cost']:.2f}",
        f"Insurance Approved: {'Yes' if bill['insurance_approved'] else 'No'}",
    ]
    return "\n".join(lines)

import json
from datetime import datetime

LOG_FILE = "logs/audit_log.jsonl"


def log_action(
    invoice_no,
    client_name,
    days_overdue,
    stage,
    status,
    delivery_mode=None
):

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "invoice_no": invoice_no,
        "client_name": client_name,
        "days_overdue": int(days_overdue),
        "stage": stage,
        "status": status,
        "delivery_mode": delivery_mode
    }

    with open(LOG_FILE, "a") as file:
        file.write(json.dumps(log_entry) + "\n")
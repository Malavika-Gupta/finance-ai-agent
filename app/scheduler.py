from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from app.data_loader import load_invoice_data
from app.escalation_engine import determine_stage
from app.email_generator import generate_email
from app.sender import mock_send_email
from app.logger import log_action


def process_invoices():

    print("\n===================================")
    print("RUNNING SCHEDULED INVOICE CHECK")
    print("===================================\n")

    # Load invoice data
    df = load_invoice_data("data/invoices.csv")

    # Calculate overdue days
    today = datetime.today()

    df["days_overdue"] = (today - df["due_date"]).dt.days

    # Determine escalation stage
    df["escalation_stage"] = df["days_overdue"].apply(determine_stage)

    # Process invoices
    for _, row in df.iterrows():

        print(f"\nProcessing {row['invoice_no']}")

        # Skip escalation cases
        if row["escalation_stage"] == "ESCALATE TO FINANCE TEAM":

            print("Flagged for manual finance/legal review.")

            continue

        # Generate AI email
        email_response = generate_email(row)

        if email_response is None:

            print("Failed to parse AI response.")

            continue

        # Mock send
        send_result = mock_send_email(
            to_email=row["email"],
            email_response=email_response
        )

        # Log result
        log_action(
            invoice_no=row["invoice_no"],
            client_name=row["client_name"],
            days_overdue=row["days_overdue"],
            stage=row["escalation_stage"],
            status=send_result["status"],
            delivery_mode=send_result["delivery_mode"]
        )


# Create scheduler
scheduler = BlockingScheduler()

# Run every 1 minute
scheduler.add_job(process_invoices, "interval", minutes=1)

print("Scheduler started...")

# Start scheduler
scheduler.start()
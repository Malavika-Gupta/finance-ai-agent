from datetime import datetime
from app.logger import log_action
from app.data_loader import load_invoice_data
from app.escalation_engine import determine_stage
from app.dispatcher import dispatch_email
from app.email_generator import generate_email


# Load invoice data
df = load_invoice_data("data/invoices.csv")

# Get today's date
today = datetime.today()

# Calculate overdue days
df["days_overdue"] = (today - df["due_date"]).dt.days

# Apply escalation logic
df["escalation_stage"] = df["days_overdue"].apply(determine_stage)

# Display results
for _, row in df.iterrows():
#for _, row in df.head(1).iterrows():

    print("\n-----------------------------")
    print(f"Invoice: {row['invoice_no']}")
    print(f"Client: {row['client_name']}")
    print(f"Days Overdue: {row['days_overdue']}")
    print(f"Assigned Stage: {row['escalation_stage']}")

    if row["escalation_stage"] == "ESCALATE TO FINANCE TEAM":
        print("Flagged for manual finance/legal review.")
        continue
    # Generate AI email
    email_response = generate_email(row)
    if email_response is None:
        print("Skipping malformed AI response.")
        continue

    print("\nGenerated Email:")

    print(f"Subject: {email_response.subject}")
    print(f"Tone: {email_response.tone}")

    print("\nBody:")
    print(email_response.body)
    # Mock send email
    send_result = dispatch_email(
        to_email=row["email"],
        email_response=email_response
    )

    # Log successful send
    log_action(
        invoice_no=row["invoice_no"],
        client_name=row["client_name"],
        days_overdue=row["days_overdue"],
        stage=row["escalation_stage"],
        status=send_result["status"],
        delivery_mode=send_result["delivery_mode"]
    )
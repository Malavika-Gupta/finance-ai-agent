import time
from datetime import datetime

import streamlit as st

from app.config import SEND_MODE
from app.data_loader import load_invoice_data
from app.email_generator import generate_email
from app.escalation_engine import determine_stage
from app.logger import log_action
from app.sender import mock_send_email

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Finance AI Agent Dashboard",
    layout="wide"
)

st.title("💰 Finance AI Agent Dashboard")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

df = load_invoice_data("data/invoices.csv")

# Ensure due_date is datetime
df["due_date"] = df["due_date"].astype("datetime64[ns]")

# Calculate overdue days
today = datetime.today()

df["days_overdue"] = (today - df["due_date"]).dt.days

# Determine escalation stage
df["escalation_stage"] = df["days_overdue"].apply(determine_stage)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("Dashboard Controls")

# Search filter
search_client = st.sidebar.text_input("🔍 Search Client")

if search_client:
    df = df[
        df["client_name"]
        .str.contains(search_client, case=False, na=False)
    ]

# Escalation stage filter
stage_filter = st.sidebar.multiselect(
    "Filter by Escalation Stage",
    options=df["escalation_stage"].unique(),
    default=df["escalation_stage"].unique()
)

df = df[df["escalation_stage"].isin(stage_filter)]

# ---------------------------------------------------
# METRICS
# ---------------------------------------------------

total_invoices = len(df)

overdue_invoices = len(df[df["days_overdue"] > 0])

escalated_cases = len(
    df[df["escalation_stage"] == "ESCALATE TO FINANCE TEAM"]
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Invoices", total_invoices)

col2.metric("Overdue Invoices", overdue_invoices)

col3.metric("Escalated Cases", escalated_cases)

st.info(f"📨 Current Delivery Mode: {SEND_MODE}")

# ---------------------------------------------------
# ESCALATION ANALYTICS
# ---------------------------------------------------

stage1_count = len(df[df["escalation_stage"].str.contains("Stage 1", na=False)])

stage2_count = len(df[df["escalation_stage"].str.contains("Stage 2", na=False)])

stage3_count = len(df[df["escalation_stage"].str.contains("Stage 3", na=False)])

stage4_count = len(df[df["escalation_stage"].str.contains("Stage 4", na=False)])

st.subheader("📈 Escalation Distribution")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Stage 1", stage1_count)

c2.metric("Stage 2", stage2_count)

c3.metric("Stage 3", stage3_count)

c4.metric("Stage 4", stage4_count)

# Bar chart
stage_counts = df["escalation_stage"].value_counts()

st.bar_chart(stage_counts)

# ---------------------------------------------------
# DATAFRAME VIEW
# ---------------------------------------------------

st.subheader("📋 Invoice Table")

st.dataframe(
    df[
        [
            "invoice_no",
            "client_name",
            "amount",
            "days_overdue",
            "escalation_stage"
        ]
    ],
    use_container_width=True
)

# ---------------------------------------------------
# CSV EXPORT
# ---------------------------------------------------

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Report",
    data=csv,
    file_name="invoice_report.csv",
    mime="text/csv"
)

# ---------------------------------------------------
# INVOICE PROCESSING QUEUE
# ---------------------------------------------------

st.subheader("🧾 Invoice Processing Queue")

for index, row in df.iterrows():

    with st.container(border=True):

        st.write(f"### Invoice: {row['invoice_no']}")
        st.write(f"Client: {row['client_name']}")
        st.write(f"Amount Due: ${row['amount']}")
        st.write(f"Days Overdue: {row['days_overdue']}")

        stage = row["escalation_stage"]

        # Stage colors
        if "Stage 1" in stage:
            st.success(f"🟢 {stage}")

        elif "Stage 2" in stage:
            st.warning(f"🟡 {stage}")

        elif "Stage 3" in stage:
            st.error(f"🟠 {stage}")

        elif "Stage 4" in stage:
            st.error(f"🔴 {stage}")

        elif "ESCALATE" in stage:
            st.error(f"⚫ {stage}")

        else:
            st.info(stage)

        # Escalation case
        if stage == "ESCALATE TO FINANCE TEAM":

            st.error("Flagged for manual finance/legal review.")

            continue

        # Generate email button
        if st.button(
            f"Generate Email - {row['invoice_no']}",
            key=f"btn_{row['invoice_no']}"
        ):

            with st.spinner("Generating AI email..."):

                start_time = time.time()

                email_response = generate_email(row)

                end_time = time.time()

                if email_response is None:
                    st.error("Failed to parse AI response.")
                    continue

                generation_time = round(end_time - start_time, 2)

                st.success("✅ Email Generated Successfully")

                st.caption(f"Generation Time: {generation_time} sec")

                # Show generated email
                with st.expander("📨 View Generated Email"):

                    st.write("### Subject")
                    st.write(email_response.subject)

                    st.write("### Tone")
                    st.write(email_response.tone)

                    st.write("### Email Body")
                    st.write(email_response.body)

                # Mock send email
                send_result = mock_send_email(
                    to_email=row["email"],
                    email_response=email_response
                )

                # Log action
                log_action(
                    invoice_no=row["invoice_no"],
                    client_name=row["client_name"],
                    days_overdue=row["days_overdue"],
                    stage=row["escalation_stage"],
                    status=send_result["status"],
                    delivery_mode=send_result["delivery_mode"]
                )

                st.success("📬 Mock email sent successfully.")

# ---------------------------------------------------
# AUDIT LOGS
# ---------------------------------------------------

st.markdown("---")

st.subheader("🗂 Audit Log History")

try:

    with open("logs/audit_log.jsonl", "r") as file:

        logs = file.readlines()

    logs.reverse()

    for log in logs[:10]:

        st.code(log, language="json")

except FileNotFoundError:

    st.warning("No audit logs found yet.")
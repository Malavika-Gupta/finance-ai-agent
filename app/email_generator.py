import ollama
import re
from app.models import EmailResponse


def _format_currency(amount) -> str:
    """Convert 18500 or '18500.00' → '$18,500'"""
    try:
        return f"${float(str(amount).replace(',', '')):,.0f}"
    except (ValueError, TypeError):
        return str(amount)


def _format_salutation(client_name: str, stage: int) -> str:
    """
    Stage 1-2 → informal first name guess  → 'Hi Acme Corp'
    Stage 3-4 → formal full name           → 'Dear Acme Corp'
    
    If client_name has multiple words, stage 1-2 uses the first word only.
    Finance teams typically address by company name, not personal name,
    unless a contact_name field is present.
    """
    name = client_name.strip()
    first_word = name.split()[0] if name else name

    if stage <= 2:
        return f"Hi {first_word}"
    else:
        return f"Dear {name}"


STAGE_PERSONAS = {
    1: {
        "role": (
            "You are a billing coordinator at a mid-sized company. "
            "You assume the client simply forgot — no accusation, no urgency. "
            "You write short, warm, human-sounding reminders. "
            "BANNED PHRASES — never use any of these: "
            "'hope this finds you well', 'please don't hesitate', 'feel free', "
            "'I completely understand', 'things can slip through the cracks', "
            "'we appreciate', 'as per', 'please be advised', 'kindly', "
            "'do not hesitate to reach out', 'feel free to contact us'. "
            "You sound like a helpful colleague, not a chatbot."
        ),
        "subject_pattern": "Quick reminder – Invoice {invoice_no}",
        "cta": "Pay now using the link below, or reply if you have already processed this.",
        "tone_label": "Warm & Friendly",
        "max_words": 80,
    },
    2: {
        "role": (
            "You are a senior accounts receivable officer. "
            "Payment is already one week late. You are polite but direct. "
            "You need a confirmed payment date — not just a promise. "
            "You do not threaten, but your tone signals this is now being tracked. "
            "BANNED PHRASES — never use any of these: "
            "'hope this finds you well', 'please don't hesitate', 'feel free', "
            "'we appreciate your cooperation', 'as per', 'kindly', "
            "'please be advised', 'do not hesitate to reach out'. "
            "Cut all fluff. Every sentence must carry new information or a clear ask."
        ),
        "subject_pattern": "Payment follow-up – Invoice {invoice_no} (overdue)",
        "cta": "Please confirm the date you will process this payment.",
        "tone_label": "Polite but Firm",
        "max_words": 90,
    },
    3: {
        "role": (
            "You are a collections manager. This invoice is now over two weeks overdue "
            "and two reminders have already been sent. You are formal and serious. "
            "You mention that continued non-payment will affect the client's credit terms. "
            "You demand a response within 48 hours. "
            "BANNED PHRASES — never use any of these: "
            "'hope this finds you well', 'please don't hesitate', 'feel free', "
            "'we appreciate', 'as per', 'kindly', 'please be advised'. "
            "No pleasantries. No filler. Short paragraphs only. "
            "You MUST output all three sections: SUBJECT, TONE, and BODY."
        ),
        "subject_pattern": "IMPORTANT: Outstanding payment – Invoice {invoice_no} ({days_overdue} days overdue)",
        "cta": "Respond within 48 hours with payment confirmation or a resolution plan.",
        "tone_label": "Formal & Serious",
        "max_words": 100,
    },
    4: {
        "role": (
            "You are a finance manager issuing a final notice before escalation. "
            "This is the last automated communication before this account is reviewed "
            "by the finance and collections team. "
            "State clearly that if payment is not received within 24 hours, this matter "
            "will be escalated for further review and recovery action. "
            "Do NOT use aggressive legal threat language like 'legal team' or 'sued'. "
            "Keep the tone stern and factual — not hostile. "
            "BANNED PHRASES — never use: "
            "'hope this finds you well', 'please don't hesitate', 'feel free', "
            "'we appreciate', 'as per', 'kindly', 'please be advised', "
            "'urge you', 'settle this debt', 'immediate action'. "
            "Two short paragraphs in the BODY only. "
            "The CTA line is the only closing — do not add any sentence after the body. "
            "You MUST output all three sections: SUBJECT, TONE, and BODY."
        ),
        "subject_pattern": "FINAL NOTICE – Invoice {invoice_no} – Action required within 24 hours",
        "cta": "Pay immediately or contact us directly to avoid further escalation.",
        "tone_label": "Stern & Urgent",
        "max_words": 110,
    },
}


def _build_system_prompt(stage: int, invoice_data: dict) -> str:
    persona = STAGE_PERSONAS[stage]
    subject = persona["subject_pattern"].format(
        invoice_no=invoice_data["invoice_no"],
        days_overdue=invoice_data["days_overdue"],
    )
    salutation = _format_salutation(invoice_data["client_name"], stage)
    amount_fmt  = _format_currency(invoice_data["amount"])

    return f"""
{persona["role"]}

HARD RULES — violating any of these will make the output unusable:
- Maximum {persona["max_words"]} words in the email body. Count carefully.
- Do NOT use markdown (no **, no *, no #, no bullet points).
- Start the email body with exactly this salutation on its own line: {salutation},
- Display the payment amount as: {amount_fmt}
- Do NOT repeat the invoice details as a formatted list. Weave them into sentences.
- End with exactly this CTA on its own line: {persona["cta"]}
- Output ONLY the three-section format below — no preamble, no explanation.

OUTPUT FORMAT (exact — no deviations):

SUBJECT: {subject}

TONE: {persona["tone_label"]}

BODY:
<write the email body here, starting with: {salutation},>
""".strip()


def _build_user_prompt(invoice_data: dict) -> str:
    return (
        f"Client: {invoice_data['client_name']}\n"
        f"Invoice: {invoice_data['invoice_no']}\n"
        f"Amount due: {_format_currency(invoice_data['amount'])}\n"
        f"Due date: {invoice_data['due_date']}\n"
        f"Days overdue: {invoice_data['days_overdue']}\n"
        f"Payment link: {invoice_data['payment_link']}"
    )


def _parse_output(raw: str) -> dict | None:
    text = raw.strip()

    subject_match = re.search(
        r"SUBJECT\s*:\s*(.+?)(?=\n(?:TONE|BODY)\s*:)", text, re.IGNORECASE | re.DOTALL
    )
    tone_match = re.search(
        r"TONE\s*:\s*(.+?)(?=\nBODY\s*:)", text, re.IGNORECASE | re.DOTALL
    )
    body_match = re.search(
        r"BODY\s*:\s*(.+)$", text, re.IGNORECASE | re.DOTALL
    )

    if not (subject_match and body_match):
        return None

    subject = subject_match.group(1).strip()
    tone    = tone_match.group(1).strip() if tone_match else "Unknown"
    body    = body_match.group(1).strip()

    if len(body) < 30:
        return None
    if "SUBJECT" in body or "TONE" in body:
        return None

    return {"subject": subject, "tone": tone, "body": body}


def generate_email(invoice_data: dict) -> EmailResponse | None:
    raw_stage = invoice_data.get("escalation_stage", "")
    match = re.search(r"\d+", str(raw_stage))
    if not match:
        print(f"[generate_email] Could not parse stage number from: '{raw_stage}'")
        return None

    stage = int(match.group())
    if stage not in STAGE_PERSONAS:
        print(f"[generate_email] Stage {stage} has no persona defined.")
        return None

    system_prompt = _build_system_prompt(stage, invoice_data)
    user_prompt   = _build_user_prompt(invoice_data)

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        options={"temperature": 0.4, "top_p": 0.9},
    )

    raw_output = response["message"]["content"]

    print("\n" + "=" * 60)
    print(f"RAW OUTPUT — Stage {stage}")
    print("=" * 60)
    print(raw_output)
    print("=" * 60 + "\n")

    parsed = _parse_output(raw_output)
    if parsed is None:
        print(f"[generate_email] Parsing failed for stage {stage}.")
        return None

    return EmailResponse(
        subject=parsed["subject"],
        tone=parsed["tone"],
        body=parsed["body"],
    )
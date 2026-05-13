# 💰 Finance AI Agent Dashboard

An AI-powered finance operations dashboard built with Streamlit and Python to automate invoice escalation workflows, generate contextual payment reminder emails, and maintain audit logs.

The system simulates how modern finance teams handle overdue invoices using intelligent escalation logic and AI-generated communication workflows.

---

# 🚀 Project Overview

Managing overdue invoices manually is repetitive, error-prone, and difficult to scale. This project demonstrates how AI agents can assist finance operations teams by:

- Tracking overdue invoices
- Automatically determining escalation stages
- Generating professional reminder emails using an LLM
- Maintaining audit logs for compliance and traceability
- Providing a real-time operational dashboard

The application acts as a lightweight internal finance operations assistant.

---

# ✨ Features

- AI-generated invoice reminder emails
- Automated escalation stage detection
- Interactive Streamlit dashboard
- Search and filtering support
- Escalation analytics and charts
- CSV export functionality
- Audit logging system
- Mock email delivery workflow
- Modular Python architecture

---

# 🛠 Tech Stack

| Component | Technology |
|---|---|
| Frontend Dashboard | Streamlit |
| Backend Logic | Python |
| Data Processing | Pandas |
| AI Email Generation | OpenAI API |
| Logging | JSONL |
| Data Storage | CSV |

---

# 🧠 LLM & Framework Choice

## LLM Choice: OpenAI GPT Models

The OpenAI API was selected because:

- Strong natural language generation quality
- Reliable structured email generation
- Good contextual understanding
- Fast inference performance
- Simple Python SDK integration

The model is used to generate finance-friendly invoice reminder emails with escalation-aware tone adaptation.

Example:
- Stage 1 → Polite reminder
- Stage 3 → Firm payment notice
- Escalation → Legal/finance escalation language

---

## Framework Choice: Streamlit

Streamlit was chosen because:

- Rapid dashboard development
- Excellent support for data applications
- Native Python workflow
- Minimal frontend complexity
- Fast prototyping for AI/internal tools

This allows focus on AI workflow automation rather than frontend engineering overhead.

---

# 🏗 Agent Architecture

```text
                    +------------------+
                    |   invoices.csv   |
                    +------------------+
                              |
                              v
                  +----------------------+
                  |   Data Loader        |
                  |  (Pandas Processing) |
                  +----------------------+
                              |
                              v
                 +-----------------------+
                 | Escalation Engine     |
                 | determine_stage()     |
                 +-----------------------+
                              |
                              v
                +-------------------------+
                | Finance AI Agent        |
                | Email Generator (LLM)   |
                +-------------------------+
                              |
               +--------------+--------------+
               |                             |
               v                             v
     +------------------+         +------------------+
     | Mock Email Sender|         | Audit Logger     |
     +------------------+         +------------------+
               |                             |
               +--------------+--------------+
                              |
                              v
                 +-----------------------+
                 | Streamlit Dashboard   |
                 +-----------------------+
```

---

# 🔐 Security Mitigations

Although this is a portfolio/demo application, several security practices were considered.

## 1. Environment Variable Protection

API keys are stored using `.env` files instead of hardcoding secrets in source code.

Example:

```env
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is excluded using `.gitignore`.

---

## 2. Mock Email Sending

The project uses mock email delivery instead of real SMTP integration to prevent accidental email transmission during testing.

This avoids:
- Spam risks
- Accidental client communication
- Credential exposure

---

## 3. Input Validation

Invoice data is processed through structured Pandas workflows to reduce malformed data issues.

Datetime conversion is validated before overdue calculations.

---

## 4. Audit Logging

Actions are logged into JSONL audit files to maintain traceability of:
- Generated emails
- Escalation stages
- Delivery activity

This supports operational transparency.

---

## 5. Separation of Concerns

The project separates:
- business logic
- AI generation
- logging
- UI rendering
- configuration

This reduces security and maintenance risks caused by tightly coupled code.

---

# 📂 Project Structure

```text
finance-ai-agent/
│
├── app/
│   ├── config.py
│   ├── data_loader.py
│   ├── email_generator.py
│   ├── escalation_engine.py
│   ├── logger.py
│   └── sender.py
│
├── data/
│   └── invoices.csv
│
├── logs/
│   └── audit_log.jsonl
│
├── dashboard.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Setup Instructions

## 1. Clone Repository

```bash
git clone <your-repo-url>
```

Move into the project folder:

```bash
cd finance-ai-agent
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## 5. Run the Application

```bash
streamlit run dashboard.py
```

Open in browser:

```text
http://localhost:8501
```

---

# 📊 Dashboard Features

## Invoice Monitoring
- Track overdue invoices
- Monitor escalation stages
- Identify critical finance cases

## AI Email Generation
- Generate contextual reminder emails
- Escalation-aware tone generation
- Mock delivery simulation

## Analytics
- Escalation distribution charts
- Invoice metrics
- Search and filtering

## Audit Logs
- Track generated communications
- Store delivery activity
- Maintain operational history

---

# 📸 Screenshots

Add screenshots after deployment.

Example:

```markdown
![Dashboard Screenshot](screenshots/dashboard.png)
```

---

# 🔮 Future Improvements

- Real email delivery integration
- ML-based payment risk prediction
- Database integration
- Multi-user authentication
- Docker deployment
- Role-based access control
- Payment history analytics

---

# 🧠 Learning Outcomes

This project demonstrates:

- AI-powered workflow automation
- Streamlit dashboard engineering
- LLM integration in business systems
- Data processing with Pandas
- Modular backend architecture
- Logging and audit systems
- Internal tool development

---

# 📜 License

This project is intended for educational and portfolio purposes.

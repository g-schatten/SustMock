# QueueStorm Warmup — CRM Ticket Classifier

A small FastAPI service that classifies customer support tickets by case type, severity, department, and generates a one-line agent summary. Built for the **SUST CSE Carnival 2026 — Mock Preliminary Round**.

## Features

- `GET /health` — service health check
- `POST /sort-ticket` — classify a single CRM ticket (rule-based, no LLM)

## Quick start (local)

### Prerequisites

- Python 3.11+

### Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify

```bash
curl http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/sort-ticket \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\":\"T-001\",\"channel\":\"app\",\"locale\":\"en\",\"message\":\"I sent 5000 taka to a wrong number this morning, please help me get it back\"}"
```

Interactive API docs: `http://localhost:8000/docs`

## API

### `POST /sort-ticket`

**Request**

```json
{
  "ticket_id": "T-001",
  "channel": "app",
  "locale": "en",
  "message": "I sent 5000 taka to a wrong number this morning, please help me get it back"
}
```

**Response**

```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending 5000 BDT to a wrong recipient and requests recovery.",
  "human_review_required": false,
  "confidence": 0.85
}
```

### Classification rules

| case_type | Typical triggers |
|-----------|------------------|
| `wrong_transfer` | wrong number/account/recipient |
| `payment_failed` | failed payment, balance deducted |
| `refund_request` | refund, money back, changed my mind |
| `phishing_or_social_engineering` | OTP, PIN, password, scam calls |
| `other` | general app/service issues |

`human_review_required` is `true` for **critical** severity or **phishing** cases.

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Deploy to Render

1. Push this repository to a **public** GitHub repo.
2. Sign in at [render.com](https://render.com).
3. **New → Blueprint** and connect the repo (uses `render.yaml`), **or** create a **Web Service** manually:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health check path:** `/health`
4. After deploy, your live base URL will look like `https://queuestorm-ticket-sorter.onrender.com`.

## Deploy to Railway

1. Push to GitHub.
2. Create a new project on [railway.app](https://railway.app) from the repo.
3. Railway auto-detects Python; set start command if needed:

   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. Enable a public HTTPS domain from the service settings.

## Submission checklist

| Field | Value |
|-------|-------|
| Team name | *(your registered team name)* |
| GitHub repository URL | *(public repo link)* |
| Live API base URL | `https://<your-host>/health` must respond |
| Deployment platform | Render / Railway / Fly / etc. |
| LLM used | **No** — rule-based classifier |

## Project structure

```
.
├── app/
│   ├── classifier.py   # Rule-based ticket classification
│   └── main.py         # FastAPI application
├── tests/
│   └── test_classifier.py
├── requirements.txt
├── Procfile
├── render.yaml
└── README.md
```

## License

MIT
# SustMock
# SustMock
# SustMock

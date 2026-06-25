# SustMock

CRM ticket classifier for the SUST CSE Carnival 2026 mock preliminary.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/sort-ticket \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\":\"T-001\",\"channel\":\"app\",\"locale\":\"en\",\"message\":\"I sent 5000 taka to a wrong number this morning, please help me get it back\"}"
```

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Deploy (Render)

1. Connect this repo as a **Web Service**.
2. Set **PYTHON_VERSION** to `3.12.8`.
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Health check path: `/health`

Or use **New → Blueprint** with the included `render.yaml`.

## API

### `POST /sort-ticket`

Request:

```json
{
  "ticket_id": "T-001",
  "channel": "app",
  "locale": "en",
  "message": "I sent 5000 taka to a wrong number this morning, please help me get it back"
}
```

Response:

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

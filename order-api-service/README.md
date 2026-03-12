# Order Management Service

A sample FastAPI microservice that manages orders and records request-performance logs to `logs.json`.  
The log file is used as the input dataset for the **API Log Performance Analyzer**.

---

## Requirements

| Tool | Version |
|---|---|
| Python | 3.9 or higher |
| pip | latest |

### Python packages

```
fastapi
uvicorn
```

---

## Project Structure

```
order-api-service/
├── app.py          # FastAPI application
├── logs.json       # Auto-generated request log file (created on first request)
├── venv/           # Python virtual environment
└── README.md
```

---

## Installation

### 1. Create and activate a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn
```

---

## Running the Service

```bash
uvicorn app:app --reload --port 8000
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/orders` | Return all orders |
| `GET` | `/orders/{id}` | Return a single order by ID |
| `POST` | `/orders` | Create a new order |
| `DELETE` | `/orders/{id}` | Delete an order |

### Example – Create an order

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Rahul",
    "product_name": "Laptop",
    "quantity": 1,
    "price": 75000,
    "order_date": "2026-03-05"
  }'
```

---

## Request Logging

Every API call is automatically logged to `logs.json` with the following fields:

```json
{
  "endpoint": "/orders",
  "response_time": 1450,
  "status_code": 200,
  "timestamp": "2026-03-05T10:22:31"
}
```

> Make several API calls to populate `logs.json` before running the **API Log Performance Analyzer**.

---

## Simulated Latency

Each endpoint introduces a random delay of **100 ms – 2000 ms** to simulate realistic slow APIs.

---

## Next Step

Once `logs.json` is populated, proceed to the **API Log Performance Analyzer**:

```
../api-log-analyzer/
```

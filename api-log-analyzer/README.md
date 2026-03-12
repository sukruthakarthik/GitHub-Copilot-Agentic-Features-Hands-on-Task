# API Log Performance Analyzer

A FastAPI service that reads API request logs from `logs.json` and exposes endpoints to identify slow APIs, calculate average response times, detect high error rates, and export reports.  
Includes real-time **Prometheus metrics** integration.

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
prometheus-fastapi-instrumentator
```

> **Prerequisite:** Complete the **Order Management Service** exercise first and copy its `logs.json` into this folder.

---

## Project Structure

```
api-log-analyzer/
├── app.py                            # FastAPI analyzer application
├── logs.json                         # Input log file (copied from order-api-service)
├── skills.md                         # Copilot Skills definitions
├── agent.md                          # Custom Copilot Agent definition
├── .github/
│   └── copilot-instructions.md       # Copilot coding standards
├── venv/                             # Python virtual environment
└── README.md
```

---

## Installation

### 1. Copy logs.json from the Order Management Service

**Windows**
```bash
copy ..\order-api-service\logs.json logs.json
```

**macOS / Linux**
```bash
cp ../order-api-service/logs.json logs.json
```

### 2. Create and activate a virtual environment

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

### 3. Install dependencies

```bash
pip install fastapi uvicorn prometheus-fastapi-instrumentator
```

---

## Running the Analyzer

```bash
uvicorn app:app --reload --port 8001
```

The API will be available at:

```
http://127.0.0.1:8001
```

Interactive Swagger UI:

```
http://127.0.0.1:8001/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/slow-endpoints` | Top 5 slowest individual API requests |
| `GET` | `/average-response` | Average response time per endpoint |
| `GET` | `/error-rate` | Endpoints with HTTP error rate > 5% |
| `GET` | `/dashboard` | Combined summary of all metrics |
| `GET` | `/report/csv` | Download a CSV report of all log entries sorted by response time |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint |

### Example requests (curl)

```bash
# Top 5 slowest endpoints
curl http://127.0.0.1:8001/slow-endpoints

# Average response time per endpoint
curl http://127.0.0.1:8001/average-response

# Endpoints with error rate > 5%
curl http://127.0.0.1:8001/error-rate

# Full dashboard summary
curl http://127.0.0.1:8001/dashboard

# Download CSV report
curl -o slow-api-report.csv http://127.0.0.1:8001/report/csv

# Prometheus metrics
curl http://127.0.0.1:8001/metrics
```

---

## Prometheus Integration

The `/metrics` endpoint is automatically exposed by `prometheus-fastapi-instrumentator`.  
It provides the following metrics out of the box:

| Metric | Type | Description |
|---|---|---|
| `http_requests_total` | Counter | Total requests by method, handler, and status code |
| `http_request_duration_seconds` | Histogram | Latency distribution per endpoint |
| `python_gc_objects_collected_total` | Counter | Python garbage collector stats |
| `python_info` | Gauge | Python runtime version info |

### Setting up a local Prometheus server

#### 1. Download Prometheus

```
https://prometheus.io/download/
```

Extract the archive and navigate to the folder.

#### 2. Create a `prometheus.yml` scrape config

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "api-log-analyzer"
    static_configs:
      - targets: ["127.0.0.1:8001"]
```

Save this file as `prometheus.yml` in the Prometheus folder.

#### 3. Start Prometheus

**Windows**
```bash
prometheus.exe --config.file=prometheus.yml
```

**macOS / Linux**
```bash
./prometheus --config.file=prometheus.yml
```

#### 4. Open the Prometheus UI

```
http://localhost:9090
```

Useful queries in the Prometheus expression browser:

```promql
# Total requests per endpoint
http_requests_total{job="api-log-analyzer"}

# 95th-percentile response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Request rate per second
rate(http_requests_total[1m])

# Error rate (4xx + 5xx)
rate(http_requests_total{status=~"4..|5.."}[5m])
```

#### 5. (Optional) Visualize with Grafana

1. Download Grafana: `https://grafana.com/grafana/download`
2. Start Grafana and open `http://localhost:3000` (default login: `admin` / `admin`)
3. Add Prometheus as a data source: `http://localhost:9090`
4. Import dashboard ID **11074** (FastAPI Observability) from the Grafana marketplace.

---

## Running Both Services Together

Open two terminal windows:

**Terminal 1 – Order Management Service (port 8000)**
```bash
cd order-api-service
venv\Scripts\activate        # Windows
uvicorn app:app --reload --port 8000
```

**Terminal 2 – API Log Performance Analyzer (port 8001)**
```bash
cd api-log-analyzer
venv\Scripts\activate        # Windows
uvicorn app:app --reload --port 8001
```

**Terminal 3 – Prometheus**
```bash
cd prometheus-folder
prometheus.exe --config.file=prometheus.yml
```

"""
API Log Performance Analyzer
Reads API logs from logs.json and exposes performance analysis endpoints.
"""

import csv
import io
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from prometheus_fastapi_instrumentator import Instrumentator

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger("api-log-analyzer")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="API Log Performance Analyzer",
    description=(
        "Analyzes API request logs to identify slow endpoints, "
        "calculate average response times, and detect high error rates."
    ),
    version="1.0.0",
)

LOGS_FILE = Path(__file__).parent / "logs.json"

# ---------------------------------------------------------------------------
# Prometheus metrics – exposes /metrics endpoint automatically
# ---------------------------------------------------------------------------
Instrumentator().instrument(app).expose(app)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def load_logs() -> List[Dict]:
    """Load and return all log entries from logs.json.

    Returns:
        A list of log entry dicts, each containing:
        endpoint, response_time, status_code, timestamp.

    Raises:
        HTTPException: 500 if the file cannot be read or parsed.
    """
    if not LOGS_FILE.exists():
        logger.error("logs.json not found at %s", LOGS_FILE)
        raise HTTPException(status_code=500, detail="logs.json file not found.")
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
        logger.info("Loaded %d log entries from %s", len(logs), LOGS_FILE)
        return logs
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse logs.json: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to parse logs.json: {exc}") from exc


def group_by_endpoint(logs: List[Dict]) -> Dict[str, List[Dict]]:
    """Group log entries by their endpoint path.

    Args:
        logs: List of raw log entry dicts.

    Returns:
        A dict mapping endpoint path → list of log entries.
    """
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for entry in logs:
        endpoint = entry.get("endpoint", "unknown")
        grouped[endpoint].append(entry)
    return dict(grouped)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/slow-endpoints",
    summary="Top 5 slowest endpoints",
    response_description="List of the 5 endpoints with the highest single-request response times",
)
def slow_endpoints():
    """Return the top 5 slowest individual API calls from the logs.

    Each result includes the endpoint path, response time (ms),
    status code, and timestamp of the slow request.
    """
    logs = load_logs()

    # Sort all entries by response_time descending and take the top 5
    sorted_logs = sorted(logs, key=lambda e: e.get("response_time", 0), reverse=True)
    top5 = sorted_logs[:5]

    logger.info("Returning top %d slow endpoint entries", len(top5))
    return {
        "slow_endpoints": [
            {
                "endpoint": e.get("endpoint"),
                "response_time_ms": e.get("response_time"),
                "status_code": e.get("status_code"),
                "timestamp": e.get("timestamp"),
            }
            for e in top5
        ]
    }


@app.get(
    "/average-response",
    summary="Average response time per endpoint",
    response_description="Map of endpoint path to its average response time in milliseconds",
)
def average_response():
    """Calculate and return the average response time for each unique endpoint.

    Results are sorted by average response time in descending order so the
    slowest endpoints appear first.
    """
    logs = load_logs()
    grouped = group_by_endpoint(logs)

    result = {}
    for endpoint, entries in grouped.items():
        times = [e.get("response_time", 0) for e in entries]
        avg = round(sum(times) / len(times), 2) if times else 0.0
        result[endpoint] = {
            "average_response_time_ms": avg,
            "request_count": len(entries),
        }

    # Sort by average descending
    sorted_result = dict(
        sorted(result.items(), key=lambda kv: kv[1]["average_response_time_ms"], reverse=True)
    )

    logger.info("Computed average response times for %d endpoints", len(sorted_result))
    return {"average_response_per_endpoint": sorted_result}


@app.get(
    "/error-rate",
    summary="Endpoints with error rate > 5%",
    response_description="Endpoints whose HTTP 4xx/5xx rate exceeds 5%",
)
def error_rate():
    """Return endpoints where the HTTP error rate (4xx + 5xx) is greater than 5%.

    Useful for identifying unreliable APIs that need investigation.
    """
    logs = load_logs()
    grouped = group_by_endpoint(logs)

    high_error_endpoints = {}
    for endpoint, entries in grouped.items():
        total = len(entries)
        errors = sum(1 for e in entries if e.get("status_code", 200) >= 400)
        rate = round((errors / total) * 100, 2) if total > 0 else 0.0
        if rate > 5.0:
            high_error_endpoints[endpoint] = {
                "error_rate_percent": rate,
                "total_requests": total,
                "error_requests": errors,
            }

    high_error_endpoints = dict(
        sorted(
            high_error_endpoints.items(),
            key=lambda kv: kv[1]["error_rate_percent"],
            reverse=True,
        )
    )

    logger.info(
        "Found %d endpoint(s) with error rate > 5%%", len(high_error_endpoints)
    )
    return {
        "high_error_rate_endpoints": high_error_endpoints,
        "threshold_percent": 5.0,
    }


@app.get(
    "/report/csv",
    summary="Download CSV report of slow APIs",
    response_description="A downloadable CSV file listing all log entries sorted by response time (slowest first)",
)
def report_csv():
    """Generate and stream a CSV report of all API log entries sorted by response time.

    The CSV includes: endpoint, response_time_ms, status_code, timestamp.
    The file can be downloaded directly from a browser or curl.
    """
    logs = load_logs()
    sorted_logs = sorted(logs, key=lambda e: e.get("response_time", 0), reverse=True)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["endpoint", "response_time_ms", "status_code", "timestamp"],
        lineterminator="\n",
    )
    writer.writeheader()
    for entry in sorted_logs:
        writer.writerow(
            {
                "endpoint": entry.get("endpoint", ""),
                "response_time_ms": entry.get("response_time", ""),
                "status_code": entry.get("status_code", ""),
                "timestamp": entry.get("timestamp", ""),
            }
        )

    output.seek(0)
    logger.info("Streaming CSV report with %d rows", len(sorted_logs))
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=slow-api-report.csv"},
    )


@app.get(
    "/dashboard",
    summary="Combined performance dashboard",
    response_description="Summary of slow endpoints, average response times, and error rates",
)
def dashboard():
    """Return a combined summary of all performance metrics in a single response.

    Aggregates data from /slow-endpoints, /average-response, and /error-rate.
    """
    logs = load_logs()
    grouped = group_by_endpoint(logs)

    # --- slow endpoints (top 5) ---
    sorted_logs = sorted(logs, key=lambda e: e.get("response_time", 0), reverse=True)
    top5 = [
        {
            "endpoint": e.get("endpoint"),
            "response_time_ms": e.get("response_time"),
            "status_code": e.get("status_code"),
            "timestamp": e.get("timestamp"),
        }
        for e in sorted_logs[:5]
    ]

    # --- averages ---
    averages = {}
    for endpoint, entries in grouped.items():
        times = [e.get("response_time", 0) for e in entries]
        averages[endpoint] = {
            "average_response_time_ms": round(sum(times) / len(times), 2) if times else 0.0,
            "request_count": len(entries),
        }

    # --- error rates ---
    error_rates = {}
    for endpoint, entries in grouped.items():
        total = len(entries)
        errors = sum(1 for e in entries if e.get("status_code", 200) >= 400)
        rate = round((errors / total) * 100, 2) if total > 0 else 0.0
        if rate > 5.0:
            error_rates[endpoint] = {
                "error_rate_percent": rate,
                "total_requests": total,
                "error_requests": errors,
            }

    logger.info("Dashboard summary generated for %d log entries", len(logs))
    return {
        "total_log_entries": len(logs),
        "slow_endpoints_top5": top5,
        "average_response_per_endpoint": averages,
        "high_error_rate_endpoints": error_rates,
    }

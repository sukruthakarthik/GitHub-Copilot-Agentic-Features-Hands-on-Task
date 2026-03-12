"""
Order Management Service API
A FastAPI application that manages orders and logs request performance.
"""

import json
import random
import time
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Order Management Service",
    description="A sample microservice API for managing orders with performance logging.",
    version="1.0.0",
)

# Path to the JSON log file
LOGS_FILE = Path(__file__).parent / "logs.json"


# ---------------------------------------------------------------------------
# Logging middleware
# ---------------------------------------------------------------------------

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs endpoint, response_time, status_code, and timestamp
    for every request to logs.json."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()
        response = await call_next(request)
        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        log_entry = {
            "endpoint": request.url.path,
            "response_time": elapsed_ms,
            "status_code": response.status_code,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        }

        # Load existing logs (or start fresh) and append the new entry
        if LOGS_FILE.exists():
            try:
                with open(LOGS_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, ValueError):
                logs = []
        else:
            logs = []

        logs.append(log_entry)

        with open(LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

        return response


app.add_middleware(RequestLoggingMiddleware)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class OrderCreate(BaseModel):
    """Request body for creating a new order."""
    customer_name: str
    product_name: str
    quantity: int
    price: float
    order_date: date


class Order(OrderCreate):
    """Full order object returned by the API (includes generated id)."""
    id: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "customer_name": "Rahul",
                "product_name": "Laptop",
                "quantity": 1,
                "price": 75000.0,
                "order_date": "2026-03-05",
            }
        }


# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------

# Pre-populate with a few sample orders so GET /orders returns something
_orders: List[Order] = [
    Order(
        id=str(uuid.uuid4()),
        customer_name="Alice",
        product_name="Smartphone",
        quantity=2,
        price=30000.0,
        order_date=date(2026, 3, 1),
    ),
    Order(
        id=str(uuid.uuid4()),
        customer_name="Bob",
        product_name="Headphones",
        quantity=1,
        price=5000.0,
        order_date=date(2026, 3, 3),
    ),
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _simulate_delay():
    """Introduce a random delay between 100 ms and 2000 ms to mimic slow APIs."""
    delay_seconds = random.randint(100, 2000) / 1000
    time.sleep(delay_seconds)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/orders", response_model=List[Order], summary="Get all orders")
def get_orders():
    """Return the list of all orders."""
    _simulate_delay()
    return _orders


@app.get("/orders/{order_id}", response_model=Order, summary="Get order by ID")
def get_order(order_id: str):
    """Return a single order identified by its *order_id*."""
    _simulate_delay()
    for order in _orders:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")


@app.post("/orders", response_model=Order, status_code=201, summary="Create a new order")
def create_order(order_data: OrderCreate):
    """Create a new order and return it with a generated ID."""
    _simulate_delay()
    new_order = Order(id=str(uuid.uuid4()), **order_data.model_dump())
    _orders.append(new_order)
    return new_order


@app.delete("/orders/{order_id}", status_code=204, summary="Delete an order")
def delete_order(order_id: str):
    """Delete the order identified by *order_id*. Returns 204 on success."""
    _simulate_delay()
    for index, order in enumerate(_orders):
        if order.id == order_id:
            _orders.pop(index)
            return  # 204 No Content
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")

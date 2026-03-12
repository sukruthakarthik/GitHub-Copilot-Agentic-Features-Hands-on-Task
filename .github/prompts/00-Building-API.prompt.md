# GitHub Copilot Hands-on Exercise

## Building an API and Generating Logs for Performance Analysis

### Objective

In this exercise, participants will build a **sample microservice API** that generates request logs.
These logs will later be used in the **API Log Performance Analyzer** exercise.

Participants will use **GitHub Copilot prompts, instructions, and agent capabilities** to generate the application quickly.

Estimated time: **15–20 minutes**

---

# Scenario

Your organization runs multiple microservices. The platform engineering team wants to identify **slow APIs and performance bottlenecks** across services.

Before building the **API Log Performance Analyzer**, you must first create a **sample Order Management API** that produces request logs.

These logs will later be analyzed by an AI-based tool.

---

# Prerequisites

Make sure the following are installed:

* Visual Studio Code
* Python (version 3.9 or higher)
* Git
* GitHub Copilot
* GitHub Copilot Chat

Verify installation:

```bash
python --version
git --version
```

---

# Step 1 – Create a Project

Create a new project folder.

```bash
mkdir order-api-service
cd order-api-service
code .
```

Create and activate a Python virtual environment.

```bash
python -m venv venv
```

Activate environment:

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install fastapi uvicorn
```

---

# Step 2 – Generate the API Using Copilot

Create a file called:

```
app.py
```

Use **Copilot Chat** and paste the following prompt.

### Copilot Prompt

```
Create a FastAPI application for an Order Management Service.

Requirements:

1. Create the following APIs:
   - GET /orders → return all orders
   - GET /orders/{id} → return order by id
   - POST /orders → create a new order
   - DELETE /orders/{id} → delete an order

2. Order object should contain:
   - id
   - customer_name
   - product_name
   - quantity
   - price
   - order_date

3. Add logging middleware that logs the following details for each request:
   - endpoint
   - response_time
   - status_code
   - timestamp

4. Save logs in a JSON file called logs.json.

5. Introduce simulated delays (100ms–2000ms) to mimic slow APIs.

6. Use clean code and add comments.
```

Allow Copilot to generate the application.

---

# Step 3 – Run the API

Start the server.

```bash
uvicorn app:app --reload
```

The API will run at:

```
http://127.0.0.1:8000
```

Open the Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# Step 4 – Test the APIs

Call the endpoints from Swagger UI.

Example APIs:

```
GET /orders
POST /orders
GET /orders/{id}
DELETE /orders/{id}
```

Example Order Request

```json
{
  "customer_name": "Rahul",
  "product_name": "Laptop",
  "quantity": 1,
  "price": 75000,
  "order_date": "2026-03-05"
}
```

---

# Step 5 – Verify Logs

Each API call should generate a log entry in:

```
logs.json
```

Example log entry:

```json
{
  "endpoint": "/orders",
  "response_time": 1450,
  "status_code": 200,
  "timestamp": "2026-03-05T10:22:31"
}
```

Make multiple API calls to generate **several log entries**.

---

# Outcome

By the end of this exercise you should have:

* A working **Order Management API**
* REST endpoints for CRUD operations
* Logging middleware that captures API performance
* A **logs.json** file containing API logs

---

# Next Exercise

➡️ Once you have completed this exercise and have a populated `logs.json` file, proceed to the next hands-on lab:

**[GitHub Copilot Agentic Features – Hands-on Lab](README.md)**

In that lab, you will build an **API Log Performance Analyzer** that will:

* Identify slow endpoints
* Calculate average response time
* Detect high error rate APIs
* Recommend performance improvements using AI agents

The `logs.json` file generated in this exercise will serve as the **input dataset** for the analyzer.

---

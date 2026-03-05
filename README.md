# GitHub Copilot Agentic Features – Hands-on Lab

## Objective

Build a small **API Log Performance Analyzer** using GitHub Copilot by leveraging:

* Copilot Instructions
* Copilot Prompts
* Copilot Skills
* Custom Agent

Estimated time: **15–20 minutes**

---

## Prerequisites

Before starting this lab, make sure you have completed the following:

* ✅ **Exercise 00 – Build the Order Management API** (`00-Exercies.md`)
  This exercise produces the `logs.json` file that you will use in this lab.
  _(File name `00-Exercies.md` contains a typo and is kept as-is for backward compatibility.)_
* Visual Studio Code installed
* Python (version 3.9 or higher) installed
* GitHub Copilot and GitHub Copilot Chat enabled in VS Code
* The `order-api-service` project from Exercise 00 with a populated `logs.json`

> ⚠️ **Do not proceed with this lab until you have completed Exercise 00 and have a `logs.json` file with API logs.**

---

## Scenario

Your organization runs several microservices. The platform team has collected API request logs from the Order Management Service you built in Exercise 00.

Your goal is to quickly build a **tool that analyzes those API logs and identifies slow endpoints**.

The logs you generated contain the following fields:

* `endpoint`
* `response_time`
* `status_code`
* `timestamp`

Example log entry:

```json
[
  {
    "endpoint": "/orders",
    "response_time": 1800,
    "status_code": 200,
    "timestamp": "2026-01-10T10:22:31"
  },
  {
    "endpoint": "/products",
    "response_time": 1200,
    "status_code": 500,
    "timestamp": "2026-01-10T10:22:35"
  }
]
```

---

## Step 1 – Set Up the Project

Create a new project folder for the analyzer.

```bash
mkdir api-log-analyzer
cd api-log-analyzer
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

Copy the `logs.json` file from your `order-api-service` project into this folder.

---

## Step 2 – Configure Copilot Instructions

Create the following file in your project:

```
.github/copilot-instructions.md
```

Add the following instructions:

```
You are an expert backend engineer.

Follow these standards:
- Use Python FastAPI
- Follow modular coding practices
- Add logging and error handling
- Write reusable functions
- Add docstrings
- Generate pytest unit tests
```

This ensures Copilot generates **consistent and structured code** throughout this exercise.

---

## Step 3 – Generate the Analyzer Application Using Copilot

Create a file called:

```
app.py
```

Open **Copilot Chat** and paste the following prompt:

```
Create a FastAPI service that reads API logs from a JSON file called logs.json.

Each log contains:
endpoint
response_time
status_code
timestamp

The API should provide the following endpoints:

1. /slow-endpoints
   Return the top 5 slowest endpoints.

2. /average-response
   Return average response time per endpoint.

3. /error-rate
   Return endpoints where error rate is greater than 5%.

Use clean architecture and add logging.
```

Allow Copilot to generate the application and save the output to `app.py`.

---

## Step 4 – Run the Application

Start the server.

```bash
uvicorn app:app --reload
```

The API will run at:

```
http://127.0.0.1:8000
```

Open the Swagger UI to explore the endpoints:

```
http://127.0.0.1:8000/docs
```

Test each endpoint:

```
GET /slow-endpoints
GET /average-response
GET /error-rate
```

Verify that the responses reflect the log data from your `logs.json` file.

---

## Step 5 – Define Copilot Skills

Create a file called:

```
skills.md
```

Define the following skills:

### Skill 1 – Log Analyzer

```
Skill: Analyze API logs

Input:
JSON API logs

Output:
- Top slow endpoints
- Average response time per endpoint
- Error rate
```

### Skill 2 – Performance Recommendation

```
Skill: API Performance Advisor

Analyze slow APIs and suggest optimizations.

Recommendations should include:
- caching
- async processing
- database optimization
- indexing strategies
```

Open **Copilot Chat** and ask it to **apply these skills to your generated `app.py`**.

---

## Step 6 – Create a Custom Agent

Create a file:

```
agent.md
```

Define a **Performance Engineer Agent** with the following content:

```
Agent Name: API Performance Engineer

Responsibilities:
- Analyze API logs
- Identify slow endpoints
- Suggest performance improvements
- Recommend monitoring metrics
```

In **Copilot Chat**, ask the agent:

```
Analyze the API logs and provide:

1. Top slow endpoints
2. Possible bottlenecks
3. Performance improvements
4. Metrics that should be monitored
```

Review the agent's recommendations and apply any code improvements it suggests.

---

## Outcome

By the end of this lab you should have:

* ✅ A working **API Log Performance Analyzer** built with FastAPI
* ✅ Three analysis endpoints (`/slow-endpoints`, `/average-response`, `/error-rate`)
* ✅ Copilot instructions configured in `.github/copilot-instructions.md`
* ✅ Copilot skills defined in `skills.md`
* ✅ A custom agent defined in `agent.md` with performance recommendations

---

## Bonus Challenge (Optional)

Ask Copilot to extend the application with:

* A `/dashboard` endpoint that returns a summary of all metrics
* A `/report/csv` endpoint that downloads a CSV report of slow APIs
* Prometheus metrics integration for real-time monitoring

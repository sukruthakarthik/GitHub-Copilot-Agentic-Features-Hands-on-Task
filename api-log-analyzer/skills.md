# Copilot Skills – API Log Performance Analyzer

---

## Skill 1 – Log Analyzer

```
Skill: Analyze API logs

Input:
JSON API logs

Output:
- Top slow endpoints
- Average response time per endpoint
- Error rate
```

### How to apply this skill

When asked to analyze API logs, Copilot should:

1. Read all entries from `logs.json`.
2. Identify the **top 5 slowest requests** sorted by `response_time` descending.
3. Compute the **average response time** per unique `endpoint`.
4. Calculate the **HTTP error rate** (4xx + 5xx responses) per endpoint and flag any endpoint whose rate exceeds 5%.
5. Return structured JSON responses from the relevant FastAPI endpoints:
   - `GET /slow-endpoints`
   - `GET /average-response`
   - `GET /error-rate`

---

## Skill 2 – Performance Recommendation

```
Skill: API Performance Advisor

Analyze slow APIs and suggest optimizations.

Recommendations should include:
- caching
- async processing
- database optimization
- indexing strategies
```

### How to apply this skill

When asked for performance recommendations, Copilot should analyze the output of the Log Analyzer skill and provide actionable suggestions:

| Issue detected | Recommended improvement |
|---|---|
| High average response time (> 1000 ms) | Add response caching (e.g., Redis, in-memory LRU cache) |
| Endpoints with large dataset queries | Introduce pagination and database indexing |
| Synchronous blocking calls | Refactor to `async def` handlers and use `asyncio`-compatible libraries |
| High error rate (> 5%) | Add request validation, retry logic, and circuit breakers |
| No observability | Integrate Prometheus metrics (`/metrics`) and structured logging |
| Repeated expensive queries | Use background task queues (e.g., Celery, ARQ) for heavy operations |

Apply these recommendations as concrete code improvements in `app.py`.

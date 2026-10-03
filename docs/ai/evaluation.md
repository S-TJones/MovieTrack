# AI Search Evaluation

## AI integration approach

The AI path is intentionally narrow and follows a strict control flow:

1. User enters a natural-language query in the React UI.
2. The frontend calls the Flask API at `POST /api/ai/search`.
3. Flask uses a dedicated `LLMClient` in `backend/app/ai/client.py` to call the configured provider.
4. The provider response is parsed as JSON and validated by `AIService` against `backend/app/ai/schemas.py`.
5. If validation or provider execution fails, the app falls back to standard TMDB keyword/title search instead of executing unsafe database logic.
6. Only validated filters are used to resolve TMDB genre/person/keyword IDs and return results to the UI.

This separation is deliberate: the LLM interprets the user request; the application performs the actual data access.

## Method

The evaluation uses deterministic structured responses injected at the LLM-client boundary. It exercises application validation and prompt/data separation without calling a paid provider or relying on model nondeterminism.

Run from `backend/`:

```powershell
python -m pytest tests/test_ai_evaluation.py -q
```

## Cases and results

| ID | Input focus | Expected behavior | Result |
| --- | --- | --- | --- |
| 1 | Action/comedy, year 2020, Tom Cruise | Accept genres, lower year bound, and cast | PASS |
| 2 | Christopher Nolan after 2010 | Accept director and year bound | PASS |
| 3 | Ambiguous request | Accept empty filters instead of inventing criteria | PASS |
| 4 | 1990 through 1999 | Accept bounded year range and genre | PASS |
| 5 | Animated family/toys | Accept multiple genres and keyword | PASS |
| 6 | Prompt-injection text in query | Keep query in user data, separate from system prompt | PASS |
| 7 | Unsupported intent | Reject response | PASS |
| 8 | Extra SQL field | Reject response | PASS |
| 9 | Model-invented TMDB ID | Reject response | PASS |
| 10 | Boolean as year | Reject response | PASS |
| 11 | Year outside supported range | Reject response | PASS |
| 12 | Reversed year range | Reject response | PASS |

Latest recorded run: **12 passed**. The full backend suite also passed with the AI evaluation included.

## Results summary

- 12/12 deterministic evaluation cases passed.
- Rejected cases included malformed schema output, unsupported intents, SQL-like keys, invented TMDB metadata, invalid year values, and reversed year ranges.
- The system remains usable when AI support is unavailable because it gracefully falls back to standard search.

## Limits

These tests establish schema and application-behavior guarantees; they do not measure a live model's semantic accuracy. A live-provider evaluation should be run with a configured `LLM_API_KEY`, record the provider/model/date, compare parsed fields to these expectations, and retain failed outputs without storing secrets or unnecessary personal data.

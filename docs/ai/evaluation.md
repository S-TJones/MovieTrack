# AI Search Evaluation

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

## Limits

These tests establish schema and application-behavior guarantees; they do not measure a live model's semantic accuracy. A live-provider evaluation should be run with a configured `LLM_API_KEY`, record the provider/model/date, compare parsed fields to these expectations, and retain failed outputs without storing secrets or unnecessary personal data.

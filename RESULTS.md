# API lab results

## Part 0
- Step 0.1, the number of pizza names: 18
- Step 0.3, status code of the request without a token: 401
- Step 0.4, the name of your pizza: A Deep Americana
- Step 0.12, results of the three runs without a session (optional): Run 1: FAILED (assert 401 == 200), Run 2: PASSED, Run 3: FAILED (assert 401 == 200)
- Step 0.16, blocks of "how many of the three tools are excluded": 0 tools, 1 tool, 2 tools, 3 tools

## Defect report
- Title: Excluding all three cutting tools in POST /api/pizza returns 500 Internal Server Error with an empty body instead of 400 Bad Request
- Request: `POST https://quickpizza.grafana.com/api/pizza` with header `Authorization: token <valid_token>` and JSON body `{"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}`
- Expected result: HTTP status `400 Bad Request` with a JSON error message (e.g., `{"error": "..."}`) explaining that no pizza can satisfy the request because all tools are excluded.
- Actual result: HTTP status `500 Internal Server Error` with an empty response body (`Content-Length: 0`).
- Severity: Medium (High for API consumers expecting structured JSON errors, as an unhandled server error with an empty body causes JSON parsing crashes in client applications, though it only occurs when a user excludes every available tool).

## Part A
- Step A4, status codes when the other user reads, changes and deletes:

## Part B
1.
2.
3.
4.
5.
6.
7.
8.

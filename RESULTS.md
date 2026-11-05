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
- Step A4, status codes when the other user reads, changes and deletes: GET (read) = 404 Not Found (`{"error": "not found"}`), PUT (change) = 400 Bad Request (`{"error": "rating ID <id> not found"}`), DELETE (delete) = 400 Bad Request (`{"error": "rating ID <id> not found"}`)

## Part B
1. **Two kinds of failure that API tests find but unit tests with stubs cannot:**
   - **Integration and contract mismatches between components:** Real API tests verify that the HTTP router, request/JSON serialization (e.g., Go struct unmarshaling rules), authentication middleware, and actual database queries work together properly. A unit test with stubs replaces neighboring components (like the database or HTTP layer) with hardcoded assumptions that may not match real behavior.
   - **Infrastructure, deployment, and environment issues:** Real API tests over the internet can catch issues caused by load balancers, sticky-session cookies (`AWSALB`), network routing, server configuration, or unhandled runtime crashes in the deployed service.
   - **One reason to still write unit tests with stubs:** Unit tests run in milliseconds without needing a running server, network connection, or database setup, making it much faster and easier to isolate the exact line of logic that broke and to test edge cases or error conditions (like simulated disk/database failures) that are difficult to trigger through the external API.

2. **Why every test creates its own user rather than using the public token, and how this applies to Project 2:**
   - The public token (`abcdef0123456789`) is shared by everyone practicing on QuickPizza. If our tests created, updated, or deleted ratings using the public token, our tests would collide with other students' tests running at the same time (or our own previous test runs), leading to race conditions, corrupted shared data, and flaky test failures. By creating a fresh user with a unique UUID name (`lab-<uuid>`) per test via fixtures, each test has an isolated workspace and starts with a known state (`{"ratings": []}`).
   - **Application to Project 2:** In Project 2 (testing the shared shop or hotel system), every test (or test fixture) should dynamically create its own unique resources (e.g., a new cart, customer, booking, or product) before running assertions and clean them up afterward (`yield` + teardown `DELETE`), and never modify or delete pre-existing shared data created by the instructor or other student groups.

3. **Why tests send every request through one session (`requests.Session`), and what happened in Step 0.12:**
   - QuickPizza runs on multiple backend server instances behind an AWS Application Load Balancer, and each server instance stores its users and ratings in its own local memory/database rather than a synchronized central database. When the first response comes back, the load balancer sets an `AWSALB` sticky-session cookie so subsequent requests carrying that cookie are routed to the exact same backend server. Using a single `requests.Session` (the `api` fixture with `scope="session"`) automatically stores and sends this `AWSALB` cookie on every request, ensuring all requests hit the same server instance.
   - **What happened in Step 0.12:** When we ran `test_no_session.py` using standalone `requests.post()` calls without a session, no cookies were saved. As a result, `POST /api/users` created the user on one server, and `POST /api/users/token/login` was often routed by the load balancer to a *different* server that did not have that user, causing login to fail with `401 Unauthorized` on Run 1 and Run 3 while passing by chance on Run 2 (a classic **flaky test**).

4. **Step 0.16 defect analysis (block, 500 vs 400, and keeping the test as `xfail`):**
   - **Which block revealed the defect:** The block where **all 3 tools are excluded** (`["Knife", "Pizza cutter", "Scissors"]`) in the characteristic *"how many of the three tools are excluded"*.
   - **Why a 500 with an empty body is worse than a 400 with a message:** Status `400 Bad Request` with a JSON error message tells the client application that the user's input constraints are invalid, allowing the app to parse the JSON safely and display a helpful message to the user. Status `500 Internal Server Error` with an empty body indicates an unhandled server crash (e.g., division by zero / empty slice index panic), gives the caller no explanation of what went wrong, causes `res.json()` in client apps to crash with a `JSONDecodeError`, and triggers false server-outage alerts in monitoring systems.
   - **Why keep the test as `xfail` instead of deleting it:** Deleting a failing test hides a known bug and loses executable documentation of the requirement. Marking it with `@pytest.mark.xfail(reason="...", strict=True)` keeps the defect visible in test reports while allowing the rest of the CI test suite to pass. Because `strict=True` is set, as soon as the developers fix the bug and the endpoint returns `400`, pytest will report an `XPASS` failure, alerting us to remove the `xfail` marker and turn it into a normal regression test.

5. **Counting tests for Base Choice Coverage vs. All Combinations Coverage in Step A1:**
   - The Input Domain Model in Step A1 has 4 characteristics with the following numbers of blocks:
     - **C1 (Value of stars):** 3 blocks (`below 1`, `1 to 5 (base)`, `above 5`)
     - **C2 (Type of stars):** 4 blocks (`whole number (base)`, `decimal`, `text`, `missing`)
     - **C3 (Pizza):** 2 blocks (`exists (base)`, `does not exist`)
     - **C4 (Token):** 3 blocks (`the user's own (base)`, `none`, `wrong length`)
   - **Base Choice Coverage:** Starts with 1 base test (all base blocks) and adds 1 test for each remaining non-base block while keeping other characteristics at their base values:
     $$1 + (3 - 1) + (4 - 1) + (2 - 1) + (3 - 1) = 1 + 2 + 3 + 1 + 2 = 9\text{ tests}$$
   - **All Combinations Coverage (ACoC):** Multiplies the number of blocks across all characteristics:
     $$3 \times 4 \times 2 \times 3 = 72\text{ tests}$$

6. **Step A4 status codes analysis (actual vs. expected, and whether the difference is a defect):**
   - **Actual status codes:** When `other_auth` tried to access `auth`'s rating, `GET` returned `404 Not Found` (`{"error": "not found"}`), while `PUT` and `DELETE` both returned `400 Bad Request` (`{"error": "rating ID <id> not found"}`).
   - **Expected status codes:** Standard REST API conventions would expect either `403 Forbidden` (authenticated user lacks permission to access another user's resource) or `404 Not Found` consistently across `GET`, `PUT`, and `DELETE` (to avoid leaking whether the rating ID exists for another user).
   - **Is the difference a defect?** Returning `404 Not Found` on `GET` is an intentional, secure design pattern (preventing ID enumeration). However, returning `400 Bad Request` with `"rating ID <id> not found"` for `PUT` and `DELETE` instead of `403 Forbidden` or `404 Not Found` is a **minor API design defect (inconsistency)**. A `400` status code normally means malformed syntax or invalid payload values, whereas a missing or unauthorized resource in the URL path should be `404` or `403`. Nonetheless, from a security standpoint, the API properly refuses all three unauthorized operations and leaves the owner's rating untouched.

7. **Result and security analysis of `madeup.txt` (`Authorization: token 0000000000000000`):**
   - **What comes back:** Sending `GET /api/ratings` with `Authorization: token 0000000000000000` returns HTTP `200 OK` along with a JSON list of ratings (`{"ratings": [{"id": 1, "stars": 5, "pizza_id": 1}, ...]}`), which are the public/default ratings!
   - **Is this a defect, and what could a stranger do on a real system?** **Yes, this is a critical security defect (Broken Authentication).** When QuickPizza checks a token that does not belong to any registered user, it only checks that the token string is exactly 16 characters long; if it is 16 characters long, it accepts the request and falls back to the default/public user context instead of rejecting the unauthenticated token with `401 Unauthorized`. On a real production system, an attacker could bypass login completely without a valid account or password simply by inventing any 16-character string, allowing them to read protected data, create spam records, or modify/delete shared resources.

8. **Comparison between API tests and Web UI tests:**
   - **One thing an API test checks better than a Web UI test:** Exact HTTP status codes (`200`, `201`, `400`, `401`, `404`, `500`), JSON response schemas/error messages, and backend security/validation rules (such as attempting `PUT`/`DELETE` as another user or sending malformed data types like `"stars": 3.5` that the browser UI dropdown would prevent a user from selecting), while running orders of magnitude faster and without browser flakiness.
   - **One thing that only a test through the Web pages (UI test) can check:** Visual rendering, layout, and client-side browser behavior—such as whether buttons, forms, CSS styles, and error messages are actually visible, clickable, and properly displayed to a human user in the DOM.

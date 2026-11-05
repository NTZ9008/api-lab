# API Lab — ITDS362 API Testing with pytest and requests

This repository contains the automated API test suite for the QuickPizza API (`https://quickpizza.grafana.com`), using `pytest` and `requests`.

## Setup and Installation

1. Clone this repository and navigate into the project directory:
   ```bash
   git clone https://github.com/NTZ9008/api-lab.git
   cd api-lab
   ```

2. Create and activate a Python virtual environment, then install the required packages:

   **Windows (PowerShell / Git Bash):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Running the Tests

Run the full test suite with verbose output:

```powershell
.venv/Scripts/pytest -v
```

Generate a self-contained HTML test report (`report.html`):

```powershell
.venv/Scripts/pytest -v --html=report.html --self-contained-html
```

## Input Domain Model for `POST /api/ratings` (Steps A1 & A2)

`POST /api/ratings` takes a JSON body with two fields (`pizza_id` and `stars`) and an `Authorization` token in the header. Below is the Input Space Partitioning (ISP) model using **Base Choice Coverage** (9 tests total):

| Characteristic | Blocks | Values in the tests | Test function covering each block |
| :--- | :--- | :--- | :--- |
| **C1 Value of stars** | below 1, 1 to 5 (base), above 5 | `0`, `3`, `6` |<ul><li>below 1 (`0`): `test_stars_out_of_range[0]`</li><li>1 to 5 (base, `3`): `test_base_choice_is_saved`</li><li>above 5 (`6`): `test_stars_out_of_range[6]`</li></ul> |
| **C2 Type of stars** | whole number (base), decimal, text, missing | `3`, `3.5`, `"3"`, no field |<ul><li>whole number (base, `3`): `test_base_choice_is_saved`</li><li>decimal (`3.5`): `test_decimal_stars_is_refused`</li><li>text (`"3"`): `test_text_stars_is_refused`</li><li>missing (no field): `test_missing_stars_is_refused`</li></ul> |
| **C3 Pizza** | exists (base), does not exist | a new pizza, `999999999` |<ul><li>exists (base, `pizza_id`): `test_base_choice_is_saved`</li><li>does not exist (`999999999`): `test_nonexistent_pizza_is_refused`</li></ul> |
| **C4 Token** | the user's own (base), none, wrong length | from `auth`, no header, `token short` |<ul><li>the user's own (base, `auth`): `test_base_choice_is_saved`</li><li>none (no header): `test_rating_without_token_is_refused`</li><li>wrong length (`token short`): `test_rating_with_short_token_is_refused`</li></ul> |

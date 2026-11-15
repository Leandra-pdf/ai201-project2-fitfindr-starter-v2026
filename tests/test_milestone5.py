#!/usr/bin/env python3
"""
Run the five FitFindr Milestone 4 acceptance criteria three times.

Run this file from the FitFindr project root:
    python test_milestone5.py https://YOUR-RENDER-URL

Or set FITFINDR_URL and run:
    FITFINDR_URL=https://YOUR-RENDER-URL python test_milestone5.py

The script tests ranking and filters locally using controlled listings, then
tests the deployed HTTP endpoints. It saves a Markdown run log and raw JSON
evidence under results/milestone5/.

The five /ask requests used for Criterion 9 are reused from Criterion 8's
ten successful-request logging checks, so each trial makes ten valid model
requests, not 15. Criterion 8 and Criterion 10 require manual verification
against the corresponding Render Runtime Logs.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TRIALS = 3
BASE_QUERY = "garment"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "tests" else SCRIPT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

# Ten distinct valid queries per trial. Using different queries avoids making
# every measurement a repeat of the exact same cached request.
ASK_QUERIES = [
    [
        "vintage graphic tee under $30",
        "Y2K baby tee under $25",
        "oversized vintage band tee under $35",
        "cropped butterfly print top under $20",
        "faded 90s concert shirt under $30",
        "black graphic tee under $25",
        "retro tour shirt under $40",
        "casual streetwear tee under $30",
        "vintage cotton baby tee under $25",
        "colorful graphic shirt under $30",
    ],
    [
        "vintage graphic shirt under $35",
        "pink Y2K baby tee under $25",
        "oversized faded band shirt under $40",
        "cropped retro graphic tee under $30",
        "90s butterfly print shirt under $25",
        "black vintage concert tee under $35",
        "retro music tour top under $30",
        "casual graphic baby tee under $20",
        "vintage cotton band tee under $40",
        "colorful Y2K shirt under $30",
    ],
    [
        "secondhand vintage graphic tee under $30",
        "fitted Y2K baby tee under $25",
        "relaxed oversized band tee under $35",
        "cropped butterfly graphic shirt under $25",
        "faded vintage concert tee under $40",
        "black retro graphic shirt under $30",
        "old-school tour tee under $35",
        "everyday streetwear graphic top under $30",
        "vintage baby tee under $20",
        "bright colorful graphic tee under $35",
    ],
]

SESSION_KEYS = {
    "query",
    "parsed",
    "search_results",
    "selected_item",
    "wardrobe",
    "outfit_suggestion",
    "fit_card",
    "error",
}


def make_listing(listing_id, title, description, style_tags, size, price):
    """Create a small listing dictionary matching the project's listing shape."""
    return {
        "id": listing_id,
        "title": title,
        "description": description,
        "style_tags": style_tags,
        "size": size,
        "price": price,
        "category": "top",
        "condition": "good",
        "colors": ["black"],
        "brand": None,
        "platform": "Test Closet",
    }


def run_criterion_6():
    """Test that title/style-tag matches outrank weaker description matches."""
    import tools

    original_loader = tools.load_listings
    test_listings = []

    def fake_load_listings():
        return test_listings

    tools.load_listings = fake_load_listings

    cases = [
        ("velvet", "title"),
        ("crochet", "title"),
        ("butterfly", "title"),
        ("retro", "style_tags"),
        ("boho", "style_tags"),
    ]

    evidence = []
    passed = 0

    try:
        for number, case in enumerate(cases, start=1):
            keyword, strong_field = case

            strong = make_listing(
                f"strong_{number}",
                keyword if strong_field == "title" else "Plain top",
                "A basic garment.",
                [keyword] if strong_field == "style_tags" else [],
                "M",
                20,
            )
            weak = make_listing(
                f"weak_{number}",
                "Plain top",
                f"A garment with {keyword} mentioned only in its description.",
                [],
                "M",
                20,
            )

            # The winner is deliberately matched in a more heavily weighted
            # field than the weaker listing.
            test_listings[:] = [weak, strong]
            results = tools.search_listings(keyword)
            result_ids = [item["id"] for item in results]
            strong_score = tools._listing_score(
                tools._keywords(keyword), strong
            )
            weak_score = tools._listing_score(
                tools._keywords(keyword), weak
            )

            case_passed = bool(result_ids) and result_ids[0] == strong["id"]
            if case_passed:
                passed += 1

            evidence.append({
                "case": number,
                "query": keyword,
                "strong_match_field": strong_field,
                "scores": {
                    strong["id"]: strong_score,
                    weak["id"]: weak_score,
                },
                "returned_order": result_ids,
                "passed": case_passed,
            })
    finally:
        tools.load_listings = original_loader

    return {
        "passed": passed,
        "total": len(cases),
        "met": passed == len(cases),
        "evidence": evidence,
        "source": "tools.py: search_listings(), _listing_score()",
    }


def run_criterion_7():
    """Test five price ceilings and five size filters against known listings."""
    import tools

    original_loader = tools.load_listings
    test_listings = [
        make_listing("small_10", "Garment small", "garment", [], "S", 10),
        make_listing("medium_20", "Garment medium", "garment", [], "M", 20),
        make_listing("sm_25", "Garment S M", "garment", [], "S/M", 25),
        make_listing("one_size_30", "Garment one size", "garment", [], "ONE SIZE", 30),
        make_listing("xl_40", "Garment XL", "garment", [], "XL", 40),
    ]

    def fake_load_listings():
        return test_listings

    tools.load_listings = fake_load_listings

    evidence = []
    passed = 0

    try:
        price_cases = [10, 20, 25, 30, 35]
        for number, ceiling in enumerate(price_cases, start=1):
            results = tools.search_listings(BASE_QUERY, max_price=ceiling)
            returned = [
                {"id": item["id"], "price": item["price"]}
                for item in results
            ]
            case_passed = all(item["price"] <= ceiling for item in results)
            if case_passed:
                passed += 1
            evidence.append({
                "case": number,
                "filter": "max_price",
                "requested": ceiling,
                "returned": returned,
                "passed": case_passed,
            })

        size_cases = [
            ("S", {"small_10", "sm_25", "one_size_30"}),
            ("M", {"medium_20", "sm_25", "one_size_30"}),
            ("XL", {"xl_40", "one_size_30"}),
            ("ONE SIZE", {"one_size_30"}),
            ("S/M", {"small_10", "medium_20", "sm_25", "one_size_30"}),
        ]

        for number, case in enumerate(size_cases, start=6):
            requested_size, expected_ids = case
            results = tools.search_listings(BASE_QUERY, size=requested_size)
            returned_ids = {item["id"] for item in results}
            case_passed = returned_ids == expected_ids
            if case_passed:
                passed += 1
            evidence.append({
                "case": number,
                "filter": "size",
                "requested": requested_size,
                "returned_ids": sorted(returned_ids),
                "expected_ids": sorted(expected_ids),
                "passed": case_passed,
            })
    finally:
        tools.load_listings = original_loader

    return {
        "passed": passed,
        "total": len(evidence),
        "met": passed == len(evidence),
        "evidence": evidence,
        "source": "tools.py: search_listings(), _size_matches()",
    }


def http_request(base_url, method, path, payload=None, timeout=120):
    """Send one HTTP request and preserve its real status, body, and duration."""
    url = base_url.rstrip("/") + path
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=data, headers=headers, method=method)
    request_started_at = datetime.now(timezone.utc).isoformat(
        timespec="milliseconds"
    )
    started = time.perf_counter()

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            status = response.status
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        status = exc.code
    except (URLError, TimeoutError, OSError) as exc:
        body = f"{type(exc).__name__}: {exc}"
        status = None

    duration = time.perf_counter() - started

    try:
        parsed_body = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        parsed_body = None

    return {
        "method": method,
        "path": path,
        "request_started_at_utc": request_started_at,
        "status": status,
        "duration_seconds": round(duration, 3),
        "body": body,
        "json": parsed_body,
    }


def run_http_trial(base_url, trial_number):
    """Run successful-request logging, endpoint-shape, and failure checks."""
    ask_results = []

    for query in ASK_QUERIES[trial_number - 1]:
        result = http_request(
            base_url,
            "POST",
            "/ask",
            {"query": query},
        )
        result["query"] = query
        body = result["json"]
        result["has_expected_session_shape"] = (
            isinstance(body, dict) and SESSION_KEYS.issubset(body.keys())
        )
        result["successful_response"] = result["status"] == 200
        ask_results.append(result)

    health_results = []
    for _ in range(5):
        result = http_request(base_url, "GET", "/health")
        body = result["json"]
        result["has_expected_health_shape"] = (
            isinstance(body, dict) and body.get("status") == "ok"
        )
        health_results.append(result)

    # These are deliberate validation failures. They should return HTTP 400,
    # not 500, and should create error-bearing POST /ask log records on Render.
    failure_payloads = [
        [],
        {"query": ""},
        {"query": None},
        {"query": 123},
        {"query": "   "},
    ]
    failure_results = []

    for payload in failure_payloads:
        result = http_request(base_url, "POST", "/ask", payload)
        result["payload"] = payload
        result["returned_400"] = result["status"] == 400
        failure_results.append(result)

    successful_ask_responses = sum(
        1 for result in ask_results if result["successful_response"]
    )
    endpoint_passed = sum(
        1 for result in ask_results[:5]
        if result["status"] == 200 and result["has_expected_session_shape"]
    ) + sum(
        1 for result in health_results
        if result["status"] == 200 and result["has_expected_health_shape"]
    )
    failure_passed = sum(
        1 for result in failure_results if result["returned_400"]
    )

    return {
        "criterion_8": {
            # HTTP success is measured automatically. Do not mark MET until
            # all ten corresponding server-side log entries are verified.
            "http_successful": successful_ask_responses,
            "total": 10,
            "met": None,
            "requests": ask_results,
            "log_verification": (
                "Verify ten matching Render Runtime Log entries for POST "
                "/ask. Each must show status 200 and numeric "
                "duration_seconds. Correlate using request_started_at_utc "
                "and query."
            ),
        },
        "criterion_9": {
            "passed": endpoint_passed,
            "total": 10,
            "met": endpoint_passed == 10,
            "health_requests": health_results,
            # Reuses the first five valid /ask requests from Criterion 8.
            "ask_requests": ask_results[:5],
        },
        "criterion_10": {
            "passed": failure_passed,
            "total": 5,
            # The HTTP statuses are checked here. Render log entries still
            # need manual inspection before this criterion can be marked MET.
            "met": None,
            "requests": failure_results,
            "log_verification": (
                "Manual check required in Render Runtime Logs: confirm five "
                "POST /ask records with status 400, duration_seconds, and "
                "non-empty error fields."
            ),
        },
    }


def compact_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def summarize_http_request(result):
    """Keep actual response evidence readable in the Markdown report."""
    return {
        "method": result.get("method"),
        "path": result.get("path"),
        "status": result.get("status"),
        "duration_seconds": result.get("duration_seconds"),
        "body": result.get("body"),
    }


def write_report(output_dir, all_trials):
    """Write the three-run table and actual Run 1 evidence."""
    criteria = [
        ("6. Weighted reranking", "5 of 5", "criterion_6"),
        ("7. Price and size filters", "10 of 10", "criterion_7"),
        ("8. Successful /ask requests are logged", "10 of 10", "criterion_8"),
        ("9. /health and /ask responses", "10 of 10", "criterion_9"),
        ("10. Failure requests return 400", "5 of 5", "criterion_10"),
    ]

    lines = [
        "# FitFindr Milestone 5 Run Log",
        "",
        "Three trials were run sequentially with the same test definitions.",
        "Criterion 9 reuses five valid `/ask` requests from Criterion 8.",
        "",
        "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |",
        "|---|---:|---:|---:|---:|---|",
    ]

    for label, target, key in criteria:
        values = []
        for trial in all_trials:
            result = trial[key]
            if key == "criterion_8":
                values.append(f"{result['http_successful']}/10 HTTP; logs pending")
            elif key == "criterion_10":
                values.append(f"{result['passed']}/5 HTTP; logs pending")
            else:
                values.append(f"{result['passed']}/{result['total']}")

        if key in {"criterion_8", "criterion_10"}:
            verdict = "PENDING LOG CHECK"
        else:
            met_all = all(trial[key]["met"] for trial in all_trials)
            verdict = "MET" if met_all else "MISSED"
        lines.append(
            f"| {label} | {target} | {values[0]} | {values[1]} "
            f"| {values[2]} | {verdict} |"
        )

    lines.extend([
        "",
        "## Run 1 evidence — actual test output",
        "",
        "### Criterion 6 — weighted reranking",
        "",
        "Produced by `tools.py`: `search_listings()` and `_listing_score()`.",
        "",
        "```json",
        compact_json(all_trials[0]["criterion_6"]["evidence"]),
        "```",
        "",
        "### Criterion 7 — price and size filters",
        "",
        "Produced by `tools.py`: `search_listings()` and `_size_matches()`.",
        "",
        "```json",
        compact_json(all_trials[0]["criterion_7"]["evidence"]),
        "```",
        "",
        "### Criterion 8 — successful `/ask` request instrumentation",
        "",
        "Produced by `serve.py`: the `/ask` route and request logging. The "
        "script records UTC request start times, query text, and HTTP results "
        "to help correlate the ten requests with Render Runtime Logs.",
        "",
        "```json",
        compact_json([
            {
                **summarize_http_request(item),
                "request_started_at_utc": item.get("request_started_at_utc"),
                "query": item.get("query"),
            }
            for item in all_trials[0]["criterion_8"]["requests"]
        ]),
        "```",
        "",
        "**Important:** A successful HTTP response does not prove its server "
        "log entry was written. Verify all ten matching `POST /ask` entries "
        "in Render Runtime Logs. Each must show HTTP 200 and a numeric "
        "`duration_seconds` field. Paste the actual log lines below.",
        "",
        "```text",
        "[RUN 1: PASTE TEN ACTUAL SUCCESSFUL RENDER LOG LINES HERE]",
        "```",
        "",
        "Run 2: verify and paste ten matching successful `/ask` log lines.",
        "```text",
        "[RUN 2: PASTE TEN ACTUAL SUCCESSFUL RENDER LOG LINES HERE]",
        "```",
        "",
        "Run 3: verify and paste ten matching successful `/ask` log lines.",
        "```text",
        "[RUN 3: PASTE TEN ACTUAL SUCCESSFUL RENDER LOG LINES HERE]",
        "```",
        "",
        "### Criterion 9 — endpoint responses",
        "",
        "Produced by `serve.py`: `/health` and `/ask` routes.",
        "",
        "```json",
        compact_json({
            "health": [
                summarize_http_request(item)
                for item in all_trials[0]["criterion_9"]["health_requests"]
            ],
            "ask": [
                summarize_http_request(item)
                for item in all_trials[0]["criterion_9"]["ask_requests"]
            ],
        }),
        "```",
        "",
        "### Criterion 10 — deliberate failures",
        "",
        "Produced by `serve.py`: `/ask` validation and `after_request` "
        "logging; this script sends the requests and records the responses.",
        "",
        "```json",
        compact_json([
            summarize_http_request(item)
            for item in all_trials[0]["criterion_10"]["requests"]
        ]),
        "```",
        "",
        "**Important:** HTTP 400 responses alone do not prove the log entries "
        "were written. Verify the five matching `POST /ask` records in Render "
        "Runtime Logs and paste those actual JSON log lines below.",
        "",
        "```text",
        "[RUN 1: PASTE FIVE ACTUAL FAILED-REQUEST LOG LINES HERE]",
        "```",
        "",
        "Run 2: verify and paste five matching failed `/ask` log lines.",
        "```text",
        "[RUN 2: PASTE FIVE ACTUAL FAILED-REQUEST LOG LINES HERE]",
        "```",
        "",
        "Run 3: verify and paste five matching failed `/ask` log lines.",
        "```text",
        "[RUN 3: PASTE FIVE ACTUAL FAILED-REQUEST LOG LINES HERE]",
        "```",
        "",
        "## Notes",
        "",
        "- The script does not change the project code or listing data.",
        "- Each trial uses five reranking cases and ten filter cases.",
        "- Each trial sends ten valid `/ask` requests, five `/health` requests, "
        "and five deliberate invalid `/ask` requests.",
        "- Criterion 8 remains unverified until all ten successful `/ask` "
        "log entries are inspected.",
        "- Criterion 10 remains unverified until all five failed `/ask` "
        "log entries are inspected.",
        "",
    ])

    report_path = output_dir / "milestone5_run_log.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main():
    base_url = (
        sys.argv[1] if len(sys.argv) > 1
        else os.getenv("FITFINDR_URL")
    )

    if not base_url:
        base_url = input("Enter your deployed FitFindr URL: ").strip()

    if not base_url.startswith(("https://", "http://")):
        print("Please provide a full URL beginning with https:// or http://")
        return 1

    output_dir = PROJECT_ROOT / "results" / "milestone5"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nFitFindr Milestone 5 tests")
    print(f"Target: {base_url}")
    print(f"Trials: {TRIALS}")
    print("Do not change the project or test setup until all trials finish.\n")

    all_trials = []

    for trial_number in range(1, TRIALS + 1):
        print(f"========== TRIAL {trial_number} OF {TRIALS} ==========")

        criterion_6 = run_criterion_6()
        print(
            f"Criterion 6 weighted reranking: "
            f"{criterion_6['passed']}/{criterion_6['total']}"
        )

        criterion_7 = run_criterion_7()
        print(
            f"Criterion 7 price/size filters: "
            f"{criterion_7['passed']}/{criterion_7['total']}"
        )

        http_results = run_http_trial(base_url, trial_number)

        for number, key in [
            (8, "criterion_8"),
            (9, "criterion_9"),
            (10, "criterion_10"),
        ]:
            result = http_results[key]
            if number == 8:
                print(
                    f"Criterion 8 successful /ask HTTP responses: "
                    f"{result['http_successful']}/10 "
                    "(Render log verification still required)"
                )
            else:
                print(
                    f"Criterion {number}: "
                    f"{result['passed']}/{result['total']}"
                )

        trial = {
            "trial": trial_number,
            "criterion_6": criterion_6,
            "criterion_7": criterion_7,
            **http_results,
        }
        all_trials.append(trial)

        raw_path = output_dir / f"trial_{trial_number}.json"
        raw_path.write_text(
            compact_json(trial) + "\n",
            encoding="utf-8",
        )
        print(f"Saved raw results: {raw_path}\n")

    report_path = write_report(output_dir, all_trials)

    print("========== FINAL SUMMARY ==========")
    for number, key in [
        (6, "criterion_6"),
        (7, "criterion_7"),
        (8, "criterion_8"),
        (9, "criterion_9"),
        (10, "criterion_10"),
    ]:
        if key == "criterion_8":
            scores = [f"{trial[key]['http_successful']}/10 HTTP" for trial in all_trials]
            verdict = "PENDING LOG CHECK"
        elif key == "criterion_10":
            scores = [f"{trial[key]['passed']}/{trial[key]['total']} HTTP" for trial in all_trials]
            verdict = "PENDING LOG CHECK"
        else:
            scores = [f"{trial[key]['passed']}/{trial[key]['total']}" for trial in all_trials]
            met_all = all(trial[key]["met"] for trial in all_trials)
            verdict = "MET" if met_all else "MISSED"
        print(f"Criterion {number}: {', '.join(scores)} — {verdict}")

    print("\nReports saved:")
    print(f"  {report_path}")
    print(f"  {output_dir / 'trial_1.json'}")
    print(f"  {output_dir / 'trial_2.json'}")
    print(f"  {output_dir / 'trial_3.json'}")
    print(
        "\nBefore submitting, verify all 30 successful and 15 failed /ask "
        "log records across the three trials in Render Runtime Logs. "
        "Paste the actual log lines into the report."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

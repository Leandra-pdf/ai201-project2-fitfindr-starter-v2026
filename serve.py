#!/usr/bin/env python3
"""
FitFindr over HTTP. ← UNIT 9

    python serve.py                       run it on your machine
    gunicorn serve:app                    run it the way a host runs it

Everything else in this repo exits after one command. A host has nothing to
keep running, so a command line cannot be deployed. This file is the smallest
thing that can: it starts a web server, waits, and hands each request to the
same `run_agent()` your CLI calls. **No new agent logic lives here.** If your
loop works from `python app.py ask`, it works from here; if it doesn't, fix it
there, not in this file.

Routes:

    GET  /           FitFindr homepage
    GET  /ask        Search form
    POST /ask        Submit a search
    GET  /health     Is the server awake?

`/ask` supports two kinds of POST requests:

    Browser form:  sends form data and receives an HTML results page.
    JSON API:      sends {"query": "...", "wardrobe": {...}} and receives
                   the session dict from `run_agent()` as JSON, unchanged.

The wardrobe is optional. Without one, the example wardrobe is used.

The JSON response keeps the same keys you print from the command line,
including `error`. Read `session["error"]` first, exactly as you do everywhere
else.

It runs **one request at a time**, and one route is deliberately slower than a
web server has to be. The reason is worth reading before you deploy: see the
note above `_one_at_a_time` below — it also decides which gunicorn worker you
can use.

Requests are instrumented with structured logs. Each completed request records
its timestamp, method, path, input, output summary, duration, status, errors,
and relevant system information. Logs go to `fitfindr.log` and the server's
standard output (which Render captures).
"""

import os
import sys
import json
import logging
import platform
import threading
import time
from datetime import datetime, timezone

# config first, and before anything that talks to the model: it loads your .env
# and fixes the Windows console encoding for every module that imports it.
import config  # noqa: F401

from flask import Flask, jsonify, render_template, request, g
from werkzeug.exceptions import HTTPException

from agent import run_agent
from utils.data_loader import get_example_wardrobe

app = Flask(__name__)


# ── structured logging ────────────────────────────────────────────────────────
# Write logs to a local file so they can be inspected after running the app.
# Also write to standard output so Render can collect them in Runtime Logs.

logger = logging.getLogger("fitfindr")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter("%(message)s")

    file_handler = logging.FileHandler("fitfindr.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def log_request(query, output, duration, status, error=None,
                method=None, path=None):
    """Write one structured record for an HTTP request."""

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "input": query,
        "output": output,
        "duration_seconds": round(duration, 3),
        "status": status,
        "error": error,
        "python_version": platform.python_version(),
        "platform": platform.system()
    }

    logger.info(json.dumps(record, default=str))


@app.before_request
def start_request():
    """Capture the start time and input before handling each request."""

    g.start_time = time.perf_counter()
    g.log_query = None
    g.log_output = None
    g.log_error = None

    # Capture the query for logging without assuming the JSON body is valid.
    if request.is_json:
        payload = request.get_json(silent=True)

        if isinstance(payload, dict):
            g.log_query = payload.get("query")

    elif request.method == "POST":
        g.log_query = request.form.get("query")


@app.after_request
def finish_request(response):
    """Log every completed request, including errors."""

    duration = time.perf_counter() - g.start_time

    log_request(
        query=g.log_query,
        output=g.log_output,
        duration=duration,
        status=response.status_code,
        error=g.log_error,
        method=request.method,
        path=request.path
    )

    return response


# ── one request at a time ─────────────────────────────────────────────────────
# Here's why this exists.
#
# A web server will happily run two requests at once. Two things in this repo
# assume otherwise:
#
#   • If you moved a tool onto MCP in unit 4, `mcp_client.call_tool` starts
#     `mcp_server.py` as a separate process over stdio, one per call. Two
#     overlapping requests means two extra Python interpreters, and the free
#     tier you're deploying to has 512 MB for all of it. That is the reason
#     that would still be here even if everything else were perfect.
#   • `generate.py`'s pacing window and its call counter are plain module
#     globals — deliberately, because that file is teaching pacing and quota,
#     not locking. Two threads sharing them means the per-minute limiter is
#     counting something that isn't true.
#
# What the lock covers is exactly the agent run: the part that spawns
# processes and calls the model. Reading the request, rejecting a bad one, and
# turning the answer into HTML or JSON all happen outside it — so a request
# with a malformed body comes straight back with a 400 instead of queueing
# behind somebody else's agent.
#
# Serialising the runs costs you nothing here — this is one user asking one
# question — and it keeps the deployed behaviour identical to the CLI's. When
# that stops being an acceptable trade, the fix is a real queue, not a bigger
# lock.
#
# The same constraint decides your start command, and this is the part that
# bites in deployment rather than on your machine. `mcp_client.call_tool`
# wraps `asyncio.run()`, and `asyncio.run()` refuses to start when an event
# loop is already running. An async worker always has one running. So under
# `gunicorn -k gevent` (or `-k eventlet`, or `serve:app` wrapped for an ASGI
# server like uvicorn) EVERY MCP call fails with "asyncio.run() cannot be
# called from a running event loop" — not some of them under load, all of
# them, every time, in a place your laptop never showed you.
#
#     gunicorn serve:app              ← right: the DEFAULT sync worker
#     gunicorn -k gevent serve:app    ← breaks every MCP call you make

_one_at_a_time = threading.Lock()


@app.get("/")
def home():
    """Show the FitFindr homepage."""
    g.log_output = {"page": "homepage"}
    return render_template("index.html")


@app.get("/health")
def health():
    """Is the server awake? A host pings something like this to find out."""
    g.log_output = {"status": "ok"}
    return jsonify({"status": "ok"})


@app.route("/ask", methods=["GET", "POST"])
def ask():
    """
    Display the search form or run the agent on one query.

    GET:
        Display the HTML search form.

    POST with form data:
        Run the agent and display an HTML results page.

    POST with JSON:
        Run the agent and return the session dict as JSON, unchanged.
    """

    # A browser visit to /ask should show the form, not return a 405.
    if request.method == "GET":
        g.log_output = {"page": "search_form"}
        return render_template("ask.html", query="", session=None, error=None)

    # Determine whether this is a browser form submission or a JSON API call.
    is_api_request = request.is_json

    if is_api_request:
        payload = request.get_json(silent=True)

        # A JSON request must contain an object, not a list, string, or invalid
        # JSON body. Checking the type prevents an AttributeError on payload.get.
        if not isinstance(payload, dict):
            error = "Invalid JSON body. Send a JSON object with a 'query' field."
            g.log_error = error
            g.log_output = {"error": error}
            return jsonify({"error": error}), 400

        query = payload.get("query")
        wardrobe = payload.get("wardrobe")

    else:
        query = request.form.get("query")
        wardrobe = None

    if not isinstance(query, str) or not query.strip():
        error = "Please enter a search query."
        g.log_error = error
        g.log_output = {"error": error}

        if is_api_request:
            return jsonify({"error": error}), 400

        return render_template(
            "ask.html",
            query="",
            session=None,
            error=error
        ), 400

    query = query.strip()
    g.log_query = query

    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()

    # The lock keeps overlapping requests from starting multiple agent runs.
    if _one_at_a_time.locked():
        logger.info(json.dumps({
            "event": "request_waiting",
            "path": request.path,
            "method": request.method
        }))

    try:
        with _one_at_a_time:
            session = run_agent(query, wardrobe)

        if not isinstance(session, dict):
            raise ValueError("The agent returned an invalid session.")

    except Exception as exc:
        # Keep internal exception details in the log, not in the browser.
        failure = f"{type(exc).__name__}: {exc}"
        g.log_error = failure
        g.log_output = {"error": "Agent request failed."}

        if is_api_request:
            return jsonify({"error": "The FitFindr request failed."}), 500

        return render_template(
            "ask.html",
            query=query,
            session=None,
            error="Something went wrong while searching. Please try again."
        ), 500

    # Log a summary rather than the entire generated response.
    selected_item = session.get("selected_item")
    selected_item_id = None

    if isinstance(selected_item, dict):
        selected_item_id = selected_item.get("id")

    search_results = session.get("search_results", [])
    if isinstance(search_results, (list, dict)):
        result_count = len(search_results)
    else:
        result_count = 0

    output_summary = {
        "selected_item": selected_item_id,
        "search_result_count": result_count,
        "outfit_suggestion_created": bool(session.get("outfit_suggestion")),
        "fit_card_created": bool(session.get("fit_card")),
        "agent_error": session.get("error")
    }

    g.log_output = output_summary

    # Keep the agent's own error in the log, even if run_agent returned
    # normally. The existing API contract still returns the session unchanged.
    if session.get("error"):
        g.log_error = session.get("error")

    # JSON API clients receive the same session structure as before.
    if is_api_request:
        return jsonify(session)

    # Browser users receive a rendered HTML results page.
    return render_template(
        "ask.html",
        query=query,
        session=session,
        error=session.get("error")
    )


@app.errorhandler(Exception)
def handle_unexpected_error(exc):
    """Handle unexpected errors without exposing internal details to visitors."""

    if isinstance(exc, HTTPException):
        g.log_error = exc.description

        if request.is_json:
            return jsonify({"error": exc.description}), exc.code

        return render_template(
            "index.html",
            error=exc.description
        ), exc.code

    g.log_error = f"{type(exc).__name__}: {exc}"
    g.log_output = {"error": "Unexpected server error."}

    if request.is_json:
        return jsonify({"error": "An unexpected server error occurred."}), 500

    return render_template(
        "index.html",
        error="Something went wrong. Please try again."
    ), 500


if __name__ == "__main__":
    # PORT and 0.0.0.0 are not decoration. A host tells you which port to
    # listen on through PORT, and it reaches your process from outside the
    # container — bind 127.0.0.1 and nothing but the container itself can
    # connect, which looks exactly like a broken app from the browser.
    port = int(os.getenv("PORT", "8080"))

    # Never on by default. Flask's debugger executes code typed into a browser,
    # and a deployed app with it on is a stranger's shell. Set AI201_DEBUG=1 in
    # your own terminal when you want the reloader.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"\nFitFindr is listening on http://localhost:{port}")
    print("It runs one request at a time — a second one waits for the first.")
    print("Ask it something (single quotes, as always):\n")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"query\": \"vintage graphic tee under $30\"}}'\n"
    )
    print("Ctrl-C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=debug)

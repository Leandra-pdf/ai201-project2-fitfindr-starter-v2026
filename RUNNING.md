# Running FitFindr

Everything about how the app works and how to use it. This guide explains how to run FitFindr locally, use the deployed app, test its HTTP endpoints, and inspect its request logs.

## Capstone Deployed app

**Live app:** [YOUR_RENDER_URL]

Replace `YOUR_RENDER_URL` above with the public URL shown for your FitFindr web service in the Render dashboard. The same base URL is used for the home page and API endpoints.

- Open the live app: `https://ai201-project2-fitfindr-starter-v2026-0nk2.onrender.com/`
- Health check: `https://ai201-project2-fitfindr-starter-v2026-0nk2.onrender.com/health`
- Search endpoint: `https://ai201-project2-fitfindr-starter-v2026-0nk2.onrender.com/ask` (POST)

The home page should load the FitFindr interface. The health endpoint should return an `ok` response when the service is running.

## Run locally

### 1. Set up the environment

From the project directory, create and activate a virtual environment, install the requirements, and create your local environment file.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Add your `GEMINI_API_KEY` to `.env`. Keep this file private; do not commit API keys to Git.

Activate the virtual environment whenever you open a new terminal. You should see `(.venv)` in your prompt.

### 2. Start the HTTP server

```bash
python serve.py
```


The server starts on port `8080` by default and prints the local address it is listening on.

Start the server:

```bash
python serve.py
```

Keep this terminal open while you use the app. Open the local address printed by the server in your browser.

If your setup reads the `PORT` environment variable, you can explicitly choose a different port before starting the server:

```bash
PORT=8081 python serve.py
```

If you choose a different port, use that port in your browser address as well. On macOS, port `5000` can sometimes be occupied by AirPlay Receiver.

## Test the HTTP endpoints

Use a second terminal while the server is running.

### Health check

Open this address in a browser, or run:

```bash
curl -i http://127.0.0.1:8080/health
```

A successful response indicates that the web service is awake. This checks the server, not the full search-and-generation workflow.

### Submit a search

```bash
curl -i -X POST http://127.0.0.1:8080/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"vintage graphic tee under $30"}'
```

A successful request should return HTTP `200` and a JSON response containing the agent's result. The `wardrobe` field is optional; the endpoint accepts a JSON body with a `query` and, when needed, wardrobe information.

To test validation and the failure-logging path, submit an empty query:

```bash
curl -i -X POST http://127.0.0.1:8080/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":""}'
```

An empty query should return HTTP `400` with the message `Please enter a search query.` This failed request should also appear in the logs.

## Request logging and instrumentation

The Flask app logs every completed HTTP request as a JSON record. The logger writes the same record to two destinations:

- **Local file:** `fitfindr.log`, created in the working directory from which the server is started (normally the project root).
- **Standard output:** the server terminal locally, and Render Runtime Logs when deployed.

Each record includes:

| Field | Meaning |
|---|---|
| `timestamp` | UTC time when the request was logged |
| `method` and `path` | HTTP method and route, such as `POST` and `/ask` |
| `input` | Search query captured from the request, when present |
| `output` | A summary of the result or the response error |
| `duration_seconds` | End-to-end request duration, measured with `time.perf_counter()` |
| `status` | HTTP response status code, such as `200` or `400` |
| `error` | Error message when the request fails; otherwise `null` |
| `python_version` | Python version running the request |
| `platform` | Operating-system identifier, such as `Darwin` on macOS or `Linux` on Render |

The output summary for `/ask` includes information such as the selected listing, number of search results, whether an outfit suggestion and fit card were created, and any agent error. It does not need to store the entire page or response body to be useful.

### View local logs

Run these commands from the project directory in a second terminal:

```bash
# Show the most recent 20 log records
tail -n 20 fitfindr.log

# Follow new log records as requests arrive
tail -f fitfindr.log
```

Press `Ctrl+C` to stop following the file. Each line is a separate JSON record, so the file can also be inspected with a text editor or a small Python script.

The log file is created when the app handles its first request. If it is not present, confirm that the server is running and that you are checking the same project directory from which `serve.py` was started.

### View deployed logs on Render

1. Sign in to [Render](https://dashboard.render.com/).
2. Open the FitFindr **Web Service**.
3. Select **Logs** in the service navigation.
4. Open or filter to **Runtime Logs**.
5. Make a request to the deployed app, then refresh or watch the logs for the new JSON record.

The deployed app sends logs to standard output so Render can collect them. The local `fitfindr.log` file is not a durable log store on Render: files on a hosted service's local filesystem may be temporary and can disappear when the service restarts or redeploys. Use Render Runtime Logs to inspect deployed requests.

### Understanding request duration

`duration_seconds` measures the time from the beginning to the completion of the HTTP request. It is end-to-end request time, so it can include application work and waiting for external services; it is not a direct measure of API charges or pure CPU time. A first request can take longer than later requests due to initialization, caching, or external-service variability.

## Deploying / redeploying on Render

The FitFindr web service runs the Flask app through Gunicorn.

For a Render Web Service, the project configuration should use:

| Setting | Value |
|---|---|
| Runtime | Python |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn serve:app` |
| Environment variable | `GEMINI_API_KEY` — set the secret value in Render's Environment settings |

Do not put the API key directly in source code or in this document. After a deployment, open the service's public URL and check `/health`, then submit a search through the app or the `/ask` endpoint. Use Runtime Logs to confirm that requests are being recorded.

Keep the start command as `gunicorn serve:app`. The MCP client uses `asyncio.run()`, which is not compatible with a worker that already runs an event loop; do not switch to an async worker such as gevent/eventlet or wrap this app in an ASGI server without changing that design.

## Useful project commands

| Command | What it does |
|---|---|
| `python test.py` | Checks the local environment |
| `python app.py fields` | Displays listing and wardrobe fields |
| `python app.py listings --full -n 6` | Displays six complete listings |
| `python app.py examples` | Shows example search queries |
| `python app.py ask 'vintage graphic tee under $30'` | Runs the agent from the command line |
| `python serve.py` | Starts the HTTP server locally |
| `python mcp_server.py` | Starts the MCP server directly |
| `python mcp_client.py` | Checks what the MCP server offers |
| `python run_eval.py --label before` | Runs the evaluation scenarios and saves results |

## Troubleshooting

| What you see | What to check |
|---|---|
| `Address already in use` | Another process is using the port. Start the app on a different available port, such as `8080`, and use that port in your test commands. |
| `No GEMINI_API_KEY found` | Confirm that `.env` exists in the project root and contains `GEMINI_API_KEY=...`; on Render, set it in the service's Environment settings. |
| HTTP `400` from `/ask` | Check that the JSON body includes a non-empty `query`. An empty query is expected to return `400`. |
| HTTP `500` from `/ask` | Inspect the corresponding local log record or Render Runtime Logs for the error. |
| `[serve] another request is still running` | The server processes one request at a time; the next request waits for the current one. |
| `[rate limit] ... Waiting ...` | The model service is rate-limiting requests. The app's pacing is intentional; wait for it to continue. |
| Fit cards look identical | Check `CACHE_ENABLED` and `TEMPERATURE` near the top of `config.py`. Cached prompts can reuse previous answers while building. |
| The deployed app does not respond | Check the Render service status and Runtime Logs, then test `/health` before testing `/ask`. |

If something is still wrong, capture the command you ran, the HTTP status or full error, and the related log record before debugging further.

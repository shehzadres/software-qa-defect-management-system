# TaskFlow Local QA Target

TaskFlow is a small, locally authored project/task management web application used as the target under test for this QA portfolio.

## Run
From the repository root:

```powershell
python -m uvicorn application.app:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. API documentation: http://127.0.0.1:8765/docs.

## Synthetic accounts
The application source initializes controlled demo accounts. These credentials are synthetic and intended only for local testing. Inspect the account initialization in `app.py` before running; never expose real credentials or reuse these passwords.

## Data
The app writes its local runtime database to `data/taskflow_app.db`. This file is generated during execution and excluded from version control. The Playwright runner resets this local demo database before a test run.

## Automated checks
See the root README for environment installation and the full test-cycle commands. The runner starts its own server, executes browser/API/database assertions, writes JSON evidence and a screenshot, then shuts the server down.

# Software QA & Defect Management Portfolio

A practical software quality assurance portfolio built around **TaskFlow**, a locally authored project/task management application. The repository demonstrates requirements analysis, risk-based test design, manual test documentation, browser/API checks with Playwright, defect triage, Jira workflow documentation, SQL validation, and evidence-based reporting.

> **Scope and honesty note:** TaskFlow is a controlled portfolio demo, not a production service. The latest recorded local run executed 32 planned cases: 32 passed, 0 failed, 0 not run. Five defect records and their Jira issues are explicitly labelled as simulated training examples, not defects reproduced by that run.

## QA snapshot

| Measure | Recorded result |
|---|---:|
| Requirements | 10 |
| Designed test cases | 32 |
| Executed planned cases | 32 |
| Passed / failed / not run | 32 / 0 / 0 |
| Execution / pass rate | 100% / 100% |
| Seeded training defects | 5 |
| Requirements and test cases traced | 100% |

These figures describe the saved evidence in this repository. Re-run the suite to generate fresh results for your environment.

## Recruiter quick tour

Start with the visual report: **[QA Execution Dashboard](reports/qa-dashboard.html)**.

Then review:
- [Test plan](docs/TEST_PLAN.md) and [test strategy](docs/TEST_STRATEGY.md)
- [32 test cases](test-cases/test-cases.csv)
- [Live execution results](test-cases/live-execution-results.csv) and [raw JSON evidence](reports/live_execution_evidence.json)
- [Requirements traceability](requirements/requirements.csv)
- [Defect register](defects/defect-register.csv) and [defect lifecycle](docs/DEFECT_LIFECYCLE.md)
- [SQL schema](sql/schema.sql) and [report queries](sql/reports.sql)
- [Jira integration evidence](docs/JIRA_INTEGRATION.md)
- [Browser screenshot](reports/taskflow_dashboard_after_login.png)

## Project structure

```text
application/   FastAPI TaskFlow demo and Playwright runner
requirements/   Requirements catalogue
 test-cases/   Manual cases, execution results, exploratory notes
 defects/       Seeded training defect register and Jira import template
 docs/          Test plan, strategy, lifecycle, sign-offs, Jira notes
 reports/       Dashboard, screenshots, JSON and Markdown evidence
 sql/           QA database schema and reporting queries
 scripts/       Database build and validation utilities
```

## Quick start

Requires Python 3.10 or newer.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

Start the local demo:

```powershell
python -m uvicorn application.app:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. Interactive API documentation is available at http://127.0.0.1:8765/docs. Synthetic demo credentials and reset guidance are in [application README](application/README.md). Do not reuse these credentials outside this demo.

## Reproduce the QA run

In a second terminal, from the repository root:

```powershell
python application\run_live_checks.py
python application\publish_live_report.py
python scripts\build_database.py
python scripts\validate_project.py
```

The Playwright runner starts and stops its own local server. It writes fresh JSON evidence, a screenshot, and a CSV execution matrix. The report publisher derives the Markdown summary and case statuses from that evidence. The database builder recreates the separate QA evidence database from source CSV files.

The validation script checks CSV/database row counts, foreign-key integrity, and complete requirement/test-case traceability. A successful validation exits with code 0.

## What is tested

- Authentication success and failure, logout, session behavior, and browser back navigation
- Project and task creation, duplicate/blank input, title boundaries, editing and deletion
- Project membership, cross-user access control, and assignment authorization
- Valid and invalid task status transitions
- Comments, blank input, and idempotent repeated submissions
- Search behavior, special characters, and empty search
- SQLite foreign-key enforcement and cascading deletion

The runner combines real Chromium browser interactions with HTTP/API assertions and direct database integrity checks. **It is not accurate to describe all 32 cases as end-to-end browser UI tests.**

## Jira

The Jira workspace/project and five Bug issues are documented in [Jira integration evidence](docs/JIRA_INTEGRATION.md). All five are simulated training examples, clearly labelled as such. The project does not claim those issues were reproduced in the live local run. See [Jira setup and import precautions](docs/JIRA_SETUP.md) before importing anything.

## Evidence boundaries

- The saved 32/32 result is a local portfolio test-cycle result, not a production release approval.
- Seeded defect records are training examples, not live findings.
- The project has not undergone an independent penetration test, load test, or production security review.
- The dashboard is a static snapshot generated from the committed evidence; rerun the suite and report publisher to refresh execution artifacts.

## License

Released under the MIT License. See [LICENSE](LICENSE).

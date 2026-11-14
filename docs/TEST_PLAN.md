# Test Plan: TaskFlow 1.4

**ID:** TF-QA-TP-014 | **Version:** 1.1 | **Target:** Locally authored TaskFlow portfolio application

## Objective and scope
Validate authentication, authorization, project and task management, assignment, status transitions, comments, search, session behavior, and data integrity. Payment, external email delivery, native mobile, load testing, penetration testing, and production migration are out of scope.

## Approach
Risk-based test design combines positive and negative functional testing, equivalence partitioning, boundary-value analysis, role/action/ownership decision tables, state-transition testing, critical-path regression, exploratory testing, and SQL persistence/integrity checks.

## Environment
TaskFlow local demo, Python/FastAPI, SQLite, Chromium via Playwright, synthetic accounts and data. The runner launches the target on 127.0.0.1:8765. Exact runtime versions depend on the machine and are installed from the root requirements file.

## Entry criteria
Requirements and acceptance criteria are baselined; source and environment are available; synthetic test data is ready; critical workflows can be started; defect severity/priority definitions are agreed.

## Exit criteria
The planned portfolio cycle requires all P1 cases to be executed, at least 95% overall execution and pass rate, no unaccepted Critical/High live defects, full requirements traceability, and every failed case linked to a defect or documented waiver. These are proposed QA gates, not proof of production release approval.

## Severity and priority
Severity: Critical (security breach, major data loss, outage), High (core workflow unusable), Medium (degraded with workaround), Low (cosmetic). Priority: P0 immediate release stop, P1 fix before release, P2 planned iteration, P3 backlog. Severity and priority are distinct.

## Risks and mitigations
Authorization gaps may expose private data; use cross-user negative checks. Invalid state transitions may corrupt workflow; exercise the transition matrix. Search filtering may leak records; test ownership and special characters. Persistence errors may lose work; verify reload and SQL integrity. Regression gaps may reintroduce defects; rerun critical journeys.

## Deliverables
Requirements catalogue, test cases, execution matrix, exploratory notes, seeded training defect register, traceability, SQL evidence database, JSON/Markdown report, dashboard, screenshot, and portfolio sign-off.

## Execution status
The committed evidence records 32 planned cases, 32 executed, 32 passed, 0 failed, and 0 not run. The runner uses Chromium for selected browser interactions and HTTP/API plus database assertions for other checks. See `reports/LIVE_EXECUTION_SUMMARY.md` and the raw JSON evidence.

## Limitations
This is a locally authored demonstration target. Results are not evidence of testing a third-party product or production deployment. No independent security certification or load test is claimed.

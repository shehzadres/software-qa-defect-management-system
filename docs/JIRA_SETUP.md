# Jira Workspace Setup and Import Procedure

## Current integration state
A Jira Cloud project named **SQA Portfolio** (key **SP**) and five Bug issues are documented in [JIRA_INTEGRATION.md](JIRA_INTEGRATION.md). The issues are simulated training examples only. This setup guide is retained for reproducibility and future sandbox work; it is not evidence that the project is currently connected to an integration session.

## Verify access before changes
1. Sign in to the intended Atlassian site.
2. Confirm the SQA Portfolio project and project key SP are accessible.
3. Confirm permission to create and edit issues.
4. Verify available issue types, priorities, components, and workflow statuses before import.

## Import precautions
- Do not present `defects/defect-register.csv` records as live defects. They are seeded training examples.
- `defects/jira-import-template.csv` is illustrative. Replace sample content only with independently reproduced findings.
- Map issue type, summary, description, priority, labels, component, assignee, and environment to fields available in the destination project.
- Verify status and priority mappings after import.
- Link genuine findings to their requirement and test case; retain the Jira issue key in the defect register.

## Acceptance evidence
For any future import, capture the project key, created issue keys, workflow transitions, and links. Never claim an issue was created, attached, fixed, or verified without checking the Jira record itself.

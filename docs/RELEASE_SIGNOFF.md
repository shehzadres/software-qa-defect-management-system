# Release Sign-off: TaskFlow 1.4

**Artifact:** Historical simulated release-candidate exercise
**Decision in this exercise:** HOLD / NOT APPROVED

This document represents a separate simulated release-gate exercise using seeded training risk/defect data. It must not be read as the outcome of the later local execution run.

For the latest local portfolio test-cycle result, see [LOCAL_TARGET_SIGNOFF.md](LOCAL_TARGET_SIGNOFF.md). That run recorded 32/32 planned cases passing, but it is not production release approval.

## Example release gates
- P1 cases executed: 100% required.
- Overall execution: at least 95%.
- Pass rate: at least 95%.
- Open Critical/High live defects: zero unless risk-accepted.
- Requirements traceability: 100%.
- Every failed case linked to a defect or waiver.
- QA Lead and Product Owner approval.

## Reconsideration conditions
Resolve or formally waive Critical/High live defects; retest failures against a stable candidate; execute critical-path regression; verify authorization and SQL integrity; recalculate metrics from observed evidence; obtain required approvals.

## Simulation boundary
The historical seeded defects are training examples, not findings from the latest local run. This exercise is not a real production release authorization.

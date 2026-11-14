# QA Test Strategy
**Risk tiers:** P1 authentication, authorization, data loss and destructive actions; P2 projects, assignment, workflow, comments and search; P3 cosmetic/empty-state behavior.

**Design techniques:** equivalence partitions; boundary values; role × action × ownership decision tables; state transition testing; error guessing (double submit, stale session, special characters, refresh during edit).

**Types:** functional, negative, boundary, regression, exploratory, authorization and data integrity.

**Lifecycle:** New → Triaged → Assigned → In Progress → Fixed → Ready for Retest → Retest Passed → Closed. Failed retest reopens to Assigned. Rejected, Duplicate and Deferred require rationale.

**Metrics:** execution rate = executed/planned × 100; pass rate = passed/executed × 100. Do not claim escaped-defect rate or defect density without real release data and a valid denominator.

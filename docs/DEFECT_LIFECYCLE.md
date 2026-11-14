# Defect Lifecycle & Triage
**Workflow:** New → Triaged → Assigned → In Progress → Fixed → Ready for Retest → Retest Passed → Closed. Failed retest → Reopened → Assigned. Alternatives: Rejected, Duplicate, Deferred, Cannot Reproduce; rationale is mandatory.

**Severity:** Critical = breach/data loss/outage; High = core workflow unusable; Medium = impaired with workaround; Low = cosmetic.
**Priority:** P0 release stop; P1 before release; P2 planned iteration; P3 backlog.

**Required fields:** summary, build/environment, preconditions, reproducible steps, expected/actual, frequency, severity, priority, component, reporter, owner, evidence, requirement/test links, status and resolution.

**Example triage targets:** Critical immediate; High same business day; Medium within 2 business days; Low within 5 business days. These are illustrative team SLAs.

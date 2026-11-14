import sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
con=sqlite3.connect(ROOT/"data"/"qa_management.db")
counts=dict(con.execute("SELECT status,COUNT(*) FROM test_executions GROUP BY status").fetchall())
total=sum(counts.values()); executed=total-counts.get("Not Run",0); passed=counts.get("Passed",0)
execution=100*executed/total if total else 0
passrate=100*passed/executed if executed else 0
open_risks=con.execute("SELECT defect_id,severity,priority,status,summary FROM defects WHERE severity IN ('Critical','High') AND status NOT IN ('Closed','Rejected','Duplicate')").fetchall()
reqs=con.execute("SELECT COUNT(*) FROM requirements").fetchone()[0]
covered=con.execute("SELECT COUNT(DISTINCT requirement_id) FROM traceability").fetchone()[0]
lines=["# Test Execution Summary - TaskFlow 1.4","", "**Build:** TF-1.4.0-rc2 | **Environment:** QA staging simulation | **Cycle:** Simulated", "",
"## Execution metrics","",f"- Planned cases: **{total}**",f"- Executed: **{executed}**",f"- Passed: **{passed}**",f"- Failed: **{counts.get('Failed',0)}**",f"- Blocked: **{counts.get('Blocked',0)}**",f"- Not run: **{counts.get('Not Run',0)}**",f"- Execution rate: **{execution:.1f}%**",f"- Pass rate of executed: **{passrate:.1f}%**","", "## Open Critical / High defects",""]
for d in open_risks: lines.append(f"- **{d[0]}** ({d[1]}, {d[2]}, {d[3]}): {d[4]}")
lines += ["",f"## Traceability","",f"- Requirements covered: {covered}/{reqs} ({100*covered/reqs:.1f}%)","", "## QA recommendation","", "**HOLD / NOT APPROVED.** The simulated cycle contains failed cases and unresolved Critical/High risk. Resolve or formally accept risk, retest, run regression and obtain QA/Product approval before release.", "","> All data is simulated. This report is not evidence of testing a live application."]
out=ROOT/"reports"/"TEST_EXECUTION_SUMMARY.md"; out.write_text("\n".join(lines),encoding="utf-8")
print(out.read_text(encoding="utf-8"))
con.close()

import csv, json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
evidence=json.loads((ROOT/"reports"/"live_execution_evidence.json").read_text(encoding="utf-8"))
with (ROOT/"test-cases"/"test-cases.csv").open(encoding="utf-8-sig",newline="") as f:
    cases=list(csv.DictReader(f))
mapped={x["case"]:x for x in evidence["results"] if x["case"].startswith("TC-") and x["case"]!="TC-001-B"}
stamp=datetime.now(timezone.utc).isoformat()
out=[]
for c in cases:
    result=mapped.get(c["test_case_id"])
    out.append({"test_case_id":c["test_case_id"],"requirement_id":c["requirement_id"],"title":c["title"],"live_status":result["result"] if result else "Not Run","actual_evidence":result["detail"] if result else "Not executed in this run","build":"TaskFlow local QA target 1.4","executed_at_utc":stamp if result else ""})
with (ROOT/"test-cases"/"live-execution-results.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
planned=len(out); executed=sum(x["live_status"]!="Not Run" for x in out); passed=sum(x["live_status"]=="PASS" for x in out); failed=sum(x["live_status"]=="FAIL" for x in out); notrun=planned-executed
supp=[x for x in evidence["results"] if x["case"].startswith("SUP-") or x["case"]=="TC-001-B"]
lines=["# Live Execution Summary - TaskFlow Local QA Target","",f"**Report generated (UTC):** {stamp}","**Target:** Locally hosted TaskFlow QA application","**Build:** TaskFlow local QA target 1.4","**Runner:** Playwright Chromium, browser UI interactions and HTTP workflow assertions","","## Planned test case metrics","",f"- Planned: **{planned}**",f"- Executed: **{executed}**",f"- Passed: **{passed}**",f"- Failed: **{failed}**",f"- Not run: **{notrun}**",f"- Execution rate: **{executed/planned*100:.1f}%**",f"- Pass rate of executed cases: **{passed/executed*100 if executed else 0:.1f}%**","","## Supplemental checks",""]
for x in supp: lines.append(f"- **{x['case']}**: {x['result']} - {x['detail']}")
lines += ["","## Unexecuted planned cases",""]
for x in out:
    if x["live_status"]=="Not Run": lines.append(f"- {x['test_case_id']}: {x['title']}")
lines += ["","## Defect outcome","",f"No defects were reproduced in the {executed} mapped cases executed during this local run. The separate seeded examples in `defects/defect-register.csv` remain training data and must not be represented as live findings.","","## Recommendation",""]
if executed==planned and failed==0:
    lines.append("**FULL LOCAL QA SUITE: PASS.** All planned test cases executed successfully against the local TaskFlow target. This is a portfolio test-cycle sign-off only, not production release approval or independent security certification.")
else:
    lines.append("**QA RESULT: INCOMPLETE / HOLD.** Complete outstanding tests and investigate failures before sign-off.")
lines += ["","## Evidence files","","- `reports/live_execution_evidence.json`: per-check evidence and outcomes.","- `reports/taskflow_dashboard_after_login.png`: browser screenshot.","- `test-cases/live-execution-results.csv`: status for all planned cases.","- `data/taskflow_app.db`: application database from the run.","","All outcomes are observed local execution evidence. TaskFlow is a controlled portfolio target, not a third-party production system."]
(ROOT/"reports"/"LIVE_EXECUTION_SUMMARY.md").write_text("\n".join(lines),encoding="utf-8")
print("\n".join(lines))

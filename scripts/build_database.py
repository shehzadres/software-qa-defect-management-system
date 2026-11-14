import csv, sqlite3
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "qa_management.db"
def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
if DB.exists(): DB.unlink()
con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys=ON")
con.executescript((ROOT/"sql"/"schema.sql").read_text(encoding="utf-8"))
for x in rows(ROOT/"requirements"/"requirements.csv"):
    con.execute("INSERT INTO requirements VALUES(?,?,?,?,?)", tuple(x[k] for k in ["requirement_id","title","description","priority","acceptance_criteria"]))
cases = rows(ROOT/"test-cases"/"test-cases.csv")
for x in cases:
    con.execute("INSERT INTO test_cases VALUES(?,?,?,?,?,?,?,?,?)", tuple(x[k] for k in ["test_case_id","requirement_id","title","test_type","priority","preconditions","steps","test_data","expected_result"]))
    con.execute("INSERT INTO traceability VALUES(?,?)",(x["requirement_id"],x["test_case_id"]))
defects = rows(ROOT/"defects"/"defect-register.csv")
for x in defects:
    con.execute("INSERT INTO defects VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(x[k] for k in ["defect_id","summary","requirement_id","severity","priority","status","component","environment","build","steps_to_reproduce","expected_result","actual_result","assignee","evidence_ref","resolution"]))
    con.execute("INSERT INTO defect_history(defect_id,from_status,to_status,changed_by,changed_at,comment) VALUES(?,?,?,?,?,?)",(x["defect_id"],None,"New","QA Engineer",datetime.now(timezone.utc).isoformat(),"Initial defect created in simulated QA cycle"))
    if x["status"] != "New":
        con.execute("INSERT INTO defect_history(defect_id,from_status,to_status,changed_by,changed_at,comment) VALUES(?,?,?,?,?,?)",(x["defect_id"],"New",x["status"],"QA Lead",datetime.now(timezone.utc).isoformat(),"Simulated lifecycle transition"))
now = datetime.now(timezone.utc).isoformat()
for x in cases:
    con.execute("INSERT INTO test_executions(test_case_id,build,environment,executed_by,executed_at,status,actual_result,defect_id) VALUES(?,?,?,?,?,?,?,?)",(x["test_case_id"],"TF-1.4.0-rc2","QA staging simulation","QA Engineer",now,x["status"],x["actual_result"],x["defect_id"] or None))
live_path=ROOT/"test-cases"/"live-execution-results.csv"
if live_path.exists():
    for x in rows(live_path):
        con.execute("INSERT INTO live_test_executions(test_case_id,build,environment,executed_at,status,actual_evidence) VALUES(?,?,?,?,?,?)",(x["test_case_id"],x["build"],"Local TaskFlow QA target",x["executed_at_utc"],x["live_status"],x["actual_evidence"]))
con.commit()
print(f"Database created: {DB}")
for table in ["requirements","test_cases","test_executions","live_test_executions","defects","defect_history","traceability"]:
    print(f"{table}: {con.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]}")
con.close()

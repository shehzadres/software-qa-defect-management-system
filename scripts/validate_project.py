import csv, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def count_csv(p):
    with p.open(encoding="utf-8-sig",newline="") as f: return len(list(csv.DictReader(f)))
db=ROOT/"data"/"qa_management.db"
if not db.exists():
    print("FAIL: database missing. Run scripts/build_database.py first."); sys.exit(1)
con=sqlite3.connect(db); con.execute("PRAGMA foreign_keys=ON")
checks=[]
for table, file in [("requirements","requirements/requirements.csv"),("test_cases","test-cases/test-cases.csv"),("defects","defects/defect-register.csv"),("live_test_executions","test-cases/live-execution-results.csv")]:
    if not (ROOT/file).exists(): continue
    actual=con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    expected=count_csv(ROOT/file)
    checks.append((f"{table} row count",actual==expected,f"{actual} / {expected}"))
fk=con.execute("PRAGMA foreign_key_check").fetchall()
checks.append(("foreign key integrity",len(fk)==0,str(fk)))
missing=con.execute("""SELECT requirement_id FROM requirements r WHERE NOT EXISTS
(SELECT 1 FROM traceability t WHERE t.requirement_id=r.requirement_id)""").fetchall()
checks.append(("all requirements traced",len(missing)==0,str(missing)))
unlinked=con.execute("""SELECT test_case_id FROM test_cases c WHERE NOT EXISTS
(SELECT 1 FROM traceability t WHERE t.test_case_id=c.test_case_id)""").fetchall()
checks.append(("all test cases traced",len(unlinked)==0,str(unlinked)))
for name,ok,detail in checks: print(("PASS" if ok else "FAIL")+f" | {name} | {detail}")
con.close()
sys.exit(0 if all(x[1] for x in checks) else 1)

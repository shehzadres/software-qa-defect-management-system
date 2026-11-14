import json, os, socket, subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
APP_DB=ROOT/"data"/"taskflow_app.db"
EVIDENCE=ROOT/"reports"/"live_execution_evidence.json"
if APP_DB.exists(): APP_DB.unlink()
with socket.socket() as port_socket:
    port_socket.bind(("127.0.0.1", 0))
    port = port_socket.getsockname()[1]
server=subprocess.Popen([sys.executable,"-m","uvicorn","application.app:app","--host","127.0.0.1","--port",str(port)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
base=f"http://127.0.0.1:{port}"
for _ in range(50):
    try:
        urllib.request.urlopen(base,timeout=1); break
    except Exception: time.sleep(.2)
else:
    server.terminate(); raise RuntimeError("TaskFlow app failed to start")

results=[]
def record(case,passed,detail):
    results.append({"case":case,"result":"PASS" if passed else "FAIL","detail":str(detail)})
def expect(case, condition, detail):
    record(case,bool(condition),detail)
try:
  with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    alice=browser.new_context()
    page=alice.new_page()
    page.goto(base)
    page.get_by_label("Email").fill("alice@taskflow.test")
    page.get_by_label("Password").fill("wrong-password")
    page.get_by_role("button",name="Sign in").click()
    page.wait_for_timeout(150)
    expect("TC-002", "Invalid email or password" in page.locator("#message").inner_text(), page.locator("#message").inner_text())
    page.get_by_label("Password").fill("Alice-QA-2026!")
    page.get_by_role("button",name="Sign in").click()
    page.wait_for_selector("#app",state="visible")
    expect("TC-001", "Projects" in page.locator("#app").inner_text(), "Authenticated dashboard rendered")
    page.locator("#projectName").fill("UI Smoke Project")
    page.get_by_role("button",name="Create project").click()
    page.get_by_role("button",name="UI Smoke Project").wait_for()
    expect("SUP-UI-01", "Project created" in page.locator("#notice").inner_text(), "Project created from browser UI")
    page.get_by_role("button",name="UI Smoke Project").click()
    page.locator("#taskTitle").fill("UI-created task")
    page.get_by_role("button",name="Add task").click()
    page.get_by_text("UI-created task").wait_for()
    expect("SUP-UI-02", "UI-created task" in page.locator("#tasks").inner_text(), "Task created and rendered in browser UI")
    r=alice.request.post(base+"/api/projects",data={"name":"Release QA"})
    expect("TC-005",r.status==200 and r.json()["name"]=="Release QA",f"HTTP {r.status}: {r.text()}")
    project_id=r.json()["id"]
    dup=alice.request.post(base+"/api/projects",data={"name":"Release QA"})
    expect("TC-007",dup.status==409,f"Duplicate project returned HTTP {dup.status}")
    blank=alice.request.post(base+"/api/projects",data={"name":"   "})
    expect("TC-006",blank.status==422,f"Blank project returned HTTP {blank.status}")
    task=alice.request.post(f"{base}/api/projects/{project_id}/tasks",data={"title":"Prepare release notes"})
    expect("TC-010",task.status==200,f"Task create HTTP {task.status}")
    task_id=task.json()["id"]
    blank_task=alice.request.post(f"{base}/api/projects/{project_id}/tasks",data={"title":""})
    expect("TC-011",blank_task.status==422,f"Empty task title HTTP {blank_task.status}")
    max_title="T"*120
    maxr=alice.request.post(f"{base}/api/projects/{project_id}/tasks",data={"title":max_title})
    expect("TC-012",maxr.status==200 and len(maxr.json()["title"])==120,f"120 char title HTTP {maxr.status}")
    over=alice.request.post(f"{base}/api/projects/{project_id}/tasks",data={"title":"T"*121})
    expect("TC-013",over.status==422,f"121 char title HTTP {over.status}")
    direct=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"status":"Done"})
    expect("TC-019",direct.status==409,f"Direct To Do > Done HTTP {direct.status}")
    step1=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"status":"In Progress"})
    step2=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"status":"Done"})
    expect("TC-018",step1.status==200 and step2.status==200,f"Sequential transitions HTTP {step1.status}/{step2.status}")
    comment_body={"body":"Ready for review","idempotency_key":"qa-comment-001"}
    c1=alice.request.post(f"{base}/api/tasks/{task_id}/comments",data=comment_body)
    c2=alice.request.post(f"{base}/api/tasks/{task_id}/comments",data=comment_body)
    comments=alice.request.get(f"{base}/api/tasks/{task_id}/comments").json()
    expect("TC-028",c1.status==200 and c2.status==200 and len(comments)==1,f"Repeated request yielded {len(comments)} stored comment(s)")
    search=alice.request.get(base+"/api/tasks",params={"search":"release"})
    expect("TC-023",search.status==200 and any("release" in t["title"].lower() for t in search.json()),f"Search returned {len(search.json())} result(s)")
    empty_search=alice.request.get(base+"/api/tasks",params={"search":""})
    expect("TC-032",empty_search.status==200 and len(empty_search.json())>=1,f"Empty search returned HTTP {empty_search.status} with {len(empty_search.json())} visible tasks")
    bob=browser.new_context()
    br=bob.request.post(base+"/api/login",data={"email":"bob@taskflow.test","password":"Bob-QA-2026!"})
    expect("TC-001-B",br.status==200,"Second user authenticated")
    outsider=bob.request.get(f"{base}/api/projects/{project_id}")
    expect("TC-008",outsider.status==404,f"Outsider project read HTTP {outsider.status}")
    outsider_tasks=bob.request.get(base+"/api/tasks",params={"search":"Prepare release notes"})
    expect("TC-024",outsider_tasks.status==200 and len(outsider_tasks.json())==0,f"Outsider search result count {len(outsider_tasks.json())}")
    outsider_create=bob.request.post(f"{base}/api/projects/{project_id}/tasks",data={"title":"Unauthorized task"})
    expect("TC-009",outsider_create.status==404,f"Outsider project mutation HTTP {outsider_create.status}")
    edit=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"title":"Release notes reviewed"})
    after_edit=alice.request.get(base+"/api/tasks",params={"project_id":project_id})
    expect("TC-014",edit.status==200 and any(t["title"]=="Release notes reviewed" for t in after_edit.json()),f"Edit HTTP {edit.status}; reload confirmed")
    page.reload()
    page.wait_for_selector("#app",state="visible")
    page.get_by_role("button",name="Release QA").click()
    page.get_by_text("Release notes reviewed").wait_for()
    expect("TC-029","Release notes reviewed" in page.locator("#tasks").inner_text(),"Edited task remained visible after browser navigation and reload")
    outsider_edit=bob.request.patch(f"{base}/api/tasks/{task_id}",data={"title":"Intruder edit"})
    expect("TC-015",outsider_edit.status==404,f"Outsider task edit HTTP {outsider_edit.status}")
    nonmember_assign=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"assignee_email":"bob@taskflow.test"})
    expect("TC-017",nonmember_assign.status==422,f"Non-member assignment HTTP {nonmember_assign.status}")
    add_member=alice.request.post(f"{base}/api/projects/{project_id}/members",data={"email":"bob@taskflow.test"})
    assign_member=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"assignee_email":"bob@taskflow.test"})
    expect("TC-016",add_member.status==200 and assign_member.status==200 and assign_member.json()["assignee_id"]==add_member.json()["user_id"],f"Add member HTTP {add_member.status}; assignment HTTP {assign_member.status}")
    invalid_status=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"status":"Archived"})
    expect("TC-020",invalid_status.status==409,f"Unknown status HTTP {invalid_status.status}")
    valid_comment=alice.request.post(f"{base}/api/tasks/{task_id}/comments",data={"body":"QA reviewed","idempotency_key":"qa-comment-002"})
    expect("TC-021",valid_comment.status==200,f"Comment create HTTP {valid_comment.status}")
    blank_comment=alice.request.post(f"{base}/api/tasks/{task_id}/comments",data={"body":"   ","idempotency_key":"qa-comment-blank"})
    expect("TC-022",blank_comment.status==422,f"Blank comment HTTP {blank_comment.status}")
    special_search=alice.request.get(base+"/api/tasks",params={"search":"' OR * %"})
    expect("TC-025",special_search.status==200,f"Special-character search HTTP {special_search.status}")
    assign_self=alice.request.patch(f"{base}/api/tasks/{task_id}",data={"assignee_email":"alice@taskflow.test"})
    expect("TC-031",assign_self.status==200 and assign_self.json()["assignee_id"] is not None,f"Assign to member HTTP {assign_self.status}")
    # Test a separate session expiry after explicitly logging Bob out.
    bob_logout=bob.request.post(base+"/api/logout",data={})
    bob_me=bob.request.get(base+"/api/me")
    expect("TC-004",bob_logout.status==200 and bob_me.status==401,f"Expired/logged-out session /me HTTP {bob_me.status}")
    # Verify relational cascade using a disposable project and its child records.
    temp=alice.request.post(base+"/api/projects",data={"name":"Cascade QA"})
    temp_id=temp.json()["id"]
    temp_task=alice.request.post(f"{base}/api/projects/{temp_id}/tasks",data={"title":"Child record"})
    delr=alice.request.delete(f"{base}/api/projects/{temp_id}")
    import sqlite3
    con=sqlite3.connect(APP_DB)
    remaining=con.execute("SELECT COUNT(*) FROM tasks WHERE id=?",(temp_task.json()["id"],)).fetchone()[0]
    con.close()
    expect("TC-026",delr.status==200 and remaining==0,f"Delete HTTP {delr.status}; remaining child tasks {remaining}")
    # Check FK enforcement directly against the application database.
    con=sqlite3.connect(APP_DB); con.execute("PRAGMA foreign_keys=ON")
    try:
        con.execute("INSERT INTO tasks(project_id,title) VALUES(999999,'Orphan')")
        fk_rejected=False
    except sqlite3.IntegrityError:
        fk_rejected=True
    con.close()
    expect("TC-027",fk_rejected,"Orphan task insert rejected by SQLite foreign key")
    # Remove the deliberately long boundary-value fixture before capturing recruiter-facing UI evidence.
    con=sqlite3.connect(APP_DB)
    con.execute("DELETE FROM tasks WHERE length(title)>80")
    con.commit()
    con.close()
    page.reload()
    page.wait_for_selector("#app",state="visible")
    page.screenshot(path=str(ROOT/"reports"/"taskflow_dashboard_after_login.png"),full_page=True)
    page.goto(base+"/?history=1")
    page.wait_for_selector("#app",state="visible")
    page.get_by_role("button",name="Sign out").click()
    page.wait_for_selector("#login",state="visible")
    page.go_back()
    page.wait_for_selector("#login",state="visible")
    expect("TC-030",page.locator("#login").is_visible() and page.locator("#app").is_hidden(),"Browser back after logout did not restore protected dashboard")
    me=alice.request.get(base+"/api/me")
    expect("TC-003",me.status==401,f"After UI logout /me HTTP {me.status}")
    bob.close(); alice.close(); browser.close()
finally:
  server.terminate()
  try: server.wait(timeout=5)
  except: server.kill()
EVIDENCE.write_text(json.dumps({"target":"TaskFlow local QA target","base_url":base,"run_type":"Playwright browser + HTTP workflow checks","simulated":False,"results":results,"passed":sum(x["result"]=="PASS" for x in results),"failed":sum(x["result"]=="FAIL" for x in results)},indent=2),encoding="utf-8")
print(json.dumps({"passed":sum(x["result"]=="PASS" for x in results),"failed":sum(x["result"]=="FAIL" for x in results),"results":results},indent=2))
if any(x["result"]=="FAIL" for x in results): sys.exit(1)

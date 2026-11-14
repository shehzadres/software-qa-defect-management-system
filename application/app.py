from fastapi import FastAPI, Request, HTTPException, Response, Cookie
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import sqlite3, uuid, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "taskflow_app.db"
app = FastAPI(title="TaskFlow QA Target", version="1.4.0")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con=db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, owner_id INTEGER NOT NULL REFERENCES users(id), is_private INTEGER NOT NULL DEFAULT 1);
    CREATE TABLE IF NOT EXISTS memberships(project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, PRIMARY KEY(project_id,user_id));
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE, title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 120), description TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'To Do' CHECK(status IN ('To Do','In Progress','Done')), assignee_id INTEGER REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE, author_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL CHECK(length(trim(body))>0), idempotency_key TEXT UNIQUE NOT NULL);
    """)
    for email,pw in [("alice@taskflow.test","Alice-QA-2026!"),("bob@taskflow.test","Bob-QA-2026!")]:
        con.execute("INSERT OR IGNORE INTO users(email,password_hash) VALUES(?,?)",(email,hashlib.sha256(pw.encode()).hexdigest()))
    con.commit(); con.close()

@app.on_event("startup")
def startup(): init_db()

def current_user(session: str | None):
    if not session: raise HTTPException(401,"Authentication required")
    con=db(); row=con.execute("SELECT u.id,u.email FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?",(session,)).fetchone(); con.close()
    if not row: raise HTTPException(401,"Session expired")
    return row

def project_access(con, project_id, user_id):
    return con.execute("SELECT 1 FROM memberships WHERE project_id=? AND user_id=?",(project_id,user_id)).fetchone() is not None

class Credentials(BaseModel):
    email: str
    password: str
class ProjectInput(BaseModel):
    name: str = Field(min_length=1,max_length=80)
class MemberInput(BaseModel):
    email: str
class TaskInput(BaseModel):
    title: str = Field(min_length=1,max_length=120)
    description: str = ""
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None,min_length=1,max_length=120)
    status: str | None = None
    assignee_email: str | None = None
class CommentInput(BaseModel):
    body: str = Field(min_length=1,max_length=1000)
    idempotency_key: str

@app.get("/",response_class=HTMLResponse)
def home():
    return HTMLResponse("""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>TaskFlow QA Target</title><style>
    body{font:16px/1.5 Arial,sans-serif;background:#f4f6f8;color:#18212b;margin:0}.wrap{max-width:850px;margin:48px auto;padding:24px}.panel{background:white;border:1px solid #dce2e8;border-radius:12px;padding:24px;margin:16px 0}input,button,textarea,select{font:inherit;padding:10px;margin:5px 0;border:1px solid #b9c4cf;border-radius:6px}button{background:#234f72;color:white;cursor:pointer}li{padding:8px;border-bottom:1px solid #eee}.muted{color:#596875}#app{display:none}.row{display:flex;gap:8px;flex-wrap:wrap}</style></head><body><main class='wrap'>
    <h1>TaskFlow</h1><p class='muted'>QA target application · Release 1.4</p>
    <section id='login' class='panel'><h2>Sign in</h2><input id='email' aria-label='Email' placeholder='Email' value='alice@taskflow.test'><br><input id='password' aria-label='Password' type='password' placeholder='Password' value='Alice-QA-2026!'><br><button id='loginBtn'>Sign in</button><p id='message' role='status'></p><small>QA fixtures: alice@taskflow.test / Alice-QA-2026! · bob@taskflow.test / Bob-QA-2026!</small></section>
    <section id='app' class='panel'><div class='row'><h2>Projects</h2><button id='logoutBtn'>Sign out</button></div><div class='row'><input id='projectName' placeholder='New project name'><button id='createProject'>Create project</button></div><ul id='projects'></ul><h2>Tasks</h2><div class='row'><input id='taskTitle' placeholder='Task title'><button id='createTask'>Add task</button></div><div class='row'><input id='search' placeholder='Search visible tasks'><button id='searchBtn'>Search</button></div><ul id='tasks'></ul><p id='notice' role='status'></p></section></main>
    <script>
    let projectId=null,taskId=null;
    async function api(path,method='GET',body){const r=await fetch(path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});let d={};try{d=await r.json()}catch{}if(!r.ok)throw Error(d.detail||'Request failed');return d}
    async function load(){try{const d=await api('/api/projects');document.querySelector('#projects').innerHTML='';d.forEach(p=>{const li=document.createElement('li');const b=document.createElement('button');b.textContent=p.name;b.onclick=()=>{projectId=p.id;loadTasks()};li.append(b);document.querySelector('#projects').append(li)});document.querySelector('#login').style.display='none';document.querySelector('#app').style.display='block'}catch{document.querySelector('#login').style.display='block'}}
    async function loadTasks(){const d=await api('/api/tasks'+(projectId?'?project_id='+projectId:''));document.querySelector('#tasks').innerHTML='';d.forEach(t=>{const li=document.createElement('li');li.textContent=t.title+' · '+t.status;document.querySelector('#tasks').append(li)})}
    document.querySelector('#loginBtn').onclick=async()=>{try{await api('/api/login','POST',{email:email.value,password:password.value});message.textContent='Signed in';await load()}catch(e){message.textContent=e.message}};
    document.querySelector('#logoutBtn').onclick=async()=>{await api('/api/logout','POST',{});location.reload()};
    document.querySelector('#createProject').onclick=async()=>{try{const p=await api('/api/projects','POST',{name:projectName.value});projectId=p.id;notice.textContent='Project created';await load()}catch(e){notice.textContent=e.message}};
    document.querySelector('#createTask').onclick=async()=>{try{if(!projectId)throw Error('Select a project first');const t=await api('/api/projects/'+projectId+'/tasks','POST',{title:taskTitle.value});taskId=t.id;notice.textContent='Task created';await loadTasks()}catch(e){notice.textContent=e.message}};
    document.querySelector('#searchBtn').onclick=async()=>{try{const d=await api('/api/tasks?search='+encodeURIComponent(search.value));tasks.innerHTML='';d.forEach(t=>{const li=document.createElement('li');li.textContent=t.title+' · '+t.status;tasks.append(li)})}catch(e){notice.textContent=e.message}};
    load();
    </script></body></html>""")

@app.post("/api/login")
def login(payload: Credentials, response: Response):
    con=db(); row=con.execute("SELECT * FROM users WHERE email=?",(payload.email.lower(),)).fetchone()
    if not row or row["password_hash"]!=hashlib.sha256(payload.password.encode()).hexdigest():
        con.close(); raise HTTPException(401,"Invalid email or password")
    token=uuid.uuid4().hex; con.execute("INSERT INTO sessions VALUES(?,?)",(token,row["id"])); con.commit(); con.close()
    response.set_cookie("session",token,httponly=True,samesite="lax")
    return {"email":row["email"]}

@app.post("/api/logout")
def logout(response: Response, session: str | None=Cookie(default=None)):
    con=db()
    if session: con.execute("DELETE FROM sessions WHERE token=?",(session,))
    con.commit(); con.close(); response.delete_cookie("session")
    return {"logged_out":True}

@app.get("/api/me")
def me(session: str | None=Cookie(default=None)):
    u=current_user(session); return {"id":u["id"],"email":u["email"]}

@app.get("/api/projects")
def list_projects(session: str | None=Cookie(default=None)):
    u=current_user(session); con=db()
    rows=con.execute("SELECT p.id,p.name FROM projects p JOIN memberships m ON m.project_id=p.id WHERE m.user_id=? ORDER BY p.id",(u["id"],)).fetchall(); con.close()
    return [dict(x) for x in rows]

@app.post("/api/projects")
def create_project(payload: ProjectInput, session: str | None=Cookie(default=None)):
    u=current_user(session); name=payload.name.strip()
    if not name: raise HTTPException(422,"Project name cannot be blank")
    con=db()
    try:
        cur=con.execute("INSERT INTO projects(name,owner_id) VALUES(?,?)",(name,u["id"])); pid=cur.lastrowid
        con.execute("INSERT INTO memberships VALUES(?,?)",(pid,u["id"])); con.commit()
    except sqlite3.IntegrityError:
        con.close(); raise HTTPException(409,"Project name already exists")
    con.close(); return {"id":pid,"name":name}

@app.get("/api/projects/{project_id}")
def get_project(project_id:int,session:str | None=Cookie(default=None)):
    u=current_user(session); con=db()
    if not project_access(con,project_id,u["id"]): con.close(); raise HTTPException(404,"Project not found")
    p=con.execute("SELECT id,name FROM projects WHERE id=?",(project_id,)).fetchone(); con.close()
    if not p: raise HTTPException(404,"Project not found")
    return dict(p)

@app.post("/api/projects/{project_id}/tasks")
def create_task(project_id:int,payload:TaskInput,session:str | None=Cookie(default=None)):
    u=current_user(session); title=payload.title.strip()
    if not title: raise HTTPException(422,"Task title cannot be blank")
    con=db()
    if not project_access(con,project_id,u["id"]): con.close(); raise HTTPException(404,"Project not found")
    cur=con.execute("INSERT INTO tasks(project_id,title,description) VALUES(?,?,?)",(project_id,title,payload.description)); tid=cur.lastrowid
    con.commit(); con.close(); return {"id":tid,"project_id":project_id,"title":title,"status":"To Do"}

@app.post("/api/projects/{project_id}/members")
def add_project_member(project_id:int,payload:MemberInput,session:str|None=Cookie(default=None)):
    u=current_user(session); con=db()
    project=con.execute("SELECT owner_id FROM projects WHERE id=?",(project_id,)).fetchone()
    if not project or project["owner_id"]!=u["id"]:
        con.close(); raise HTTPException(404,"Project not found")
    member=con.execute("SELECT id,email FROM users WHERE email=?",(payload.email.lower(),)).fetchone()
    if not member:
        con.close(); raise HTTPException(404,"User not found")
    con.execute("INSERT OR IGNORE INTO memberships(project_id,user_id) VALUES(?,?)",(project_id,member["id"]))
    con.commit(); con.close(); return {"project_id":project_id,"user_id":member["id"],"email":member["email"]}

@app.delete("/api/projects/{project_id}")
def delete_project(project_id:int,session:str|None=Cookie(default=None)):
    u=current_user(session); con=db()
    project=con.execute("SELECT owner_id FROM projects WHERE id=?",(project_id,)).fetchone()
    if not project or project["owner_id"]!=u["id"]:
        con.close(); raise HTTPException(404,"Project not found")
    con.execute("DELETE FROM projects WHERE id=?",(project_id,))
    con.commit(); con.close(); return {"deleted":True}

@app.get("/api/tasks")
def list_tasks(project_id:int|None=None,search:str="",session:str|None=Cookie(default=None)):
    u=current_user(session); con=db()
    q="""SELECT t.id,t.project_id,t.title,t.status,t.assignee_id FROM tasks t JOIN memberships m ON m.project_id=t.project_id WHERE m.user_id=?"""
    args=[u["id"]]
    if project_id is not None: q+=" AND t.project_id=?"; args.append(project_id)
    if search: q+=" AND lower(t.title) LIKE ?"; args.append("%"+search.lower()+"%")
    rows=con.execute(q,args).fetchall(); con.close(); return [dict(x) for x in rows]

@app.patch("/api/tasks/{task_id}")
def update_task(task_id:int,payload:TaskUpdate,session:str|None=Cookie(default=None)):
    u=current_user(session); con=db()
    task=con.execute("SELECT * FROM tasks WHERE id=?",(task_id,)).fetchone()
    if not task or not project_access(con,task["project_id"],u["id"]): con.close(); raise HTTPException(404,"Task not found")
    if payload.status is not None:
        allowed={"To Do":"In Progress","In Progress":"Done"}
        if allowed.get(task["status"])!=payload.status: con.close(); raise HTTPException(409,"Invalid status transition")
    updates=[]; args=[]
    if payload.title is not None:
        title=payload.title.strip()
        if not title: con.close(); raise HTTPException(422,"Task title cannot be blank")
        updates.append("title=?"); args.append(title)
    if payload.status is not None: updates.append("status=?"); args.append(payload.status)
    if payload.assignee_email is not None:
        member=con.execute("SELECT u.id FROM users u JOIN memberships m ON m.user_id=u.id WHERE m.project_id=? AND u.email=?",(task["project_id"],payload.assignee_email.lower())).fetchone()
        if not member: con.close(); raise HTTPException(422,"Assignee must be a project member")
        updates.append("assignee_id=?"); args.append(member["id"])
    if updates:
        args.append(task_id); con.execute("UPDATE tasks SET "+",".join(updates)+" WHERE id=?",args); con.commit()
    out=con.execute("SELECT id,title,status,assignee_id FROM tasks WHERE id=?",(task_id,)).fetchone(); con.close(); return dict(out)

@app.post("/api/tasks/{task_id}/comments")
def add_comment(task_id:int,payload:CommentInput,session:str|None=Cookie(default=None)):
    u=current_user(session); body=payload.body.strip()
    if not body: raise HTTPException(422,"Comment cannot be blank")
    con=db(); task=con.execute("SELECT project_id FROM tasks WHERE id=?",(task_id,)).fetchone()
    if not task or not project_access(con,task["project_id"],u["id"]): con.close(); raise HTTPException(404,"Task not found")
    try:
        cur=con.execute("INSERT INTO comments(task_id,author_id,body,idempotency_key) VALUES(?,?,?,?)",(task_id,u["id"],body,payload.idempotency_key)); con.commit()
    except sqlite3.IntegrityError:
        existing=con.execute("SELECT id,body FROM comments WHERE idempotency_key=?",(payload.idempotency_key,)).fetchone(); con.close()
        if existing: return dict(existing)
        raise HTTPException(409,"Comment could not be saved")
    result={"id":cur.lastrowid,"body":body}; con.close(); return result

@app.get("/api/tasks/{task_id}/comments")
def get_comments(task_id:int,session:str|None=Cookie(default=None)):
    u=current_user(session); con=db(); task=con.execute("SELECT project_id FROM tasks WHERE id=?",(task_id,)).fetchone()
    if not task or not project_access(con,task["project_id"],u["id"]): con.close(); raise HTTPException(404,"Task not found")
    rows=con.execute("SELECT id,body,author_id FROM comments WHERE task_id=? ORDER BY id",(task_id,)).fetchall(); con.close(); return [dict(x) for x in rows]

from fastapi import FastAPI, Request, Depends, Form
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date

from database import Base, engine, SessionLocal
from models import Project, Task

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- DASHBOARD ----------------

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()

    # dashboard_data = []
    # for p in projects:
    #     total = len(p.tasks)
    #     done = len([t for t in p.tasks if t.done])
    #     progress = int((done / total) * 100) if total else 0
    #     dashboard_data.append((p, progress))

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request, 
            # "projects": dashboard_data,
            "projects": projects,
            "current_project": None
        }
    )


# ---------------- PROJECT ----------------

@app.get("/projects/create")
def create_project_form(request: Request, db: Session = Depends(get_db)):
    # return templates.TemplateResponse("create_project.html", {"request": request})
    projects = db.query(Project).all()
    return templates.TemplateResponse(
        "create_project.html",
        {
            "request": request,
            "projects": projects,
            "current_project": None
        }
    )


@app.post("/projects/create")
def create_project(name: str = Form(...), db: Session = Depends(get_db)):
    project = Project(name=name)
    db.add(project)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.get("/projects/{project_id}")
def view_project(project_id: int, request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    project = db.query(Project).get(project_id)
    project.tasks.sort(
        # done tasks to list last
        key=lambda t: (t.done, t.due_date is None, t.due_date)
    )
    return templates.TemplateResponse(
        "project.html",
        {
            "request": request, 
            "projects": projects,
            "current_project": project,
            "today": date.today().isoformat()
        }
    )


# ---------------- TASKS ----------------

@app.post("/projects/{project_id}/tasks")
def add_task(
    project_id: int,
    title: str = Form(...),
    due_date: date = Form(...),
    priority: str = Form(...),
    db: Session = Depends(get_db)
):
    task = Task(
        title=title,
        due_date=due_date,
        priority=priority,
        project_id=project_id
    )
    db.add(task)
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    task.done = not task.done
    db.commit()
    return RedirectResponse(f"/projects/{task.project_id}", status_code=303)

@app.get("/tasks/{task_id}/edit")
def edit_task_form(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    task = db.query(Task).get(task_id)
    projects = db.query(Project).all()

    if not task:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "edit_task.html",
        {
            "request": request, 
            "task": task,
            "projects": projects,
            "current_project": task.project
        }
    )

@app.post("/tasks/{task_id}/edit")
def update_task(
    task_id: int,
    title: str = Form(...),
    due_date: date = Form(...),
    priority: str = Form(...),
    db: Session = Depends(get_db)
):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404)

    task.title = title
    task.due_date = due_date
    task.priority = priority

    db.commit()
    return RedirectResponse(f"/projects/{task.project_id}", status_code=303)


@app.post("/projects/{project_id}/notes")
def update_project_notes(
    project_id: int,
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    project = db.query(Project).get(project_id)
    project.notes = notes
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


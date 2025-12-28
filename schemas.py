from pydantic import BaseModel
from datetime import date

class ProjectCreate(BaseModel):
    name: str


class TaskCreate(BaseModel):
    title: str
    due_date: date
    priority: str

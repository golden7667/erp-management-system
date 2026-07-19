import os
import django

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_erp.settings')
try:
    django.setup()
except RuntimeError:
    # Already configured in ASGI
    pass

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from asgiref.sync import sync_to_async
from departments.models import Department

# Pydantic Schemas
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Computer Science")
    code: str = Field(..., min_length=1, max_length=10, example="CSE")
    description: Optional[str] = Field(None, example="Department of Computer Science & Engineering")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        from_attributes = True

# FastAPI Application
fastapi_app = FastAPI(
    title="Smart College ERP - Department API",
    description="High-performance FastAPI microservice handling Department Management modules",
    version="1.0.0",
    docs_url="/fastapi/docs",
    openapi_url="/fastapi/openapi.json"
)

# Helper functions wrapped in sync_to_async for Django ORM safety
@sync_to_async
def get_all_departments():
    return list(Department.objects.all())

@sync_to_async
def get_department_by_id(dept_id: int):
    try:
        return Department.objects.get(pk=dept_id)
    except Department.DoesNotExist:
        return None

@sync_to_async
def get_department_by_code(code: str):
    return Department.objects.filter(code=code).first()

@sync_to_async
def create_new_department(data: DepartmentCreate):
    return Department.objects.create(
        name=data.name,
        code=data.code.upper(),
        description=data.description
    )

@sync_to_async
def update_existing_department(dept: Department, data: DepartmentCreate):
    dept.name = data.name
    dept.code = data.code.upper()
    dept.description = data.description
    dept.save()
    return dept

@sync_to_async
def delete_existing_department(dept: Department):
    dept.delete()
    return True

# API Endpoints
@fastapi_app.get("/fastapi/departments/", response_model=List[DepartmentOut])
async def list_departments():
    return await get_all_departments()

@fastapi_app.get("/fastapi/departments/{dept_id}", response_model=DepartmentOut)
async def read_department(dept_id: int):
    dept = await get_department_by_id(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept

@fastapi_app.post("/fastapi/departments/", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(data: DepartmentCreate):
    existing = await get_department_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="Department with this code already exists")
    return await create_new_department(data)

@fastapi_app.put("/fastapi/departments/{dept_id}", response_model=DepartmentOut)
async def update_department(dept_id: int, data: DepartmentCreate):
    dept = await get_department_by_id(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if code belongs to another department
    code_match = await get_department_by_code(data.code)
    if code_match and code_match.id != dept_id:
        raise HTTPException(status_code=400, detail="Another department is already using this code")
        
    return await update_existing_department(dept, data)

@fastapi_app.delete("/fastapi/departments/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(dept_id: int):
    dept = await get_department_by_id(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    await delete_existing_department(dept)
    return None

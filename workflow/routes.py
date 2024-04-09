from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from workflow import schemas
from workflow.crud import CrudWorkflow


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()
crud = CrudWorkflow()

# workflow CRUD

@router.post('/workflow/', response_model=schemas.WorkflowResponse)
def create_workflow(workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    return crud.create_workflow(db, workflow)


@router.get('/workflow/{workflow_id}', response_model=schemas.WorkflowResponse)
def read_workflow(workflow_id: int, db: Session = Depends(get_db)):
    return crud.get_workflow(db, workflow_id)


@router.get('/workflow/list/', response_model=List[schemas.WorkflowResponse])
def get_workflows(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_workflows(skip=skip, limit=limit, db=db)


@router.put('/workflow/{workflow_id}', response_model=schemas.WorkflowResponse)
def update_workflow(workflow_id: int, workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    db_workflow = crud.update_workflow(db=db, workflow_id=workflow_id, workflow=workflow)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return db_workflow


@router.delete('/workflow/{workflow_id}', response_model=schemas.WorkflowResponse)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    db_workflow = crud.delete_workflow(db=db, workflow_id=workflow_id)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not")
    return db_workflow

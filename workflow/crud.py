from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from workflow import schemas
from db import models


# CRUD WorkFlow
class CrudWorkflow:
    def create_workflow(self, db: Session, workflow: schemas.WorkflowCreate):
        db_workflow = models.Workflow(**workflow.model_dump())
        db.add(db_workflow)
        db.commit()
        db.refresh(db_workflow)
        return db_workflow

    def get_workflow(self, db: Session, workflow_id: int):
        db_workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return db_workflow

    def get_workflows(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Workflow]:
        return db.query(models.Workflow).offset(skip).limit(limit).all()

    def update_workflow(self, db: Session, workflow_id: int, workflow: schemas.WorkflowCreate):
        db_workflow = self.get_workflow(db=db, workflow_id=workflow_id)
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        for var, value in vars(workflow).items():
            setattr(db_workflow, var, value) if value else None
        db.commit()
        db.refresh(db_workflow)
        return db_workflow

    def delete_workflow(self, db: Session, workflow_id: int):
        db_workflow = self.get_workflow(db=db, workflow_id=workflow_id)
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        db.delete(db_workflow)
        db.commit()

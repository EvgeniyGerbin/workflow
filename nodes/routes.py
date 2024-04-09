from typing import List

from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from workflow.crud import CrudWorkflow

from nodes import schemas
from db import models
from .crud import CRUDBase
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)  # create all tables in the database
workflow_crud = CrudWorkflow()  # instantiate the CrudWorkflow class
crud_base = CRUDBase()  # instantiate the CRUDBase class
router = APIRouter()  # create an API router object


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Node Endpoints
@router.post("/nodes/", response_model=schemas.NodeResponse, status_code=201)
def create_node(node: schemas.NodeCreate, db: Session = Depends(get_db)):
    return crud_base.create_node(db=db, node=node)


@router.get("/nodes/{node_id}", response_model=schemas.NodeResponse)
def read_node(node_id: int, db: Session = Depends(get_db)):
    node = crud_base.get_node(db=db, node_id=node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put('/nodes/{node_id}', response_model=schemas.NodeResponse)
def update_node(node_id: int, node: schemas.NodeUpdate, db: Session = Depends(get_db)):
    updated_node = crud_base.update_node(db=db, node_id=node_id, updated_node=node)
    if updated_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return updated_node


@router.delete('/nodes/{node_id}', status_code=204)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    crud_base.delete_node(db=db, node_id=node_id)
    return Response(status_code=204)


# initialize a workflow by creating a start node
@router.post('/workflows/{workflow_id}/start_node/', response_model=schemas.NodeResponse)
def init_workflow(name: str, description: str, workflow_id: int, db: Session = Depends(get_db)):
    check_workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not check_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    start_node = crud_base.create_start_node(db=db, name=name, description=description, workflow_id=workflow_id)
    if start_node is None:
        raise HTTPException(status_code=400, detail="Unable to create node.")
    else:
        return start_node


# create a message node in a workflow
@router.post("/workflows/{workflow_id}/nodes/message/", response_model=schemas.NodeResponse)
def init_message_node(workflow_id: int, name: str, description: str, text: str,
                      status: str, db: Session = Depends(get_db)):
    check_workflow = workflow_crud.get_workflow(db, workflow_id)
    if not check_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    message_node = crud_base.create_message_node(db=db, name=name, description=description,
                                                 workflow_id=workflow_id, status=status, text=text)

    return message_node


# create a condition node in a workflow
@router.post("/workflows/{workflow_id}/nodes/condition/", response_model=schemas.NodeResponse)
def init_condition_node(workflow_id: int, db: Session = Depends(get_db)):
    condition_node = crud_base.create_condition_node(db, workflow_id)
    if condition_node is None:
        raise HTTPException(status_code=400, detail="Unable to create node.")
    else:
        return condition_node


# create an end node in a workflow
@router.post("/workflows/{workflow_id}/nodes/end/", response_model=schemas.NodeResponse)
def init_end_node(workflow_id: int, name: str, description: str, db: Session = Depends(get_db)):
    end_node = crud_base.create_end_node(db=db, workflow_id=workflow_id,
                                         name=name, description=description)
    if end_node is None:
        raise HTTPException(status_code=400, detail="Unable to create node.")
    else:
        return end_node


# execute a workflow to find a path
@router.post("/workflows/{workflow_id}/run/", response_model=List[List[int]])
def run_workflow(workflow_id: int, db: Session = Depends(get_db)):
    try:
        workflow_path = crud_base.run_workflow(db=db, workflow_id=workflow_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return workflow_path

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from edge import schemas, crud
from db.database import SessionLocal
from db import models

router = APIRouter()

crud_edge = crud.CRUDEdge()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoints EDGE
@router.post("/edges/", response_model=schemas.EdgeResponse, status_code=201)
def create_edge(edge: schemas.EdgeCreate, db: Session = Depends(get_db)):
    return crud_edge.create_edge(db=db, edge_data=edge)


@router.get("/edges/{edge_id}", response_model=schemas.EdgeResponse)
def read_edge(edge_id: int, db: Session = Depends(get_db)):
    return crud_edge.get_edge(db=db, edge_id=edge_id)


@router.get("/edges/list/", response_model=list[schemas.EdgeResponse])
def read_edges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    edges = crud_edge.get_edges(db, skip=skip, limit=limit)
    return edges


@router.put("/edges/{edge_id}", response_model=schemas.EdgeResponse)
def update_edge(edge_id: int, edge: schemas.EdgeCreate, db: Session = Depends(get_db)):
    return crud_edge.update_edge(db=db, edge_id=edge_id, edge_data=edge)


@router.delete("/edges/{edge_id}")
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    crud_edge.delete_edge(db=db, edge_id=edge_id)
    return {"detail": "Edge deleted successfully"}

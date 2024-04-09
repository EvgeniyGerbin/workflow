from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from db import models
from edge import schemas

# EDGE CRUD
class CRUDEdge:
    def create_edge(self, db: Session, edge_data: schemas.EdgeCreate) -> models.Edge:
        db_edge = models.Edge(**edge_data.model_dump())
        db.add(db_edge)
        db.commit()
        db.refresh(db_edge)
        return db_edge

    def get_edge(self, db: Session, edge_id: int) -> models.Edge:
        edge = db.query(models.Edge).filter(models.Edge.id == edge_id).first()
        if edge is None:
            raise HTTPException(status_code=404, detail="Edge not found")
        return edge

    def get_edges(self, db: Session, skip: int = 0, limit: int = 100) -> list[models.Edge]:
        return db.query(models.Edge).offset(skip).limit(limit).all()

    def update_edge(self, db: Session, edge_id: int, edge_data: schemas.EdgeCreate) -> models.Edge:
        db_edge = db.query(models.Edge).filter(models.Edge.id == edge_id).first()
        if db_edge is None:
            raise HTTPException(status_code=404, detail="Edge not found")
        for key, value in edge_data.model_dump(exclude_unset=True).items():
            setattr(db_edge, key, value)
        db.commit()
        db.refresh(db_edge)
        return db_edge

    def delete_edge(self, db: Session, edge_id: int):
        db_edge = db.query(models.Edge).filter(models.Edge.id == edge_id).first()
        if db_edge is None:
            raise HTTPException(status_code=404, detail="Edge not found")
        db.delete(db_edge)
        db.commit()

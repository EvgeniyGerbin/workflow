from pydantic import BaseModel
from typing import List, Optional, ClassVar
from nodes.schemas import NodeCreate


# Base model for workflows.
class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None


# Inherits from WorkflowBase, used for creating workflows.
class WorkflowCreate(WorkflowBase):
    pass


# Detailed response model for a workflow.
class WorkflowResponse(WorkflowBase):
    id: int
    nodes: List[NodeCreate] = []

    config: ClassVar[dict] = {'from_attributes': True}



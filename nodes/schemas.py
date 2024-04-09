from pydantic import BaseModel
from typing import Optional
from db.models import NodeType, NodeStatus


# Define a Pydantic model for creating a new node.
class NodeCreate(BaseModel):
    name: str
    type: NodeType
    description: Optional[str] = None
    status: Optional[NodeStatus] = None
    message_text: Optional[str] = None
    condition_expression: Optional[str] = None


# Define a Pydantic model for updating an existing node.
class NodeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[NodeType] = None
    description: Optional[str] = None
    status: Optional[NodeStatus] = None
    message_text: Optional[str] = None
    condition_expression: Optional[str] = None


class NodeResponse(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[NodeType] = None
    description: Optional[str] = None
    status: Optional[NodeStatus] = None
    message_text: Optional[str] = None
    condition_expression: Optional[str] = None
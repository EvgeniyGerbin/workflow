from typing import ClassVar

from pydantic import BaseModel, ConfigDict


# Pydantic model for EDGE
class EdgeBase(BaseModel):
    from_node_id: int
    to_node_id: int


class EdgeCreate(EdgeBase):
    pass


class EdgeResponse(EdgeBase):
    id: int
    config: ClassVar[dict] = {'from_attributes': True}



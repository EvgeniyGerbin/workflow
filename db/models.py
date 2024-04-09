from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum
from db.database import Base


# Defines an enumeration for node types, specifying the different kinds of nodes that can exist in a workflow.
class NodeType(PythonEnum):
    START = "start"
    MESSAGE = "message"
    CONDITION = "condition"
    END = "end"


# Defines an enumeration for node statuses, representing the various states a node can be in during workflow execution.
class NodeStatus(PythonEnum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"


# Represents a workflow configuration, containing a name, an optional description, and a collection of nodes.
class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)

    nodes = relationship("Node", back_populates="workflow")


# Defines the base model for a node within a workflow, including details.
class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    type = Column(Enum(NodeType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(NodeStatus), nullable=True)
    message_text = Column(Text, nullable=True)
    condition_expression = Column(Text, nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    workflow = relationship("Workflow", back_populates="nodes")

    incoming_edges = relationship("Edge", foreign_keys="[Edge.to_node_id]", cascade="all, delete",
                                  back_populates="to_node")
    outgoing_edges = relationship("Edge", foreign_keys="[Edge.from_node_id]", cascade="all, delete",
                                  back_populates="from_node")


# Models the connections between nodes.
class Edge(Base):
    __tablename__ = "edges"
    id = Column(Integer, primary_key=True)
    from_node_id = Column(Integer, ForeignKey("nodes.id", ondelete='CASCADE'), nullable=False)
    to_node_id = Column(Integer, ForeignKey("nodes.id", ondelete='CASCADE'), nullable=False)

    from_node = relationship("Node", foreign_keys=[from_node_id], back_populates="outgoing_edges")
    to_node = relationship("Node", foreign_keys=[to_node_id], back_populates="incoming_edges")

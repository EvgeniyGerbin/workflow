import networkx as nx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import NodeType, NodeStatus
from nodes import schemas
from db import models
from edge.crud import CRUDEdge

crud_edge = CRUDEdge()  # instantiate the CRUDEdge class



class CRUDBase:
    # Retrieve a node by its ID from the database
    def get_node(self, db: Session, node_id: int):
        node = db.query(models.Node).filter(models.Node.id == node_id).first()
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return node

    # Create a new node in the database
    def create_node(self, db: Session, node: schemas.NodeCreate):
        db_node = models.Node(**node.model_dump())
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return db_node

    # Update an existing node in the database
    def update_node(self, db: Session, node_id: int, updated_node: schemas.NodeUpdate):
        db_node = self.get_node(db, node_id)
        for key, value in updated_node.model_dump(exclude_unset=True).items():
            setattr(db_node, key, value)
        db.commit()
        db.refresh(db_node)
        return db_node

    # Delete a node from the database
    def delete_node(self, db: Session, node_id: int):
        db_node = self.get_node(db, node_id)
        db.delete(db_node)
        db.commit()

    # Create a start node for a workflow
    def create_start_node(self, db: Session, workflow_id: int, name: str, description: str):
        node_data = schemas.NodeCreate(name=name, type=NodeType.START, description=description, status=None,
                                       message_text=None, condition_expression=None)
        db_node = models.Node(**node_data.model_dump(), workflow_id=workflow_id)
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return db_node

    # Create a message node in a workflow
    def create_message_node(self,
                            db: Session,
                            name: str,
                            description: str,
                            text: str,
                            status: str,
                            workflow_id: int

                            ):
        message_node = models.Node(type=NodeType.MESSAGE, name=name, description=description, workflow_id=workflow_id,
                                   message_text=text, status=status)
        db.add(message_node)
        db.commit()
        db.refresh(message_node)
        return message_node

    # Create an end node in a workflow
    def create_end_node(self,
                        db: Session,
                        workflow_id: int,
                        name: str,
                        description: str
                        ):
        end_node = models.Node(type=NodeType.END, name=name, description=description, workflow_id=workflow_id)
        db.add(end_node)
        db.commit()
        db.refresh(end_node)
        return end_node

    # Create a condition node in a workflow
    def create_condition_node(self,
                              db: Session,
                              workflow_id: int
                              ):
        previous_node = db.query(models.Node).filter(models.Node.workflow_id == workflow_id) \
            .order_by(models.Node.id.desc()).first()

        if previous_node and previous_node.status == NodeStatus.SENT and previous_node.type == NodeType.MESSAGE:
            message_node = models.Node(
                type=NodeType.MESSAGE, name='YES', description='Yes EDGE', workflow_id=workflow_id)

            db.add(message_node)
            db.commit()
            db.refresh(message_node)
            edge_node = models.Edge(from_node=previous_node, to_node=message_node)
            db.add(edge_node)
            db.commit()
            db.refresh(edge_node)

            return message_node

        else:
            condition_node = models.Node(
                type=NodeType.CONDITION, name='NO', description='No EDGE', workflow_id=workflow_id)

            db.add(condition_node)
            db.commit()
            db.refresh(condition_node)
            edge_node = models.Edge(from_node=previous_node, to_node=condition_node)
            db.add(edge_node)
            db.commit()
            db.refresh(edge_node)
            return condition_node

    # Run a workflow and return the paths from start nodes to end nodes
    def run_workflow(self, db: Session, workflow_id: int) -> list:
        # Retrieve all nodes associated with the specified workflow_id
        nodes = db.query(models.Node).filter(models.Node.workflow_id == workflow_id).all()

        # Retrieve all edges associated with the specified workflow_id. Edges connect nodes in the workflow.
        edges = db.query(models.Edge).join(models.Node, models.Edge.from_node_id == models.Node.id) \
            .filter(models.Node.workflow_id == workflow_id).all()

        # Initialize a directed graph. In this graph, nodes represent workflow steps, and edges represent transitions between these steps.
        G = nx.DiGraph()

        # Add each node from the database as a node in the graph with its ID, type, and name as attributes.
        for node in nodes:
            G.add_node(node.id, type=node.type, name=node.name)

        # Add edges between nodes in the graph based on the retrieved edges from the database.
        for edge in edges:
            G.add_edge(edge.from_node_id, edge.to_node_id)

        # Identify all start nodes (nodes where the workflow begins) and end nodes (nodes where the workflow can end).
        start_nodes = [node.id for node in nodes if node.type == NodeType.START]
        end_nodes = [node.id for node in nodes if node.type == NodeType.END]

        # Find all possible paths from each start node to each end node. This determines the different ways a workflow can proceed from start to finish.
        paths = []
        for start_node in start_nodes:
            for end_node in end_nodes:
                try:
                    # Find the shortest path from the current start node to the current end node. This represents one possible route through the workflow.
                    path = nx.shortest_path(G, source=start_node, target=end_node)
                    paths.append(path)
                except nx.NetworkXNoPath:
                    # If there is no path from the current start node to the current end node, skip and continue with the next pair.
                    continue

        # Return the list of all paths found. Each path is a list of node IDs, representing a sequence of steps in the workflow.
        return paths
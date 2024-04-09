import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.models import Workflow, Node, NodeType, Edge
from main import app
from nodes.routes import get_db

client = TestClient(app)

wf_data = {
    "name": "start Workflow",
    "description": "start description"
}


@pytest.fixture
def test_db_session():
    session = next(get_db())
    yield session
    session.rollback()


wf_data = {
    "name": "start Workflow",
    "description": "start description"
}


def test_node_start(test_db_session):
    response_workflow = client.post('/workflow/', json=wf_data)
    workflow_id = response_workflow.json()["id"]

    response_node = client.post(f'/workflows/{workflow_id}/start_node?name=somename&description=desc')
    assert response_node.status_code == 200
    assert response_node.json()['type'] == 'start'


def test_message_node(test_db_session):
    response_workflow = client.post('/workflow/', json=wf_data)
    workflow_id = response_workflow.json()["id"]

    response_node = client.post(
        f'/workflows/{workflow_id}/nodes/message/?name=Name&description=Desc%20something%20&text=Text&status=OPENED')
    assert response_node.status_code == 200
    assert response_node.json()['type'] == 'message'
    assert response_node.json()['status'] == 'opened'


def test_condition_node(test_db_session):
    response_workflow = client.post('/workflow/', json=wf_data)
    workflow_id = response_workflow.json()["id"]

    client.post(
        f'/workflows/{workflow_id}/nodes/message/?name=Name&description=Desc%20something%20&text=Text&status=OPENED')

    response_node = client.post(f'/workflows/{workflow_id}/nodes/condition/')

    assert response_node.status_code == 200
    assert response_node.json()['description'] == 'No EDGE'


def test_end_node(test_db_session):
    response_workflow = client.post('/workflow/', json=wf_data)
    workflow_id = response_workflow.json()["id"]

    response_node = client.post(f'/workflows/{workflow_id}/nodes/end/?name=End&description=Test End')
    assert response_node.status_code == 200
    assert response_node.json()['type'] == 'end'
    assert response_node.json()['description'] == 'Test End'


def test_update_node(test_db_session):
    response_workflow = client.post('/workflow/', json=wf_data)
    workflow_id = response_workflow.json()["id"]

    response_node = client.post(f'/workflows/{workflow_id}/nodes/end/?name=End&description=Test End')
    node_id = response_node.json()["id"]

    update_data = {
        "name": "updated node",
        "description": "updated",
    }

    response = client.put(f'/nodes/{node_id}', json=update_data)
    assert response.status_code == 200
    assert response.json()['name'] == 'updated node'
    assert response.json()['description'] == 'updated'


def test_delete_node(test_db_session):
    response_workflow = client.post('/workflow/', json=wf_data)
    workflow_id = response_workflow.json()["id"]

    response_node = client.post(f'/workflows/{workflow_id}/nodes/end/?name=Endnode%20&description=desc')
    node_id = response_node.json()["id"]

    response = client.delete(f'/nodes/{node_id}')
    assert response.status_code == 204


def test_create_edge(test_db_session):
    response_workflow = client.post('/workflow/', json=wf_data)
    assert response_workflow.status_code == 200
    workflow_id = response_workflow.json()["id"]

    response_first_node = client.post(f'/workflows/{workflow_id}/start_node?name=somename&description=desc')
    assert response_first_node.status_code == 200
    node_first_id = response_first_node.json()["id"]

    response_second_node = client.post(
        f'/workflows/{workflow_id}/nodes/message/?name=Name&description=Desc&text=Text&status=OPENED')
    assert response_second_node.status_code == 200
    node_second_id = response_second_node.json()["id"]

    edge_data = {
        "from_node_id": node_first_id,
        "to_node_id": node_second_id
    }

    response_edge = client.post('/edges/', json=edge_data)
    assert response_edge.status_code == 201
    response_data = response_edge.json()
    assert response_data['from_node_id'] == node_first_id
    assert response_data['to_node_id'] == node_second_id


def create_test_data(db: Session):
    workflow = Workflow(name="Test Workflow", description="Test Description")
    db.add(workflow)
    db.commit()

    start_node = Node(type=NodeType.START, name="Start Node", workflow_id=workflow.id)
    end_node = Node(type=NodeType.END, name="End Node", workflow_id=workflow.id)
    db.add(start_node)
    db.add(end_node)
    db.commit()

    edge = Edge(from_node_id=start_node.id, to_node_id=end_node.id)
    db.add(edge)
    db.commit()

    return workflow.id


def test_run_workflow(test_db_session):
    workflow_id = create_test_data(test_db_session)

    response = client.post(f"/workflows/{workflow_id}/run/")
    assert response.status_code == 200
    paths = response.json()

    assert len(paths) > 0
    for path in paths:
        assert len(path) >= 2

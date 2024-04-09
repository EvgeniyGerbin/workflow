from fastapi import FastAPI
from nodes.routes import router as node_router
from workflow.routes import router as workflow_router
from edge.routes import router as edge_router


app = FastAPI()


app.include_router(node_router)
app.include_router(workflow_router)
app.include_router(edge_router)

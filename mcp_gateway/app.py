"""FastAPI application factory."""
from fastapi import FastAPI, HTTPException
from .models import ToolDefinition, ToolExecutionRequest, ToolExecutionResult
from .registry import ToolRegistry


def create_app(registry: ToolRegistry) -> FastAPI:
    app = FastAPI(
        title="Agent Tool Orchestration Gateway",
        description="FastAPI service for secure MCP tool discovery and execution",
        version="0.1.0",
    )

    @app.get("/tools")
    def list_tools():
        return registry.list_tools()

    @app.post("/tools/execute", response_model=ToolExecutionResult)
    def execute_tool(req: ToolExecutionRequest):
        res = registry.execute_tool(req)
        if not res.success and "missing required scope" in (res.error or "").lower():
            raise HTTPException(status_code=403, detail=res.error)
        if not res.success and "security violation" in (res.error or "").lower():
            raise HTTPException(status_code=400, detail=res.error)
        return res

    @app.get("/metrics")
    def get_metrics():
        return registry.metrics

    return app

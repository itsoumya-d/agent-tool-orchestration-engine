"""Pydantic schemas for MCP tool definitions and execution requests."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Description of the tool capability")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for arguments")
    required_scopes: List[str] = Field(default_factory=list, description="Scopes needed to execute this tool")
    timeout_seconds: float = Field(default=5.0, description="Max execution timeout in seconds")


class ToolExecutionRequest(BaseModel):
    tool_name: str
    tenant_id: str
    granted_scopes: List[str] = Field(default_factory=list)
    arguments: Dict[str, Any] = Field(default_factory=dict)
    session_context: Optional[str] = Field(default=None, description="Prompt context to inspect for injections")


class ToolExecutionResult(BaseModel):
    tool_name: str
    tenant_id: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float

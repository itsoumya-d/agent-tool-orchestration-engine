"""Tool registry and execution engine."""
import time
from typing import Dict, Any, Callable, List, Optional
from .models import ToolDefinition, ToolExecutionRequest, ToolExecutionResult
from .security import SecurityGuardrails


class ToolRegistry:
    """Manages MCP tools and executes them with safety guardrails."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self.metrics = {
            "total_invocations": 0,
            "successful_invocations": 0,
            "failed_invocations": 0,
            "security_blocks": 0,
        }

    def register_tool(self, tool_def: ToolDefinition, handler: Callable[[Dict[str, Any]], Any]) -> None:
        self._tools[tool_def.name] = tool_def
        self._handlers[tool_def.name] = handler

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def execute_tool(self, req: ToolExecutionRequest) -> ToolExecutionResult:
        t0 = time.perf_counter()
        self.metrics["total_invocations"] += 1

        tool_def = self._tools.get(req.tool_name)
        if not tool_def:
            self.metrics["failed_invocations"] += 1
            return ToolExecutionResult(
                tool_name=req.tool_name,
                tenant_id=req.tenant_id,
                success=False,
                error=f"Tool '{req.tool_name}' not found",
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
            )

        # 1. Safety Guardrails: Prompt injection check
        try:
            SecurityGuardrails.inspect_context(req.session_context)
            for v in req.arguments.values():
                if isinstance(v, str):
                    SecurityGuardrails.inspect_context(v)
        except Exception as e:
            self.metrics["security_blocks"] += 1
            self.metrics["failed_invocations"] += 1
            return ToolExecutionResult(
                tool_name=req.tool_name,
                tenant_id=req.tenant_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
            )

        # 2. Scope Authorization
        try:
            SecurityGuardrails.verify_authorization(tool_def.required_scopes, req.granted_scopes)
        except Exception as e:
            self.metrics["security_blocks"] += 1
            self.metrics["failed_invocations"] += 1
            return ToolExecutionResult(
                tool_name=req.tool_name,
                tenant_id=req.tenant_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
            )

        # 3. Parameter Validation (basic required check)
        required_params = tool_def.input_schema.get("required", [])
        for param in required_params:
            if param not in req.arguments:
                self.metrics["failed_invocations"] += 1
                return ToolExecutionResult(
                    tool_name=req.tool_name,
                    tenant_id=req.tenant_id,
                    success=False,
                    error=f"Missing required parameter '{param}'",
                    execution_time_ms=(time.perf_counter() - t0) * 1000.0,
                )

        # 4. Handler Execution
        handler = self._handlers[req.tool_name]
        try:
            out = handler(req.arguments)
            self.metrics["successful_invocations"] += 1
            return ToolExecutionResult(
                tool_name=req.tool_name,
                tenant_id=req.tenant_id,
                success=True,
                output=out,
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
            )
        except Exception as err:
            self.metrics["failed_invocations"] += 1
            return ToolExecutionResult(
                tool_name=req.tool_name,
                tenant_id=req.tenant_id,
                success=False,
                error=f"Handler execution failed: {str(err)}",
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
            )

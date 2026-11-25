# Agent Tool Orchestration Engine

Enterprise agent tool execution gateway and Model Context Protocol (MCP) orchestrator built with Python 3.12, FastAPI, and Pydantic.

## Features
- **MCP Tool Registration**: Dynamic tool schema definition with parameter validation and execution timeouts.
- **Sandboxed Safety Guardrails**: Heuristic prompt injection detection and tenant authorization boundary enforcement.
- **Auditing & Observability**: Structured execution metrics, invocation latency tracking, and security violation audit logging.

## Running Tests
```bash
pytest -v
```

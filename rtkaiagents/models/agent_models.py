from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StructuredResponseConfig(BaseModel):
    enabled: bool = False
    schema: Optional[Dict[str, Any]] = None


class ModelConfig(BaseModel):
    provider: str = "litellm"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 1000
    additional_params: Dict[str, Any] = Field(default_factory=dict)
    structured_response: Optional[StructuredResponseConfig] = None


class InlinePromptConfig(BaseModel):
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None


class PromptProviderConfig(BaseModel):
    inline: Optional[InlinePromptConfig] = None


class MemoryConfig(BaseModel):
    enabled: bool = True


class AgentConfig(BaseModel):
    name: str
    type: str = "react"
    model: ModelConfig
    prompt_provider: Optional[PromptProviderConfig] = None
    mcp_servers: List[str] = Field(default_factory=list)
    max_iterations: int = 10
    early_stopping: bool = True
    verbose: bool = False
    memory: Optional[MemoryConfig] = None
    structured_response: Optional[StructuredResponseConfig] = None


class NodeConfig(BaseModel):
    name: str
    type: str = "agent"
    agent_name: Optional[str] = None
    custom: Optional[Dict[str, Any]] = None


class EdgeCondition(BaseModel):
    condition: str
    target: str


class EdgeConfig(BaseModel):
    source: str
    target: str
    type: str = "static"
    conditions: List[EdgeCondition] = Field(default_factory=list)
    default_target: Optional[str] = None


class GraphConfig(BaseModel):
    name: str
    description: str = ""
    nodes: List[NodeConfig] = Field(default_factory=list)
    edges: List[EdgeConfig] = Field(default_factory=list)
    start_node: Optional[str] = None


class MCPConfig(BaseModel):
    name: str
    config: Dict[str, Any] = Field(default_factory=dict)


class ToolConfig(BaseModel):
    name: str
    config: Dict[str, Any] = Field(default_factory=dict)


class SharedModelConfig(BaseModel):
    name: str
    provider: str = "litellm"
    model_name: str = "gpt-4o-mini"


class PersistenceConfig(BaseModel):
    type: str = "memory"
    config: Dict[str, Any] = Field(default_factory=dict)


class MiddlewareConfig(BaseModel):
    name: str
    config: Dict[str, Any] = Field(default_factory=dict)

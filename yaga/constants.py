from enum import Enum


class AgentType(str, Enum):
    REACT = "react"
    TOOL_CALLING = "tool_calling"
    OPENAI_FUNCTIONS = "openai_functions"
    DEEP = "deep"
    CUSTOM = "custom"
    SAGEMAKER = "sagemaker"


class NodeType(str, Enum):
    AGENT = "agent"
    CUSTOM = "custom"

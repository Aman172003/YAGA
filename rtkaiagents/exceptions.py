class AIAgentError(Exception):
    """Base error for the agents platform."""


class AgentNotFoundError(AIAgentError):
    pass


class GraphNotFoundError(AIAgentError):
    pass

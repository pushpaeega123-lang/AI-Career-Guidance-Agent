from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Abstract Base Class for Multi-Agent AI system.
    To be extended by domain agents (e.g. ProfileAgent, PathwayAgent, OpportunityAgent).
    """
    def __init__(self, agent_name: str, description: str):
        self.agent_name = agent_name
        self.description = description

    @abstractmethod
    def process_task(self, task_input: dict) -> dict:
        """
        Process incoming task request and return output context.
        Must be implemented by concrete agent subclasses.
        """
        pass

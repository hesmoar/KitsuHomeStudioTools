"""
Base integration class for DCC software
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseIntegration(ABC):
    """Base class for all DCC software integrations."""
    
    def __init__(self, software_path: str):
        """Initialize the integration with the software path."""
        self.software_path = software_path
    
    @abstractmethod
    def launch(self, task_context: Dict[str, Any]) -> None:
        """Launch the software with the given task context."""
        pass
    
    @abstractmethod
    def publish(self, task_context: Dict[str, Any]) -> None:
        """Publish the current work to Kitsu."""
        pass
    
    @abstractmethod
    def load_context(self, task_context: Dict[str, Any]) -> None:
        """Load the task context into the software."""
        pass
    
    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the software is installed."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get the software version."""
        pass 
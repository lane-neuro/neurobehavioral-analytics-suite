"""
This module defines the abstract base class BaseOperation, which provides a common interface for all operations in the
NeuroBehavioral Analytics Suite. The BaseOperation class requires any child class to implement execute, start, pause,
stop, and resume methods. It also provides a property for the status of the operation, which can be "idle", "started",
"paused", "running", or "stopped". This class is designed to be inherited by other classes that represent specific
operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.
    """

    @abstractmethod
    def __init__(self):
        """
        Initialize the operation instance.
        """
        pass

    @abstractmethod
    def init_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        pass

    @abstractmethod
    async def start(self):
        """
        Start the operation.
        """
        pass

    @abstractmethod
    async def execute(self):
        """
        Execute the operation.
        """
        pass

    @abstractmethod
    def get_result(self):
        """
        Retrieve the result of the operation, if applicable.
        """
        pass

    @abstractmethod
    async def pause(self):
        """
        Pause the operation.
        """
        pass

    @abstractmethod
    async def resume(self):
        """
        Resume the operation.
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        Stop the operation.
        """
        pass

    @abstractmethod
    async def reset(self):
        """
        Reset the operation.
        """
        pass

    @abstractmethod
    async def restart(self):
        """
        Restart the operation from the beginning.
        """
        pass

    @abstractmethod
    def is_running(self):
        """
        Check if the operation is currently running.
        """
        pass

    def is_complete(self):
        """
        Check if the operation is complete.
        """
        pass

    @abstractmethod
    def is_paused(self):
        """
        Check if the operation is currently paused.
        """
        pass

    @abstractmethod
    def is_stopped(self):
        """
        Check if the operation is currently stopped.
        """
        pass

    @abstractmethod
    def progress(self) -> Tuple[int, str]:
        """
        Get the progress of the operation.
        """
        pass

    @abstractmethod
    async def update_progress(self):
        """
        Update the progress of the operation.
        """
        pass

    @abstractmethod
    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operation has completed or been stopped.
        """
        pass

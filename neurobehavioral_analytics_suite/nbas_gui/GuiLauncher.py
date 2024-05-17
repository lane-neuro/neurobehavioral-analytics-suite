"""
This is the GuiLauncher module.

This module is responsible for launching the GUI of the NeuroBehavioral Analytics Suite. It initializes the necessary
classes and starts the DearPyGui event loop, keeping it running until the DearPyGui window is closed.

Author: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync
from neurobehavioral_analytics_suite.nbas_gui.ConsoleGui import ConsoleGui
from neurobehavioral_analytics_suite.nbas_gui.OperationManagerGui import OperationManagerGui
from neurobehavioral_analytics_suite.nbas_gui.ProjectManagerGui import ProjectManagerGui
from neurobehavioral_analytics_suite.nbas_gui.ResourceMonitorGui import ResourceMonitorGui


class GuiLauncher:
    """A class used to launch the GUI of the NeuroBehavioral Analytics Suite.

    Attributes:
        resource_monitor (ResourceMonitorGui): An instance of the ResourceMonitorGui class.
        console (ConsoleGui): An instance of the ConsoleGui class.
        operation_manager (OperationManagerGui): An instance of the OperationManagerGui class.
        project_manager (ProjectManagerGui): An instance of the ProjectManagerGui class.
        dpg_async (DearPyGuiAsync): An instance of the DearPyGuiAsync class.
    """

    def __init__(self, operation_handler):
        """Initializes the GuiLauncher with instances of the necessary classes."""
        self.operation_handler = operation_handler
        self.resource_monitor = None
        self.console = None
        self.operation_manager = None
        self.project_manager = None
        self.dpg_async = DearPyGuiAsync()  # initialize

    async def launch(self):
        """Launches the GUI.

        This method sets up the DearPyGui context, creates the viewport, sets up DearPyGui,
        initializes the GUI components, and starts the DearPyGui event loop. It keeps the event
        loop running until the DearPyGui window is closed.
        """
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()

        self.project_manager = ProjectManagerGui(self.operation_handler)
        self.operation_manager = OperationManagerGui(self.operation_handler)
        self.console = ConsoleGui(self.operation_handler)
        self.resource_monitor = ResourceMonitorGui(self.operation_handler)

        dpg.show_viewport()
        await self.dpg_async.start()

        # Keep the event loop running until the DearPyGui window is closed
        while dpg.is_dearpygui_running():
            await asyncio.sleep(0.01)

        dpg.destroy_context()
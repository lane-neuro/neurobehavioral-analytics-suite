"""
OperationModule

This module defines the OperationModule class, which is responsible for managing operations and their GUI representation
within the research analytics suite. It handles the initialization, execution, stopping, pausing, resuming, and
resetting of operations and updates the GUI accordingly.

Author: Lane
Copyright: Lane
Credits: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
import uuid
from typing import Any

import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.modules.CreateOperationModule import CreateOperationModule
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class OperationModule:
    """A class to manage operations and their GUI representation."""

    def __init__(self, operation: ABCOperation, operation_control: Any, width: int, height: int):
        """
        Initializes the OperationModule with the given operation, control, and logger.

        Args:
            operation (ABCOperation): An instance of ABCOperation.
            operation_control: Control interface for operations.
            width (int): The width of the module.
            height (int): The height of the module.
        """
        self.child_ops_parent = None
        self.log_container_id = None
        self._operation = operation
        self.operation_control = operation_control
        self.width = int(width * 1.0)
        self.height = int(height * 1.0)
        self._logger = CustomLogger()
        self.update_operation = None
        self.unique_id = str(uuid.uuid4())
        self.log_id = None
        self.result_id = None
        self.persistent_id = None
        self.cpu_bound_id = None

    async def initialize(self) -> None:
        """Initializes resources and adds the update operation."""
        self.update_operation = await self.add_update_operation()
        self.initialize_resources()

    def initialize_resources(self) -> None:
        """Initializes necessary resources and logs the event."""
        try:
            self._operation.attach_gui_module(self)
        except Exception as e:
            self._logger.error(e, self)

    async def add_update_operation(self) -> ABCOperation:
        """
        Adds an update operation to the operations manager.

        Returns:
            The created update operation or None if an error occurred.
        """
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=ABCOperation, name="gui_OperationUpdateTask", logger=self._logger,
                local_vars=self.operation_control.local_vars,
                func=self.update_gui, persistent=True, concurrent=True)
            operation.is_ready = True
            return operation
        except Exception as e:
            self._logger.error(e, self)
            self._operation.add_log_entry(f"Error creating task: {e}")

    async def execute_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Executes the operation."""
        try:
            self._operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self)
            self._operation.status = "error"
            self._operation.add_log_entry(f"Error executing operation: {e}")

    async def stop_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Stops the operation."""
        if not self._operation.persistent:
            try:
                await self._operation.stop()
            except Exception as e:
                self._logger.error(e, self)
                self._operation.status = "error"
                self._operation.add_log_entry(f"Error stopping operation: {e}")

    async def pause_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Pauses the operation."""
        if not self._operation.persistent:
            try:
                await self._operation.pause()
            except Exception as e:
                self._logger.error(e, self)
                self._operation.status = "error"
                self._operation.add_log_entry(f"Error pausing operation: {e}")

    async def resume_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Resumes the operation."""
        if not self._operation.persistent:
            try:
                await self._operation.resume()
            except Exception as e:
                self._logger.error(e, self)
                self._operation.status = "error"
                self._operation.add_log_entry(f"Error resuming operation: {e}")

    async def reset_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Resets the operation."""
        try:
            await self._operation.reset()
        except Exception as e:
            self._logger.error(e, self)
            self._operation.status = "error"
            self._operation.add_log_entry(f"Error resetting operation: {e}")

    def draw(self, parent) -> None:
        """Draws the GUI elements for the operation."""
        with dpg.group(parent=parent, height=int(self.height * 0.14) - 2):
            self.log_id = f"log_{self.unique_id}"
            self.result_id = f"result_{self.unique_id}"
            self.persistent_id = f"persistent_{self.unique_id}"
            self.cpu_bound_id = f"cpu_bound_{self.unique_id}"

            with dpg.child_window(height=-1, width=-1, border=True):
                dpg.add_text(f"Operation: {self._operation.name}")
                dpg.add_separator()

                with dpg.group(horizontal=True, width=-1, height=-1):
                    dpg.add_text(f"Status: {self._operation.status}",
                                 tag=f"status_{self._operation.name}_{self.unique_id}")
                    dpg.add_text(f"Persistent: {self._operation.persistent}", tag=self.persistent_id)
                    dpg.add_text(f"CPU Bound: {self._operation.is_cpu_bound}", tag=self.cpu_bound_id)

        with dpg.group(parent=parent, horizontal=True):
            with dpg.child_window(height=int(self.height * 0.85) - 12, width=int(self.width * 0.4) - 15, border=True):
                dpg.add_progress_bar(
                    default_value=self._operation.progress[0] / 100,
                    tag=f"progress_{self._operation.name}_{self.unique_id}",
                    overlay="%.1f%%" % self._operation.progress[0],
                    width=-1
                )
                dpg.add_separator()

                button_width = int(((self.width * 0.4) - 45) / 3)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Execute", callback=self.execute_operation, width=button_width)
                    dpg.add_button(label="Stop", callback=self.stop_operation, width=button_width)
                    dpg.add_button(label="Pause", callback=self.pause_operation, width=button_width)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Resume", callback=self.resume_operation, width=button_width)
                    dpg.add_button(label="Reset", callback=self.reset_operation, width=button_width)
                dpg.add_separator()

                dpg.add_text("Child Operations:")
                self.child_ops_parent = f"child_ops_{self.unique_id}"
                with dpg.group(tag=f"container_{self.unique_id}"):
                    with dpg.group(tag=self.child_ops_parent):
                        if self._operation.child_operations:
                            for child_op in self._operation.child_operations:
                                dpg.add_text(
                                    label=f"Child Operation: {child_op.name} - Status: {child_op.status} - "
                                          f"Concurrent: {child_op.concurrent}",
                                    parent=self.child_ops_parent
                                )
                                dpg.add_separator()

                    dpg.add_separator()
                    dpg.add_button(
                        label="Execute Child Operations",
                        callback=self._operation.execute_child_operations,
                        width=-1, parent=f"container_{self.unique_id}"
                    )
                    create_operation_module = CreateOperationModule(operation_control=self.operation_control,
                                                                    width=700,
                                                                    height=400,
                                                                    parent_operation=self._operation)
                    create_operation_module.draw_button(parent=f"container_{self.unique_id}",
                                                        label="Add Child Operation")

            child_height = int((self.height * 0.85) * 0.5) - 18
            with dpg.child_window(height=int(self.height * 0.85) - 12, width=int(self.width * 0.6) - 10, border=True):
                logs_results_tag = f"logs_results_{self.unique_id}"
                with dpg.group(tag=logs_results_tag, width=-1, height=child_height):
                    with dpg.child_window(border=False, parent=logs_results_tag):
                        dpg.add_text("Logs")
                        dpg.add_separator()
                        log_container_id = f"log_container_{self.unique_id}"
                        with dpg.child_window(tag=log_container_id, width=-1, border=False):
                            for log in self._operation.operation_logs:
                                dpg.add_text(log, parent=log_container_id)

                    dpg.add_separator()

                    with dpg.child_window(border=False, parent=logs_results_tag):
                        dpg.add_text("Result")
                        dpg.add_separator()
                        dpg.add_input_text(tag=self.result_id, readonly=True, multiline=True, width=-1)
                        dpg.add_separator()
                        dpg.add_button(label="View Result", callback=self.view_result, width=-1)

    async def update_gui(self) -> None:
        """Updates the GUI with the current status and progress."""
        while True:
            if dpg.does_item_exist(f"status_{self._operation.name}_{self.unique_id}"):
                dpg.set_value(f"status_{self._operation.name}_{self.unique_id}", f"Status: {self._operation.status}")

            if dpg.does_item_exist(f"progress_{self._operation.name}_{self.unique_id}"):
                dpg.set_value(f"progress_{self._operation.name}_{self.unique_id}", self._operation.progress[0] / 100)
                dpg.configure_item(f"progress_{self._operation.name}_{self.unique_id}",
                                   overlay="%.1f%%" % self._operation.progress[0])

            if dpg.does_item_exist(self.log_container_id):
                logs = self._operation.operation_logs
                children = dpg.get_item_children(self.log_container_id, slot=1)
                if len(children) != len(logs):
                    dpg.delete_item(self.log_container_id, children_only=True)
                    for log in logs:
                        dpg.add_text(log, parent=self.log_container_id)

            if dpg.does_item_exist(self.child_ops_parent):
                current_child_operations = {child_op.name for child_op in self._operation.child_operations}
                existing_children = {dpg.get_item_label(child) for child in
                                     dpg.get_item_children(self.child_ops_parent, slot=0)}

                # Remove old child operations
                for child in existing_children - current_child_operations:
                    for child_id in dpg.get_item_children(self.child_ops_parent, slot=0):
                        if dpg.get_item_label(child_id) == child:
                            dpg.delete_item(child_id)

                # Add new child operations
                for child_op in self._operation.child_operations:
                    if child_op.name not in existing_children:
                        dpg.add_text(
                            f"Child Operation: {child_op.name} - Status: {child_op.status} - Concurrent: {child_op.concurrent}",
                            parent=self.child_ops_parent, wrap=200, bullet=True)

            if dpg.does_item_exist(self.result_id):
                result = self._operation.get_result()
                dpg.set_value(self.result_id, str(result))

            if dpg.does_item_exist(self.persistent_id):
                dpg.set_value(self.persistent_id, f"Persistent: {self._operation.persistent}")

            if dpg.does_item_exist(self.cpu_bound_id):
                dpg.set_value(self.cpu_bound_id, f"CPU Bound: {self._operation.is_cpu_bound}")

            await asyncio.sleep(0.05)

    def view_result(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Handles the event when the user clicks the 'View Result' button."""
        result = self._operation.get_result()
        self._operation.add_log_entry(f"Result viewed: {result}")

    async def add_child_operation(self, child_operation: ABCOperation) -> None:
        """Adds a child operation to the current operation."""
        await self._operation.add_child_operation(child_operation)

    def remove_child_operation(self, child_operation: ABCOperation) -> None:
        """Removes a child operation from the current operation."""
        self._operation.remove_child_operation(child_operation)
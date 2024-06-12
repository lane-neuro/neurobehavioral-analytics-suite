# WorkspaceModule.py

import asyncio
import os
import uuid
from typing import Optional, Any

import dearpygui.dearpygui as dpg

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class WorkspaceModule:
    """A class to manage the GUI representation of the Workspace."""

    def __init__(self, workspace: Workspace, operation_control, width: int, height: int):
        """
        Initializes the WorkspaceModule with the given workspace.

        Args:
            workspace (Workspace): An instance of Workspace.
            operation_control: The operation control instance.
            width (int): The width of the module.
            height (int): The height of the module.
        """
        self.workspace = workspace
        self._operation_control = operation_control
        self.width = width
        self._user_vars_width = int(self.width * 0.6)
        self._management_width = int(self.width * 0.31)
        self.height = height
        self._logger = CustomLogger()
        self._config = Config()
        self.update_operation = None
        self.unique_id = str(uuid.uuid4())
        self.user_var_list_id = f"user_var_list_{self.unique_id}"
        self.add_var_dialog_id = None
        self.user_vars = {}  # Store user variables

    async def initialize(self) -> None:
        """Initializes resources and sets up the GUI."""
        self.initialize_resources()
        await self.setup_workspace_pane()
        self.update_operation = await self.add_update_operation()

    async def add_update_operation(self) -> Optional[Any]:
        try:
            operation = await self._operation_control.operation_manager.add_operation(
                operation_type=ABCOperation, name="gui_WorkspaceUpdateTask",
                local_vars=self._operation_control.local_vars,
                func=self.update_user_variables_list, persistent=True, concurrent=True)
            operation.is_ready = True
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    def initialize_resources(self) -> None:
        """Initializes necessary resources and logs the event."""
        pass

    async def setup_workspace_pane(self) -> None:
        """Sets up the workspace pane asynchronously."""
        with dpg.group(tag="workspace_pane_group", horizontal=True, parent="workspace_group"):

            with dpg.child_window(tag="user_variables_pane",
                                  width=self._user_vars_width,
                                  border=True, parent="workspace_pane_group"):
                dpg.add_text("User Variables")
                dpg.add_separator()
                dpg.add_button(label="Add User Variable", callback=self.open_add_var_dialog)
                dpg.add_group(tag=self.user_var_list_id)  # Create the group for user variables list

            with dpg.child_window(tag="workspace_management_pane", width=self._management_width, border=True,
                                  parent="workspace_pane_group"):
                dpg.add_text("Workspace Details")
                dpg.add_separator()
                dpg.add_button(label="Save Workspace", callback=self.save_workspace)
                dpg.add_button(label="Load Workspace", callback=self.load_workspace)
                dpg.add_separator()
                dpg.add_text("Workspace Name:")
                dpg.add_input_text(tag="workspace_name_input", default_value="default_name")
                dpg.add_separator()

                dpg.add_text("Backup and Restore")
                dpg.add_separator()
                dpg.add_button(label="Backup User Variables", callback=self.backup_user_variables)
                dpg.add_button(label="Restore User Variables", callback=self.restore_user_variables)
                dpg.add_separator()
                dpg.add_text("Backup File Path:")
                dpg.add_input_text(tag="backup_path_input",
                                   default_value=os.path.join(self._config.BASE_DIR, 'user_variables_backup.db'))

    async def update_user_variables_list(self) -> None:
        """Updates the user variables list in the GUI."""
        while True:
            try:
                new_user_vars = await self.workspace.list_user_variables()
                new_user_vars_dict = {}

                if isinstance(new_user_vars, dict):
                    for var in new_user_vars:
                        if isinstance(var, dict) and 'name' in var:
                            name = var['name']
                            value = await self.workspace.get_user_variable(name)
                            new_user_vars_dict[name] = value
                        elif isinstance(var, str):
                            name = var
                            value = await self.workspace.get_user_variable(name)
                            new_user_vars_dict[name] = value
                        else:
                            self._logger.error(Exception(f"Unexpected variable structure: {var}", self))
                else:
                    self._logger.error(Exception("Expected list of user variables, got something else", self))

                # Update existing variables and add new ones
                for name, value in new_user_vars_dict.items():
                    if name in self.user_vars:
                        if self.user_vars[name] != value:
                            dpg.set_value(f"user_var_value_{name}", value)
                    else:
                        self.add_user_variable_to_gui(name, value)

                # Remove old variables
                for name in list(self.user_vars.keys()):
                    if name not in new_user_vars_dict:
                        self.remove_user_variable_from_gui(name)

                self.user_vars = new_user_vars_dict
            except Exception as e:
                self._logger.error(Exception(f"Error updating user variables: {e}", self))
            await asyncio.sleep(0.1)

    def add_user_variable_to_gui(self, name: str, value: str) -> None:
        """Adds a user variable to the GUI."""
        with dpg.group(parent=self.user_var_list_id, tag=f"user_var_group_{name}"):
            dpg.add_text(f"Name: {name}, Value: ", parent=f"user_var_group_{name}")
            dpg.add_text(value, tag=f"user_var_value_{name}", parent=f"user_var_group_{name}")
            dpg.add_button(label=f"Remove {name}",
                           callback=lambda s, a, u=name: asyncio.create_task(self.remove_user_variable(u)),
                           parent=f"user_var_group_{name}")

    def remove_user_variable_from_gui(self, name: str) -> None:
        """Removes a user variable from the GUI."""
        dpg.delete_item(f"user_var_group_{name}")

    async def add_user_variable(self, name, value) -> None:
        """Adds a user variable."""
        try:
            await self.workspace.add_user_variable(name, value)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add user variable '{name}': {e}", self))

    async def remove_user_variable(self, name) -> None:
        """Removes a user variable."""
        try:
            await self.workspace.remove_user_variable(name)
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove user variable '{name}': {e}", self))

    async def backup_user_variables(self) -> None:
        """Backups the user variables."""
        try:
            backup_path = dpg.get_value("backup_path_input")
            await self.workspace.backup_user_variables(backup_path)
            self._logger.info(f"User variables backed up to {backup_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to backup user variables: {e}", self))

    async def restore_user_variables(self) -> None:
        """Restores the user variables."""
        try:
            backup_path = dpg.get_value("backup_path_input")
            await self.workspace.restore_user_variables(backup_path)
            self._logger.info(f"User variables restored from {backup_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to restore user variables: {e}", self))

    async def save_workspace(self) -> None:
        """Saves the current workspace."""
        try:
            await self.workspace.save_current_workspace()
            self._logger.info("Workspace saved successfully")
        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}", self))

    async def load_workspace(self) -> None:
        """Loads a workspace."""
        try:
            workspace_path = dpg.get_value("workspace_path_input")
            await self.workspace.load_workspace(workspace_path)
            self._logger.info("Workspace loaded successfully")
        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}", self))

    def open_add_var_dialog(self) -> None:
        """Opens a dialog to add a user variable."""
        if self.add_var_dialog_id is None:
            self.add_var_dialog_id = dpg.generate_uuid()
            with dpg.window(label="Add User Variable", modal=True, tag=self.add_var_dialog_id):
                dpg.add_input_text(label="Variable Name", tag="var_name_input")
                dpg.add_input_text(label="Variable Value", tag="var_value_input")
                dpg.add_button(label="Add", callback=lambda: asyncio.create_task(self.add_user_variable_from_dialog()))
                dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(self.add_var_dialog_id))
        else:
            dpg.show_item(self.add_var_dialog_id)

    async def add_user_variable_from_dialog(self) -> None:
        """Adds a user variable from the dialog inputs."""
        try:
            name = dpg.get_value("var_name_input")
            value = dpg.get_value("var_value_input")
            await self.add_user_variable(name, value)
            dpg.hide_item(self.add_var_dialog_id)
        except Exception as e:
            self._logger.error(Exception(f"Error adding user variable: {e}", self))

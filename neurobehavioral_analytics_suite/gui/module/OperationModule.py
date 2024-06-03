import asyncio
import uuid
import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.operation_manager.operation.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation


class OperationModule:
    def __init__(self, operation: Operation, operation_control, logger):
        self.current_items = []
        self.operation = operation
        self.operation_control = operation_control
        self.logger = logger
        self.update_operation = None
        self.unique_id = None
        self.log_id = None

    async def initialize(self):
        await self.initialize_resources()
        self.update_operation = await self.add_update_operation()

    async def initialize_resources(self):
        try:
            self.log_event("Resources initialized.")
        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
            self.operation.status = "error"
            self.log_event(f"Error during initialization: {e}")

    async def add_update_operation(self):
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=CustomOperation, name="gui_OperationUpdateTask",
                local_vars=self.operation_control.local_vars, error_handler=self.operation_control.error_handler,
                func=self.update_gui, persistent=True)
            return operation
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            self.log_event(f"Error creating task: {e}")
        return None

    async def start_operation(self, sender, app_data, user_data):
        try:
            await self.operation.start()
        except Exception as e:
            self.logger.error(f"Error starting operation: {e}")
            self.operation.status = "error"
            self.log_event(f"Error starting operation: {e}")

    async def stop_operation(self, sender, app_data, user_data):
        try:
            await self.operation.stop()
        except Exception as e:
            self.logger.error(f"Error stopping operation: {e}")
            self.operation.status = "error"
            self.log_event(f"Error stopping operation: {e}")

    async def pause_operation(self, sender, app_data, user_data):
        try:
            await self.operation.pause()
        except Exception as e:
            self.logger.error(f"Error pausing operation: {e}")
            self.operation.status = "error"
            self.log_event(f"Error pausing operation: {e}")

    async def resume_operation(self, sender, app_data, user_data):
        try:
            await self.operation.resume()
        except Exception as e:
            self.logger.error(f"Error resuming operation: {e}")
            self.operation.status = "error"
            self.log_event(f"Error resuming operation: {e}")

    async def reset_operation(self, sender, app_data, user_data):
        try:
            await self.operation.reset()
        except Exception as e:
            self.logger.error(f"Error resetting operation: {e}")
            self.operation.status = "error"
            self.log_event(f"Error resetting operation: {e}")

    def draw(self, parent):
        with dpg.group(parent=parent):
            dpg.add_text(f"Operation: {self.operation.name}")
            self.unique_id = str(uuid.uuid4())
            self.log_id = f"log_{self.unique_id}"
            dpg.add_text(f"Status: {self.operation.status}", tag=f"status_{self.operation.name}_{self.unique_id}")
            dpg.add_progress_bar(default_value=self.operation.progress[0] / 100, tag=f"progress_{self.operation.name}_{self.unique_id}", overlay="%.1f%%" % self.operation.progress[0], width=dpg.get_item_width(parent)-20)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start", callback=self.start_operation)
                dpg.add_button(label="Stop", callback=self.stop_operation)
                dpg.add_button(label="Pause", callback=self.pause_operation)
                dpg.add_button(label="Resume", callback=self.resume_operation)
                dpg.add_button(label="Reset", callback=self.reset_operation)
            dpg.add_text("Logs:")
            dpg.add_listbox(items=[], num_items=5, tag=self.log_id, width=dpg.get_item_width(parent)-20)
            dpg.add_text("Child Operations:")
            for child_op in self.operation.child_operations:
                dpg.add_text(f"Child Operation: {child_op.name} - Status: {child_op.status}")
        self.operation.attach_gui_module(self)

    async def update_gui(self):
        while True:
            if dpg.does_item_exist(f"status_{self.operation.name}_{self.unique_id}"):
                dpg.set_value(f"status_{self.operation.name}_{self.unique_id}", f"Status: {self.operation.status}")
            if dpg.does_item_exist(f"progress_{self.operation.name}_{self.unique_id}"):
                dpg.set_value(f"progress_{self.operation.name}_{self.unique_id}", self.operation.progress[0])
            dpg.set_value(f"log_{self.unique_id}", self.current_items)
            await asyncio.sleep(.25)

    def log_event(self, message: str):
        self.current_items.append(message)

    # Child Operation Management
    def add_child_operation(self, child_operation):
        self.operation.add_child_operation(child_operation)

    def remove_child_operation(self, child_operation):
        self.operation.remove_child_operation(child_operation)

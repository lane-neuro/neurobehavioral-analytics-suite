"""
A module for launching the NeuroBehavioral Analytics Suite.

This module contains the main entry point for launching the NeuroBehavioral Analytics Suite. It includes functions
for parsing command line arguments and launching the application.

Author: Lane
"""

import argparse
import asyncio
import logging

import nest_asyncio

from neurobehavioral_analytics_suite.gui.GuiLauncher import GuiLauncher
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger
from neurobehavioral_analytics_suite.data_engine.Workspace import Workspace
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


async def launch_nbas():
    """
    Launches the NeuroBehavioral Analytics Suite.

    This function checks the command line arguments to determine whether to create a new project or open an existing
    one. It then initializes the asyncio event loop and starts the application.

    Raises:
        AssertionError: If no active project is open.
    """
    nest_asyncio.apply()
    args = launch_args().parse_args()
    print("Initiating CustomLogger - Logging Level: INFO")
    logger = CustomLogger(logging.INFO)
    error_handler = ErrorHandler()
    launch_tasks = []

    # Initialize Workspace
    workspace = Workspace(logger=logger, error_handler=error_handler)

    # Checks args for -o '--open_project' flag.
    # If it exists, open the project from the file
    if args.open_project is None:
        logger.info('New Project Parameters Detected - Creating New Project')
        data_engine = workspace.create_project(args.directory, args.user_name, args.subject_name,
                                               args.camera_framerate, args.file_list)
    else:
        logger.info('Project File Detected - Loading Project at: ' + args.open_project)
        data_engine = workspace.load_workspace(args.open_project)

    nest_asyncio.apply()
    operation_control = OperationControl(logger=logger, error_handler=error_handler, workspace=workspace)

    launch_tasks.append(operation_control.exec_loop())
    gui_launcher = None

    if args.gui is not None and args.gui.lower() == 'true':
        try:
            gui_launcher = GuiLauncher(data_engine=data_engine, operation_control=operation_control,
                                       logger=logger, error_handler=error_handler, workspace=workspace)
        except Exception as e:
            logger.error(f"launch_nbas: {e}")
        finally:
            launch_tasks.append(gui_launcher.setup_main_window())

    logger.info("Launching NBAS")

    try:
        await asyncio.gather(*launch_tasks)
    except Exception as e:
        logger.error(f"launch_nbas: {e}")
    finally:
        logger.info("Cleaning up...")
        workspace.save_current_workspace()
        logger.info("Exiting NeuroBehavioral Analytics Suite...")
        asyncio.get_event_loop().close()


def launch_args():
    """
    Parses command line arguments for launching the NeuroBehavioral Analytics Suite.

    The arguments include options for opening an existing project, creating a new project, and specifying various
    project parameters.

    Returns:
        argparse.ArgumentParser: The argument parser with the parsed command line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-g', '--gui', help='Launches the NeuroBehavioral Analytics Suite GUI')
    parser.add_argument('-o', '--open_project', help='Opens an existing project from the specified file')
    parser.add_argument('-u', '--user_name', help='Name of user/experimenter')
    parser.add_argument('-d', '--directory', help='Directory where project files will be located')
    parser.add_argument('-s', '--subject_name', help='Name of the experimental subject (e.g., mouse, human, etc.)')
    parser.add_argument('-f', '--file_list', help='List of files containing experimental data')
    parser.add_argument('-c', '--camera_framerate', help='Camera Framerate')

    return parser

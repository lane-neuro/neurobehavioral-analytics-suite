"""
This modules serves as the main entry point for running the NeuroBehavioral AnalyticsCore Suite.

It contains the main function which initiates the suite and sets up the necessary parameters.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import asyncio
import sys
from neurobehavioral_analytics_suite.launch_nbas import launch_nbas


def main():
    """
    Initiates the NeuroBehavioral AnalyticsCore Suite.

    This function prints the version of the suite, imports the launch_nbas modules,
    and calls it to start the suite.
    """
    print('Starting NeuroBehavioral AnalyticsCore Suite v0.0.0.1')
    try:
        asyncio.run(launch_nbas())
    except KeyboardInterrupt:
        print('Exiting NeuroBehavioral AnalyticsCore Suite...')
    finally:
        print("Cleaning up...")
        asyncio.get_event_loop().close()
        sys.exit(0)


if __name__ == '__main__':
    sys.argv = ['__main__.py',
                '-g', 'True',
                '-u', 'dev_test',
                '-d', '..\\..\\NBAS-test-output\\',
                '-s', 'Mouse',
                '-c', '60',
                '-f', '..\\sample_datasets\\2024-Tariq-et-al_olfaction\\9-2-2021-4-07 PM-Mohammad-ETHSensor-CB5-28_'
                      'reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv']
    main()

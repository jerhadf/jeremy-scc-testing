# env/bin/python
"""
A generic test runner that is customizable through values read from a config file.

functions:
    load_config     Adds a custom dictionary to the master config dictionary.
    get_config      Gets a value from the master config dictionary.
    set_config      Adds a key,value pair to the master config dictionary.
    run             Runs the tests specified in the config file using an xmlrunner.

constants:
    CONFIG_FILE     The master config dictionary. As the implementation of config value storage may change, it is
                    recommended that this should not be accessed directly. Instead, the load_config, get_config and
                    set_config functions should be used.
"""

import argparse
import json
import unittest
import importlib
import xmlrunner
from pylat.configvalues import USE_QB
#from pylat.setuptests import qb

CONFIG_FILE = {}


def load_config(config):
    """
    Add a dictionary to the master config dictionary.

    load_config provides a convenient way to add large numbers of key,value pairs at one time. The result of calling
    load_config is the same as calling set_config for each key,value pair in the dictionary passed into load_config.
    """

    CONFIG_FILE.update(config)


def get_config(key):
    """Return a value (specified by 'key') from the master config dictionary."""
    if key in CONFIG_FILE:
        return CONFIG_FILE[key]
    return None


def set_config(key, value):
    """Set a key,value pair in the master config dictionary."""

    CONFIG_FILE[key] = value


def run():
    """
    Run a set of specified tests using xmlrunner.

    This function should be the last command called in the if __name__ == ("__main__") conditional of a unittest module.
    The config file is passed as a command line argument into the module calling this function, and it must contain
    the key "tests" that points to an Array of test module names that should be run.
    """

    parser = argparse.ArgumentParser(
        description="Test Runner for Jenkins Tests.")

    parser.add_argument('-c', '--config', type=argparse.FileType('r'), help="Name of the configuration file that contains the correct \
     system info to test against", required=True)
    parser.add_argument('-l', '--loop', type=int, help="Number of times to loop the tests", default=1)
    args = parser.parse_args()
    # TODO: Write Some Sort of config file parser to detect invalid config files
    load_config(json.load(args.config))
    testCases = map(importlib.import_module, CONFIG_FILE['tests'])
    # if a test suite is specified, try to get test suite parameters
    try: runSuite = (CONFIG_FILE['run_suite'])
    except: runSuite = False
    if runSuite:
        try:
            testSuiteClass = map(importlib.import_module, CONFIG_FILE['test_suite_class'])
            testSuiteClassName = CONFIG_FILE['test_suite_class']
            testSuiteCases = CONFIG_FILE['test_suite']
        except:
            print("Test suite parameters incomplete, please provide test_suite_class and test_suite config file variables")
            return
    # if test setup is specified, try to get test suite parameters
    try:
        testSetup = (CONFIG_FILE['setup_test'])
    except:
        testSetup = False
    #If test setup is specified, try to get test setup parameters
    if testSetup:
        try:
            testSetupCases = map(importlib.import_module, CONFIG_FILE['test_setup'])
        except:
            print("Test setup selected but no test_setup variable set")
            return
    setupCases = []
    testSetupArray = []
    if testSetup:
        testSetupArray.extend(testSetupCases)
        testSetupSuite = unittest.TestSuite([unittest.TestLoader().loadTestsFromModule(case) for case in testSetupArray])
        xmlrunner.XMLTestRunner(output='test-reports').run(testSetupSuite)
    if runSuite:
        testSuite = unittest.TestSuite([unittest.TestLoader().loadTestsFromName('{}.{}'.format(testSuiteClassName[0], testSuiteCases[case])) for case in range(len(testSuiteCases))])
        xmlrunner.XMLTestRunner(output='test-reports').run(testSuite)
    else:
        # if get_config(USE_QB):
        #     setupCases.append(qb)
        setupCases.extend(testCases)
        testSuite = unittest.TestSuite([unittest.TestLoader().loadTestsFromModule(case) for case in setupCases])
        for i in range(args.loop):
            xmlrunner.XMLTestRunner(output='test-reports').run(testSuite)
            
if __name__ == "__main__":
    run()
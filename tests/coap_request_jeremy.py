import unittest
import random
import json
from . import scc
from pylat import get_config

import abc

class Coap_Request_Tests(unittest.TestCase):
    available_endpoints = []

    @abc.abstractmethod
    def GET_coap(self, endpoint, proxy="::1"):
        pass

    @abc.abstractmethod
    def DELETE_coap(self, endpoint, proxy="::1"):
        pass

    @abc.abstractmethod
    def POST_coap(self, endpoint, payload=None, proxy="::1"):
        pass

    def __jsonify(self, strToJson):
        failed = False
        try:
            toRet = json.loads(strToJson)
        except ValueError:
            failed = True
        finally:
            if failed:
                self.fail("Couldn't convert '{}' to json.".format(strToJson))
                return None
            else:
                return toRet

    ###JEREMY FACTORY RESET TEST
    def test_fac_rst(self):
        """Perform factory reset on specified device and verify that the device paremeters were reset to defaults."""

        # if the dataCmd CoAP endpoint is not available for the current device, skip this test
        if "dataCmd" not in self.available_endpoints: self.skipTest("Factory Reset not available") 
        
        self.available_endpoints.remove("dataCmd")
        print("\n---STARTING FACTORY RESET TEST---")

        facResetData = self.GET_coap("dataCmd?default=3")['Data'][1:-1] # run factory reset command and grab data from output

        # assert that all the expected keys exist in the output data for the dataCmd
        self.assertIn("m", facResetData.keys())
        self.assertIn("d", facResetData.keys())
        self.assertIn("n", facResetData["m"].keys())
        self.assertIn("v", facResetData["m"].keys())
        self.assertIn("t", facResetData["m"].keys())
        self.assertIn("default", facResetData["d"].keys()) 

        # verify that all the values in the data dictionary match what we expect
        manLogData = self.GET_coap("dataManagerLog?force=1")['Data'][1:-1]
        toTest = []

        # dictionary of all default values
        defaultVals = { #! this is currently empty - the below is just a template for what it would be
            'dname':'default', 
            'Voltage':'default value', 
            'ZeroX On':'default value'
        }

        # parse the data output of the dataManagerLog endpoint; append the value of each "dname" key to the toTest list
        for item in manLogData.split(","):
            if len(item.split(":",1))==2:
                k,v = item.split(":",1)
                if "dname" in k: toTest.append(v[1:-1].replace(" ", "_"))

        # hit each endpoint in the toTest list using the dd command (e.g. coap://[::-1]/dd/[endpoint]). 
        for ep in toTest:
            curr_dd_results = self.GET_coap("dd/{0}".format(ep))
            if curr_dd_results==None: self.fail("data == None.")
            data = self.__jsonify(curr_dd_results['Data'][1:-1]) # convert the dd output to JSON format
            #! below is just speculation on what the assert would be (not working!) 
            #! test fails if any of the actual default values are not equal to expected default values 
            self.assertEqual(data['default'], defaultVals[ep], "default value is {0}. should be {1}".format(data['default'], defaultVals[ep]))

    @classmethod
    def tearDownClass(cls):
        """Runs after all test_* functions."""
        if len(cls.available_endpoints) > 0:
            print("\n\n-------- NOT TESTED ---------")
            print(", ".join(cls.available_endpoints))


if __name__ == '__main__':
    unittest.main()
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
                
###SWINFO TEST ----------------------------------------------------------------
    def test_SWInfo(self):
        """Query SWInfo, verify Name and Version are in the response data."""
        if "SWInfo" not in self.available_endpoints: self.skipTest("SWInfo not available")
        self.available_endpoints.remove("SWInfo")
        print("\n---STARTING SWInfo TEST---")

        swInfo = self.GET_coap("SWInfo")['Data'][1:-1]
        swInfoData = self.__jsonify(swInfo)
        print(swInfoData)
        self.assertIn("Name", swInfoData.keys())
        self.assertIn("Version", swInfoData.keys())

    @classmethod
    def tearDownClass(cls):
        """Runs after all test_* functions."""
        if len(cls.available_endpoints) > 0:
            print("\n\n-------- NOT TESTED ---------")
            print(", ".join(cls.available_endpoints))


if __name__ == '__main__':
    unittest.main()
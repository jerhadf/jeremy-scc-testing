from . import coap_request_tests
from . import scc
from pylat import get_config

class Test_BLE_Device(coap_request_tests.Coap_Request_Tests):
    available_endpoints = []

    @classmethod
    def setUpClass(cls):
        """Set up the class variables.
        Call well-known/core endpoint, create a list of available endpoints
        """
        cls.sccPath = get_config("scc_path")
        cls.mac = get_config("device_MAC") # check here to see if list; run against list of devices or single
        cls.outputFile = get_config("output_file")

        wellKnown = scc.run_scc(cls.sccPath, "--mac {0} --type GET --url coap://[::1]/.well-known/core".format(cls.mac), cls.outputFile)
        data = wellKnown['Data'].split(',')
        cls.available_endpoints = [d.split('>')[0][2:] for d in data]
        #cls.available_endpoints = ["lock", "login"] #fill this list to test specific endpoints.

    def GET_coap(self, endpoint, proxy="::1"):
        return scc.run_scc(self.sccPath, "--mac {0} --type GET --url coap://[{1}]/{2}".format(self.mac, proxy, endpoint), self.outputFile)
    
    def DELETE_coap(self, endpoint, proxy="::1"):
        return scc.run_scc(self.sccPath, "--mac {0} --type DELETE --url coap://[{1}]/{2}".format(self.mac, proxy, endpoint), self.outputFile)

    def POST_coap(self, endpoint, payload=None, proxy="::1"):
        requestString = "--mac {0} --type POST --url coap://[{1}]/{2}".format(self.mac, proxy, endpoint)
        if payload != None:
            requestString = requestString + " --payload {}".format(payload)
        return scc.run_scc(self.sccPath, requestString, self.outputFile)
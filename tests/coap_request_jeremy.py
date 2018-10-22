import unittest
import random
import json
from . import scc

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
        # if the FacRst CoAP endpoint is not available for the current device, skip this test
        # ? what name should the endpoint be? ("FacRst" will not appear in any available_endpoints list)
        if "dataCmd" not in self.available_endpoints: self.skipTest("Factory Reset not available") # self.available_endpoints is defined in a subclass of this class
        
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

        #TODO: find an endpoint that allows you to query the device for its parameters
        #TOdO: write code to verify that the device's parameters match the expected default values after the dataCmd is run

###.WELL-KNOWN/CORE TEST ---------------------------------------------------------------
    def test_wellKnown_core(self):
        """GET each of the available endpoints returned from /.well-known/core query"""
        if ".well-known/core" not in self.available_endpoints: self.skipTest(".well-known/core not available")
        self.available_endpoints.remove(".well-known/core")
        print("\n---STARTING .WELL-KNOWN/CORE TEST---")

        for ep in self.available_endpoints:
            if ep not in ["netkey", "writepage"]:
                results = self.GET_coap(ep)
                self.assertGreater(len(results['Time']), 0, "All scc calls should return an execution time")
                self.assertEqual(results['Error'], "", "An error occured with the scc call.")


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


###DD TEST ----------------------------------------------------------------
    def test_DD(self):
        """Query the data dictionary for a few parameters."""
        if "dd" not in self.available_endpoints: self.skipTest("dd is not available")
        self.available_endpoints.remove("dd")
        print("\n---STARTING DD TEST---")

        #check RSSI
        current_dd_results = self.GET_coap("dd/RSSI")
        if current_dd_results==None: self.fail("data == None.")
        data = self.__jsonify(current_dd_results['Data'][1:-1])
        self.assertEqual(data['dname'], "RSSI", "dname is {0}. should be RSSI.".format(data['dname']))
        self.assertIn("-", data['cval'], "RSSI's cval should containt a '-'")
        self.assertEqual(data['un'], "dBm", "RSSI units should be 'dBm'")

        #check all items that come back from dataManagerLog endpoint.
        manLogData = self.GET_coap("dataManagerLog?force=1")['Data'][1:-1]
        toTest = []
        for item in manLogData.split(","):
            if len(item.split(":",1))==2:
                k,v = item.split(":",1)
                if "dname" in k: toTest.append(v[1:-1].replace(" ", "_"))
        for ep in toTest:
            current_dd_results = self.GET_coap("dd/{0}".format(ep))
            if current_dd_results==None: self.fail("data == None.")
            data = self.__jsonify(current_dd_results['Data'][1:-1])
            self.assertEqual(data['dname'].replace(" ", "_"), ep, "dname is {0}. should be {1}.".format(data['dname'], ep))


###DataManagerLog TEST ----------------------------------------------------------------
    def __extract_name_and_index(self, data):
        toRet = dict()
        if data==None: self.fail("data == None.")
        for item in self.__jsonify(data):
            if ('dname' in item) and ('idx' in item):
                toRet[item['dname'].replace(' ','_')] = item['idx']
            else:
                print("ERROR! dname and idx should exist in data.")
        return toRet
    def test_Data_Manager_Log(self):
        """Query /dataManagerLog with different force values, check each endpoint using /dd
        force (Verbosity) vals
        1 = Return all meaningful datapoints
        2 = Return every datapoint in the DD, across all force values
        3 = Return ever datapoint in the DD, without names or units !?
        4 = Returns an empty array for the one im working with….
        5 = Return only the data to be logged every 5 minutes
        6 = Return only writeable points
        7 = Return advanced/hidden config
        """
        if "dataManagerLog" not in self.available_endpoints: self.skipTest("dataManagerLog is not available")
        self.available_endpoints.remove("dataManagerLog")
        print("\n---STARTING TEST dataManagerLog---")

        tested_dd_eps = []
        to_test_eps = dict()

        #test verbosity = 1, 2, 3, 4, 5, 6, 7
        for verb in ["1", "2", "3", "4", "5", "6", "7"]:
            manLogData = self.GET_coap("dataManagerLog?force={0}".format(verb))['Data']
            to_test_eps = self.__extract_name_and_index(manLogData)
            for ep in to_test_eps.keys():
                if ep not in tested_dd_eps:
                    current_dd_results = self.GET_coap("dd/{0}".format(ep))['Data']
                    self.assertIn(ep, current_dd_results.replace(" ", "_"), "{0} should be in {1}".format(ep, current_dd_results.replace(" ", "_")))
                    self.assertIn('"idx":"{0}"'.format(to_test_eps[ep]), current_dd_results, "data dictionary index does not match.")
                    tested_dd_eps.append(ep)
          

###PNL_MODE TEST ----------------------------------------------------------------
    def test_pnl_mode(self):
        """Query pnl_mode, Enter then exit pnl_mode."""
        if "pnl_mode" not in self.available_endpoints: self.skipTest("pnl_mode is not available")
        self.available_endpoints.remove("pnl_mode")
        print("\n---STARTING TEST PNL_MODE---")
        
        pnlData = self.__jsonify(self.GET_coap("pnl_mode")['Data'])['d']
        self.assertIn(pnlData['val'], [0,1], "val should be either 0 or 1.")
        pnlVal = str(pnlData['val'])
        
        #change val (mode)
        valToSet = "0" if pnlVal=="1" else "1"
        self.GET_coap("pnl_mode?val={0}".format(valToSet))
        pnlData = self.__jsonify(self.GET_coap("pnl_mode")['Data'])['d']
        self.assertIn(str(pnlData['val']), valToSet, "val should be {0}".format(valToSet))

        #change val (mode) BACK
        self.GET_coap("pnl_mode?val={0}".format(pnlVal))
        pnlData = self.__jsonify(self.GET_coap("pnl_mode")['Data'])['d']
        self.assertIn(str(pnlData['val']), pnlVal, "val should be {0}".format(pnlVal))


###PTP_MODE TEST ----------------------------------------------------------------
    def test_ptp_mode(self):
        """Query ptp_mode, then enters and exits ptp_mode."""
        if "ptp_mode" not in self.available_endpoints: self.skipTest("ptp_mode is not available")
        self.available_endpoints.remove("ptp_mode")
        print("\n---STARTING TEST PTP_MODE---")

        ptpData = self.__jsonify(self.GET_coap("ptp_mode")['Data'])
        self.assertIn(ptpData['val'], [0,1], "val should be either 0 or 1.")
        ptpVal = str(ptpData['val'])
        
        #change val (mode)
        valToSet = "0" if ptpVal=="1" else "1"
        self.GET_coap("ptp_mode?val={0}".format(valToSet))
        ptpData = self.__jsonify(self.GET_coap("ptp_mode")['Data'])
        self.assertIn(str(ptpData['val']), valToSet, "val should be {0}".format(valToSet))

        #change val (mode) BACK
        self.GET_coap("ptp_mode?val={0}".format(ptpVal))
        ptpData = self.__jsonify(self.GET_coap("ptp_mode")['Data'])
        self.assertIn(str(ptpData['val']), ptpVal, "val should be back to {0}".format(ptpVal))

        for loadNum in ["1","2","3"]:
            self.GET_coap("ptp_mode?load={0}".format(loadNum))
            ptpData = self.__jsonify(self.GET_coap("ptp_mode")['Data'])
            self.assertIn(loadNum, ptpData['load'], "load shoudl be set to {0}".format(loadNum))


###ACTION TABLE TEST ---------------------------------------------------------------
###--TABLELIST test
###--FUNCTIONLIST test
    def test_action_table(self):
        """Query /tablelist for lists of linkIDs, query /functionlist for a list of linkIDs & names, query each linkID using /actiontable"""
        for ep in ["actiontable", "tablelist", "functionlist"]:
            if ep not in self.available_endpoints: self.skipTest("{0} is not available".format(ep))
        for ep in ["actiontable", "tablelist", "functionlist"]:
            self.available_endpoints.remove(ep)
        print("\n---STARTING TEST ACTION TABLE---")

        tableListData = self.__jsonify(self.GET_coap("tablelist")['Data'])
        links = []
        for link in tableListData:
            if ("lId" in link) and ("aFun" in link):
                links.append( (link["lId"], link["aFun"]) )
            else:
                print("ERROR! missing a linkID or function address.")

        functionListData = self.__jsonify(self.GET_coap("functionlist")['Data'])
        functions = dict()
        for fun in functionListData:
            if ("add" in fun) and ("str" in fun):
                functions[fun["add"]] = fun["str"]
            else:
                print("ERROR! missing a function address or name.")            

        for id,add in links:
            #find link in name in functionlist data
            self.assertIn(add, functions.keys(), "add:{0} is not in the fucntion list.".format(add))
            print("-=-=-= testing {0} =-=-=-".format(functions[add])) 
            #get link
            if id in [4]:
                print("{0} is not supported on cooja".format(functions[add]))
            else:
                actionTableResults = self.GET_coap("actiontable?linkID={0}".format(str(id)))
                self.assertIn("Ok", actionTableResults['Data'], "{0} did not return 'Ok'".format(str(id)))


###FADE CMD TEST ------------------------------------------------------------
    def test_fade_cmd(self):
        """Query /fadeCmd, change to new values, verify /fadeCmd Data changed"""
        if "fadeCmd" not in self.available_endpoints: self.skipTest("fadeCmd is not available")
        self.available_endpoints.remove("fadeCmd")
        print("\n---STARTING TEST FADE CMD---")
 
        current_fadeCmd_data = self.__jsonify(self.GET_coap("fadeCmd")['Data'])
        load_dict = current_fadeCmd_data['d']

        #find new values to set for fadeCmd, set using /fadeCmd?...
        mode = "1" if str(load_dict['mode1']) != "1" else "2"
        min_val = "10" if str(load_dict['min1']) != "10" else "15"
        max_val = "75" if str(load_dict['max1']) != "75" else "90"
        duty = "65" if str(load_dict['duty1']) != '65' else "85"
        self.GET_coap("fadeCmd?chan=1&mode={0}&min={1}&max={2}&duty={3}".format(mode, min_val, max_val, duty))

        current_fadeCmd_data = self.__jsonify(self.GET_coap("fadeCmd")['Data'])
        load_dict = current_fadeCmd_data['d']

        self.assertEqual(str(load_dict['mode1']), mode)
        self.assertEqual(str(load_dict['min1']), min_val)
        self.assertEqual(str(load_dict['max1']), max_val)
        # dutyComp1 = (int(max_val)-int(min_val)) /100
        # print(dutyComp1)
        # dutyComp1 = dutyComp1 * int(duty)
        # print(dutyComp1)
        # dutyComp1 = dutyComp1 + int(min_val)
        # print(dutyComp1)
        dutyComp = str( int(((int(max_val)-int(min_val))/100 * int(duty)) + int(min_val)) )
        #print( str(int(dutyComp1)), "::", dutyComp)
        self.assertEqual(str(load_dict['duty1']), dutyComp)


###NETWORK CFG TEST ----------------------------------------------------------
    def test_network_config(self):
        """change the channel, pan, and ttl. Verify that they changed. Change back to initial values."""
        if "networkCfg" not in self.available_endpoints: self.skipTest("networkCfg is not available")
        self.available_endpoints.remove("networkCfg")
        print("\n---STARTING NETWORK CONFIG TEST---")

        availableChannels = [11,13,14,15,16,17,19,20,21,23]
        #pan = any number between 1-65535
        availableTTL = [1,2,3,4,5,6,7,8,9,10]

        current_networkConfig_data = self.__jsonify(self.GET_coap("networkCfg")['Data'])
        cfgData = current_networkConfig_data['d']
        
        o_chan = cfgData['chan']
        o_pan = cfgData['pan']
        o_ttl = cfgData['ttl']
        availableChannels.remove(o_chan)
        availableTTL.remove(o_ttl)

        #set parameters
        new_chan = random.choice(availableChannels)
        new_pan = str(random.randint(2,65535))
        new_ttl = random.choice(availableTTL)

        for data in [(new_chan, new_pan, new_ttl), (o_chan, o_pan, o_ttl)]:
            self.GET_coap("networkCfg?chan={}&pan={}&ttl={}".format(data[0], data[1], data[2]))
            current_networkConfig_data = self.__jsonify(self.GET_coap("networkCfg")['Data'])
            cfgData = current_networkConfig_data['d']
            self.assertEqual(cfgData['chan'], data[0])
            self.assertEqual(cfgData['pan'], data[1])
            self.assertEqual(cfgData['ttl'], data[2])


###RADIO CFG TEST ----------------------------------------------------------
    def test_radio_cfg(self):
        """query /radioCfg. Change parameters & Verify. Change back to original values."""
        if "radioCfg" not in self.available_endpoints: self.skipTest("radioCfg is not available")
        self.available_endpoints.remove("radioCfg")
        print("\n---STARTING RADIO CONFIG TEST---")

        availableAnt = [0,1,2]
        availablePower = [-17,-12,-8,-6,-4,-3,-2,-1,0,1,2,3,4]

        current_networkConfig_data = self.__jsonify(self.GET_coap("networkCfg")['Data'])
        cfgData = current_networkConfig_data['d']

        o_ant = cfgData['ant']
        o_pow = cfgData['power']
        availableAnt.remove(o_ant)
        availablePower.remove(o_pow)

        #set parameters
        new_ant = random.choice(availableAnt)
        new_pow = random.choice(availablePower)

        #set new data, get /radioCfg, verify changes
        #revert changes, get /radioCfg, verify changes
        for data in [(new_ant, new_pow), (o_ant, o_pow)]:
            self.GET_coap("radioCfg?ant={}&power={}".format(data[0], data[1]))
            current_networkConfig_data = self.__jsonify(self.GET_coap("networkCfg")['Data'])
            cfgData = current_networkConfig_data['d']
            self.assertEqual(cfgData['ant'], data[0])
            self.assertEqual(cfgData['power'], data[1])


###LOCK TEST ---------------------------------------------------------------
###--LOGIN TEST
    def test_lock(self):
        """Verify unlocked, set the lock & verify, delete the lock & verify"""
        for ep in ["lock", "login"]:
            if ep not in self.available_endpoints: self.skipTest("{0} is not available".format(ep))
        for ep in ["lock", "login"]:
            self.available_endpoints.remove(ep)

        print("\n---STARTING TEST LOCK----")

        #{"K1HWMT":"kkytDzb5L-h2hqK-hYuE1p8xx5WxujnVoPPrUlLo-Zg="}
        lockPayload = '{"K1HWMT":"kkytDzb5L-h2hqK-hYuE1p8xx5WxujnVoPPrUlLo-Zg="}'
        loginPayload = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzaXRlIjoiSzFIV01UIiwicGVyIjoiMHg4MyIsImV4cCI6IjE1MTkyOTI4OTIiLCJ1aWQiOiJkcm9idWxpYWsifQ.rg3SNgzVHwI4MNTCQxXJcQpHnYDpGBEBZs9VWikSkQI'
        current_lock_state = self.GET_coap("lock")
        if ":" in current_lock_state['Data']:
            self.DELETE_coap("lock")
        current_lock_state = self.GET_coap("lock")
        self.assertIn("key", current_lock_state['Data'], "the lock shouldn't be set.")
        #attempt to login before setting the lock. check for 404 error.
        login_reply = self.POST_coap("login", loginPayload)
        self.assertIn("NetworkError(404)", login_reply['Error'], "logging in without a lock should produce a 404 error")
        

        #set the lock, verify that it returns the correct payload.
        current_lock_state = self.POST_coap("lock", lockPayload)
        self.assertIn("ok", current_lock_state['Data'], "lock should be  set")
        current_lock_state = self.GET_coap("lock")
        for val in lockPayload[1:-1].split(":"):
            self.assertIn(val[3:-3], current_lock_state['Data'])

        #######
        #TEST ENDPOINTS THAT CHANGE WHEN LOCKED HERE

        #attempt invalid login, check for 401 error
        login_reply = self.POST_coap("login", loginPayload[:-2])
        self.assertIn("NetworkError(401)", login_reply['Error'], "invalid login should produce 401 error")
        
        #attempt valid login. NOTE this should return a permission mask, not an 'ok'
        login_reply = self.POST_coap("login", loginPayload)
        self.assertIn("ok", login_reply['Data'], "login did not work")
        #######

        current_lock_state = self.DELETE_coap("lock")
        self.assertIn("ok", current_lock_state['Data'], "lock should removed")

        #attempt to login after lock has been deleted. check for 404 error
        login_reply = self.POST_coap("login", loginPayload)
        self.assertIn("NetworkError(404)", login_reply['Error'], "logging in without a lock should produce a 404 error")

###NEIGHBORS TEST ---------------------------------------------------------------
    def test_neighbors(self):
        """query for neighbor table, proxy ping (SWInfo) the addresses through the current device. check for valid ping response."""
        for ep in ["neighbors"]:
            if ep not in self.available_endpoints: self.skipTest("{0} is not available".format(ep))
        for ep in ["neighbors"]:
            self.available_endpoints.remove(ep)

        print("\n---STARTING NEIGHBORS TEST---")

        neighborsResult = self.GET_coap("neighbors")
        neighbors = self.__jsonify(neighborsResult['Data'])
        for ipv6Add in neighbors:
            result = self.GET_coap("SWInfo", proxy=ipv6Add)
            self.assertIn("Name", result['Data'])
            self.assertIn("Version", result['Data'])

        

    @classmethod
    def tearDownClass(cls):
        """Runs after all test_* functions."""
        if len(cls.available_endpoints) > 0:
            print("\n\n-------- NOT TESTED ---------")
            print(", ".join(cls.available_endpoints))


if __name__ == '__main__':
    unittest.main()
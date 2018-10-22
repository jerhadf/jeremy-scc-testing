import os
from subprocess import Popen, PIPE, run
from pprint import pprint
from time import sleep

# Various notes
# talk to Robert Daniels about resetting factory defaults using a COAP endpoint
# take the coap_request_tests.py file 

def run_scc(scc_path, scc_command, outputFile=None):
    """This function runs the solstice SCC command line tool.\n
    arg scc_path -- path to scc executable\n
    arg scc_command -- the full scc command\n
    \t--url {full coap url}\n
    \t--ha {host address of cooja}\n
    \t--payload {payload in text format}\n
    \t--mote {cooja mote identifier}\n
    \t--name {name of command}\n
    \t--devname {BLE device name}\n
    \t--bda {BDA address}\n
    \t--mac {DLMW-Wireless MAC Address (XX:XX:XX:XX:XX:XX)}
    
    outputFile is not used.
    """
 
    #this doesn't write to a file
    toRun = "{} {}".format(scc_path, scc_command)
    print("\n\n" + toRun + "\n")
    raw_res = run(toRun.split(" "), stderr=PIPE)
    res_list = raw_res.stderr.decode("utf-8").split("\n")
    results = [line for line in res_list if ":" in line]
    
    while 'Execute command' not in results[0]: results.remove(results[0])
    results.remove(results[0])

    toRet = (kvPair.split(':', 1) for kvPair in results if ":" in kvPair)
    toRet = dict((a.strip(),b.strip()) for a,b in toRet)
    pprint(toRet)
    return toRet

def run_interactive(scc_path, scc_commands, outputFile=None):
    """This function runs the Solstice CoAP Client command line tool in interactive mode.
    arg scc_path -- path to scc executable
    arg scc_commands -- a list of string, each string is a coap request to run.

    result:
    a list of dictionaries will be returned once the commands complete running
    """
    p = Popen("{} --i".format(scc_path).split(" "), stdout=PIPE, stderr=PIPE, stdin=PIPE)
    output=""
    while "Start" not in output and "Interactive" not in output:
        output = p.stderr.readline().decode('utf-8')
        print(output)

    toRet = []
    for cmd in scc_commands:
        cmdResponse = dict()
        
        #write 1 char at a time, followed by two new-lines
        toWrite = "{0}{1}{1}".format(cmd, os.linesep)
        for char in toWrite:
            sleep(0.001)
            p.stdin.write(bytes(char, 'utf-8'))
            p.stdin.flush()
        nextRes = p.stderr.readline().decode('utf-8')
        print(nextRes, end="")
        while "URL" not in nextRes:
            nextRes = p.stderr.readline().decode('utf-8')
            print(nextRes, end="")
        while "Time" not in nextRes:
            response = nextRes.split(":",1)
            cmdResponse[response[0].strip()] = response[1].strip()
            nextRes = p.stderr.readline().decode('utf-8')
            print(nextRes, end="")
        response = nextRes.split(":",1)
        cmdResponse[response[0].strip()] = response[1].strip()
        
        toRet.append(cmdResponse)
    for char in "quit{0}{0}".format(os.linesep):
        p.stdin.write(bytes(char, 'utf-8'))
        p.stdin.flush()
    return toRet


if __name__ == '__main__':
    #SWInfo
    run_scc('C:/Builds/solstice-testing/win32-msvc/debug/bin/tests/utilities/scc/scc.exe', '--ha 10.87.57.58 --mote 1 --type GET --url coap://[::1]/SWInfo')
    #lock
    run_scc('C:/Builds/solstice-testing/win32-msvc/debug/bin/tests/utilities/scc/scc.exe', '--ha 10.87.57.58 --mote 1 --type POST --url coap://[::1]/lock --payload {"""K1HWMT""":"""kkytDzb5L-h2hqK-hYuE1p8xx5WxujnVoPPrUlLo-Zg="""}')
    #login
    run_scc('C:/Builds/solstice-testing/win32-msvc/debug/bin/tests/utilities/scc/scc.exe', '--ha 10.87.57.58 --mote 1 --type POST --url coap://[::1]/login --payload eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzaXRlIjoiSzFIV01UIiwicGVyIjoiMHg4MyIsImV4cCI6IjE1MTkyOTI4OTIiLCJ1aWQiOiJkcm9idWxpYWsifQ.rg3SNgzVHwI4MNTCQxXJcQpHnYDpGBEBZs9VWikSkQI')


###Used to test interactive mode login on raspberry pi (via BLE)
#`mac 00:04:74:16:0e:c1 `type GET `url coap://[::1]/lock
#`mac 00:04:74:16:0e:c1 `type DELETE `url coap://[::1]/lock
#`mac 00:04:74:16:0e:c1 `type POST `url coap://[::1]/lock `payload {"K1HWMT":"kkytDzb5L-h2hqK-hYuE1p8xx5WxujnVoPPrUlLo-Zg="}
#`mac 00:04:74:16:0e:c1 `type POST `url coap://[::1]/login `payload eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzaXRlIjoiSzFIV01UIiwicGVyIjoiMHg4MyIsImV4cCI6IjE1MTkyOTI4OTIiLCJ1aWQiOiJkcm9idWxpYWsifQ.rg3SNgzVHwI4MNTCQxXJcQpHnYDpGBEBZs9VWikSkQI
#`mac 00:04:74:16:0e:c1 `type DELETE `url coap://[::1]/lock
    
#`mac 00:04:74:16:0A:7C `type POST `url coap://[::1]/lock `payload {"K1HWMT":"kkytDzb5L-h2hqK-hYuE1p8xx5WxujnVoPPrUlLo-Zg="}
#`mac 00:04:74:16:0A:7C `type POST `url coap://[::1]/login `payload eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzaXRlIjoiSzFIV01UIiwicGVyIjoiMHg4MyIsImV4cCI6IjE1MTkyOTI4OTIiLCJ1aWQiOiJkcm9idWxpYWsifQ.rg3SNgzVHwI4MNTCQxXJcQpHnYDpGBEBZs9VWikSkQI

#`mac 00:04:74:16:12:91 `type GET `url coap://[::1]/SWInfo


###Alternate payload for lock
#{"""K1HWMT""":"""kkytDzb5L-h2hqK-hYuE1p8xx5WxujnVoPPrUlLo-Zg="""}
#{"""TMWH1K""":"""L5bzDtykk-Kqh2h-oLlUrPPoVnjuxW5xx8p1EuYh-Zg="""}
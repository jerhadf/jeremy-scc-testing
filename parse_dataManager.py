import re 
import json


d = {}

# parse the output of the dataManagerLog into a dictionary
with open("dataManagerLog.txt") as f:

    output = ''
    

    for line in f:
        output = line[1:-1]  # remove square brackets

    output = output.split(",")

    for indx, item in enumerate(output): 
        output[indx] = output[indx].split(", ")

    dname_list = []
    cval_list = []

    for item in output: 
        for val in item:
            if "dname" in val:
                dname_list.append(val.split(":")[1][1:-1].replace(" ", "_"))
            if "cval" in val:
                cval_list.append(val.split(":")[1][1:-1].replace(" ", "_"))
    
    d = dict(zip(dname_list, cval_list))

with open('dataManagerLog.json', 'w') as outfile:
    json.dump(d, outfile, indent=2)

# compare the defaults.json and the dataManagerLog.json and create a JSON file with the differences between them
diffs = []
with open("dataManagerLog.json") as fileA: 
    data_output = json.load(fileA)
    
with open("defaults.json") as fileB:
    defaults = json.load(fileB)

print("-----IN DataManagerLog output BUT NOT IN defaults.json-----")
for key, value in data_output.items(): 
    if key not in defaults.keys():
        print(f"{key}:{value}")

print("-----IN defaults.json BUT NOT IN DataManagerLog output-----")
for key, value in defaults.items(): 
    if key not in data_output.keys():
        print(f"{key}:{value}")

import re 
import json

d = {}
with open("defaults.txt") as f:
    for line in f:
        if "const" in line: 
            dname = line.split("=")[1][3:-3].replace(" ", "_")
            dname = re.sub(r'\s+', '', dname)
        elif ".dflt" in line: 
            dval = line.split("=")[1]
            dval = re.sub(r'\s+', '', dval)
            d[dname] = dval
        else:
            continue

with open('defaults.json', 'w') as outfile:
    json.dump(d, outfile, indent=2)

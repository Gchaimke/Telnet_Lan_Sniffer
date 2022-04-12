
import re


data = open("out/172.18.119.34.conf","r").read()

regex  = re.compile("(.+)->.+",re.MULTILINE)

host_name = re.findall(regex, data)
if(len(host_name)>0):
    host_name=host_name[0]

with open(f"out/{host_name}.conf","w") as  file:
    for line in data:
        if line == "\n":
            continue
        file.write(line)


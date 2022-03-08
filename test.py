import re

data = open("test.conf","r")

regex  = re.compile("(.+)->.+",re.MULTILINE)

host_name = re.findall(regex, data.read())
if(len(host_name)>0):
    host_name=host_name[0]

with open(f"out/{host_name}.conf","w") as  file:
    for line in data.readlines():
        if line == "\n":
            continue
        file.write(line)


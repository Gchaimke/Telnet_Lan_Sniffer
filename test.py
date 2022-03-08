import re

data_file = open("test.conf", encoding='utf8')
data = data_file.read()
data_file.close()


def get_hostname(string):
    regex = re.compile("(.+)->.+", re.MULTILINE)
    host_name = re.findall(regex, string)
    if(len(host_name) > 0):
        return host_name[0]
    return "hostname_not_found"


def remove_empty_lines(string):
    new_string = ""
    data = string.splitlines()
    for line in data:
        if line == "":
            continue
        new_string += line+"\n"
    return new_string

host = get_hostname(data)
data = remove_empty_lines(data)

txt = f"""
new file name {host}
{data}
"""

print(txt)
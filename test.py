
from random import randint
import re


data = open("test.conf", "r").read()


def get_hostname(string: str) -> str:

    hostname_regex = re.compile(
        r"set (system )?host\W?name ([a-zA-Z0-9]*\S*[a-zA-Z0-9]*[^\\rn\s>])", re.MULTILINE)
    host_name = re.findall(hostname_regex, str(string))

    if host_name:
        host_name = host_name[0][1]
    else:
        hostname_regex = re.compile("(.+)->.+", re.MULTILINE)
        host_name = re.findall(hostname_regex, str(string))
        if host_name:
            host_name = host_name[0]
        else:
            host_name = f"NA_{randint(1,1000)}_"

    return host_name.replace(".", "").replace("\\r", "").replace("\\", "")


hostname = get_hostname(data)
print(hostname)

from TS_client import *

ts = TS_client()

data_file = open("test.conf", encoding='utf8')
data = data_file.read()
data_file.close()

host = ts.get_hostname(data)
data = ts.remove_empty_lines(data)

txt = f"""
new file name {host}
{data}
"""

print(txt)
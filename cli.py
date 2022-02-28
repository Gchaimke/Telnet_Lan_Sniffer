import os
from TS_client import *

header = """
===========================================================
    Telnet&SSH utility to grab configs from SSG and SRX
===========================================================

"""
menu1 = """
    --  Protocol selection  --
    1.Telnet
    2.SSH

"""

menu2 = """
    --  Ping  --
    1.Yes
    2.No

"""

menu3 = """
    --  IP Config --
    1.From settings.json
    2.From input

"""


def start_cli(**kwargs):

    protocol = kwargs.get("protocol", "")
    ping = kwargs.get("ping", "")
    source_ip = kwargs.get("source_ip", "")

    clearConsole()
    if protocol == "":
        protocol = "Telnet" if input(menu1) == "1" else "SSH"
        clearConsole()
    if ping == "":
        ping = True if input(menu2) == "1" else False
        clearConsole()

    if source_ip == "":
        if input(menu3) == "1":
            source_ip = True
        else:
            source_ip = input(
                "input your ip like 192.168.1.1 or range like 192.168.0.0/24\n\n")
        clearConsole()
    input(
        f"\tprotocol = {protocol}\n\tping = {ping}\n\tsource_ip = {source_ip} \n\n press Enter to start \n")
    client = TS_client(protocol=protocol, ping=ping, source_ip=source_ip,telnet_debug=True)

    clearConsole()
    client.run_in_pool()
    return


def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)
    print(header)


if __name__ == '__main__':
    start_cli()
    # start_cli(protocol="SSH", ping=True, source_ip=True)

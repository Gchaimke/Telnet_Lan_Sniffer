import os
from TS_client import *

exit = False


def start():
    global exit
    while not exit:
        start_cli()
        # start_cli(protocol="SSH", ping=True, source_ip=True)
    return


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
    global exit

    protocol = kwargs.get("protocol", "")
    ping = kwargs.get("ping", "")
    config_file = kwargs.get("config_file", "")
    source_ip = kwargs.get("source_ip", "")
    stop_ip = kwargs.get("stop_ip", "")

    clearConsole()
    if protocol == "":
        protocol = "Telnet" if input(menu1) == "1" else "SSH"
    clearConsole()
    if ping == "":
        ping = True if input(menu2) == "1" else False
    clearConsole()
    if config_file == "":
        choice = input(menu3)
        if(choice != ""):
            if choice == "1":
                config_file = True
                source_ip = "from config file"
                stop_ip = "from config file"
            else:
                config_file = False
                source_ip = input(
                    "input start ip like 192.168.1.1\n\n")
                stop_ip = input(
                    "input stop ip like 192.168.255.255\n\n")
                if stop_ip == '':
                    stop_ip = source_ip
    clearConsole()
    input(
        f"\tprotocol = {protocol}\n\tping = {ping}\n\tsource_ip = {source_ip}\n\tstop_ip = {stop_ip} \n\n press Enter to start \n")
    client = TS_client(protocol=protocol, ping=ping, config_file=config_file,
                       source_ip=source_ip, stop_ip=stop_ip, telnet_debug=True)
    try:
        client.run()
    except Exception as ex:
        print(f"Error: {ex}")
        
    choice = input("\n\t1 to exit, Enter  to continue\n")
    if choice == "1":
        exit = True
    return


def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)
    print(header)


if __name__ == '__main__':
    start()

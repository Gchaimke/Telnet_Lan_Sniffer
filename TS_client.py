# Rename settings_template.json to settings.json, and setup your network and user names
import ipaddress
import json
from multiprocessing import Pool, Process
from os import path, makedirs
import re
import subprocess
import telnetlib
import paramiko
import numpy

settings_path = r"settings.json"
if not path.exists(settings_path):
    with open(settings_path, "w+") as settings_data:
        settings_data.write("""
{
    "range": "192.168.0.0/20",
    "stop_ip": "192.168.1.250",
    "port": "23",
    "timeout": "100",
    "threads": 20,
    "run_commands":["ls","ifconfig"],
    "users": [
        {
            "name": "admin",
            "pass": "12345"
        },
        {
            "name": "Admin",
            "pass": "0000"
        }
    ]
}
        """)
if not path.exists("out"):
    makedirs("out")
settings_data = open(settings_path, "r")
settings = json.load(settings_data)
settings_data.close()
re_ping_ok = re.compile(r"from \d+.\d+.\d+.\d+: bytes=\d+ time=\d+ms TTL=\d+")


class TS_client:
    def __init__(self, **kwargs):
        self.protocol = kwargs.get("protocol", "Telnet")
        self.ping = kwargs.get("ping", True)
        self.source_ip = kwargs.get("source_ip", True)
        self.telnet_debug = kwargs.get("telnet_debug", True)

        if self.source_ip == True:
            self.ip_range = list(ipaddress.IPv4Network(settings["range"]))
        else:
            self.ip_range = list(ipaddress.IPv4Network(
                kwargs.get("source_ip", settings["range"])))

        return

    def check_range(self, chunk_ips):
        stop_ip = ipaddress.IPv4Address(settings["stop_ip"])
        for ip in chunk_ips:
            print("_"*16+f"\tstart check {ip}\t"+"_"*16)
            if ip > stop_ip:
                break
            if self.ping == True:
                response = subprocess.run(
                    ["ping", str(ip)], capture_output=True)
                if(len(re.findall(re_ping_ok, str(response))) > 0):
                    print("#"*16+f"\t {ip}\t is accessble \t\t"+"#"*16)
                    getattr(self, self.protocol)(ip)
                else:
                    print("="*16+f"\t {ip}\t is not accessble \t"+"="*16)
            else:
                getattr(self, self.protocol)(ip)

        print(f"exit {ip} check_range")
        return

    def Telnet(self, ip):
        port = settings["port"]
        timeout = settings["timeout"]
        users = settings["users"]
        commands = settings["run_commands"]
        output = ""
        cmd_timeout = 3
        try:
            with telnetlib.Telnet(str(ip), int(port), float(timeout)) as session:
                if self.telnet_debug == True:
                    session.set_debuglevel(1)
                for user in users:
                    print(
                        f"Telnet {ip} =>  try login with user {user['name']} and password {user['pass']}")
                    session.expect([b"login", b"Login"], cmd_timeout)
                    session.write(user['name'].encode("ascii")+b"\n")
                    print(f"enter user: {user['name']}")
                    session.expect([b"password", b"Password"], cmd_timeout)
                    print(f"enter password: {user['pass']}")
                    session.write(user['pass'].encode("ascii") + b"\n")
                    recv = session.read_until(
                        b"\n$", cmd_timeout).decode('ascii')
                    output += recv
                    error_keys = ["login", "Login"]
                    if any(word in recv for word in error_keys):
                        continue

                    for command in commands:
                        session.write(command.encode("ascii") + b"\n")
                        recv = session.read_until(
                            b"\n$", cmd_timeout).decode('ascii')
                        output += recv
                    session.read_until(b"\n$", cmd_timeout)
                    session.write(b"exit\n")
                    break
                print(f"end processing ip {ip}")
                
            host_name = self.get_hostname(output)
            output = self.remove_empty_lines(output)

            output_file = open(f"out/{host_name}_{ip}.conf", "w+")
            output_file.write(output)
            output_file.close()
        except Exception as ex:
            print(f"{ip} {ex}")

        print(f"exit {ip} Telnet")
        return

    def SSH(self, ip):
        users = settings["users"]
        commands = settings["run_commands"]
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for user in users:
            print(
                f"SSH {ip} => try login with user {user['name']} and password {user['pass']}")
            try:
                client.connect(
                    str(ip), username=user['name'], password=user['pass'])
                output_file = open(f"out/{ip}.conf", "w")
                for command in commands:
                    stdin, stdout, stderr = client.exec_command(command)
                    recv = stdout.read().decode("utf8")
                    print(recv)
                    output_file.write(recv)

                stdin.close()
                stdout.close()
                stderr.close()
                client.close()
                output_file.close()
                break
            except Exception as ex:
                print(ex)
        print(f"exit {ip} SSH")
        return

    def get_hostname(self, string):
        regex = re.compile("(.+)->.+", re.MULTILINE)
        host_name = re.findall(regex, string)
        if(len(host_name) > 0):
            return host_name[0]
        return "hostname_not_found"

    def remove_empty_lines(self, string):
        new_string = ""
        data = string.splitlines()
        for line in data:
            if line == "":
                continue
            new_string += line+"\n"
        return new_string

    def run_in_process(self):
        range_chunks = numpy.array_split(self.ip_range, settings["threads"])
        for chunk in range_chunks:
            Process(name="check_range", target=self.check_range,
                    args=(chunk,)).start()

    def run_in_pool(self):
        p = Pool(settings["threads"])
        if(len(self.ip_range) > 1):
            range_chunks = numpy.array_split(
                self.ip_range, settings["threads"])
        else:
            range_chunks = [self.ip_range]
        with p:
            p.map(self.check_range, range_chunks)

    def run(self):
        self.check_range(self.ip_range)


if __name__ == '__main__':
    app = TS_client()

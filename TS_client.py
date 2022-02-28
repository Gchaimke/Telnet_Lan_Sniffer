# Rename settings_template.json to settings.json, and setup your network and user names
import ipaddress
import json
from multiprocessing import Pool, Process
import re
import subprocess
import telnetlib
import paramiko
import numpy


settings_path = open(r"settings.json", "r")
settings = json.load(settings_path)
settings_path.close()
re_ping_ok = re.compile(r"from \d+.\d+.\d+.\d+: bytes=\d+ time=\d+ms TTL=\d+")


class TS_client:
    def __init__(self, **kwargs):
        self.protocol = kwargs.get("protocol", "Telnet")
        self.ping = kwargs.get("ping", True)
        self.source_ip = kwargs.get("source_ip", True)

        if self.source_ip == True:
            self.ip_range = list(ipaddress.IPv4Network(settings["range"]))
        else:
            self.ip_range = list(ipaddress.IPv4Network(
                kwargs.get("source_ip", settings["range"])))

        return

    def check_range(self, chunk_ips):
        stop_ip = ipaddress.IPv4Address(settings["stop_ip"])
        for ip in chunk_ips:
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
        try:
            with telnetlib.Telnet(str(ip), int(port), float(timeout)) as session:
                session.set_debuglevel(0)
                session.expect([b"login", b"Login"], 10)
                for user in users:
                    print(
                        f"Telnet {ip} =>  try login with user {user['name']} and password {user['pass']}")
                    session.write(user['name'].encode("ascii")+b"\n")
                    print(f"enter user: {user['name']}")
                    session.expect([b"password", b"Password"], 10)
                    print(f"enter password: {user['pass']}")
                    session.write(user['pass'].encode("ascii") + b"\n")
                    err, obj, data = session.expect([b"Login incorrect"], 10)
                    if(err == 0):
                        continue

                    for command in commands:
                        session.write(command.encode("ascii") + b"\n")
                    session.write(b"exit\n")
                    session_read_data = session.read_all().decode('ascii')
                    save_file = open(f"output/{ip}.conf", "w")
                    save_file.write(session_read_data)
                    save_file.close()
                    print(session_read_data)
                    break
                print(f"end processing ip {ip}")
        except Exception as ex:
            print(f"{ip} {ex}")

        print(f"exit {ip} Telnet")
        return

    def SSH(self, ip):
        users = settings["users"]
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for user in users:
            print(
                f"SSH {ip} => try login with user {user['name']} and password {user['pass']}")
            try:
                client.connect(
                    ip, username=user['name'], password=user['pass'])
                stdin, stdout, stderr = client.exec_command('ifconfig')
                save_file = open(f"output/{ip}.conf", "w")
                save_file.write(stdout.read().decode("utf8"))
                save_file.close()
                print(f'STDOUT: {stdout.read().decode("utf8")}')

                stdin.close()
                stdout.close()
                stderr.close()
                client.close()
                break
            except Exception as ex:
                client.close()
                print(ex)
        print(f"exit {ip} SSH")
        return

    def run_in_process(self):
        range_chunks = numpy.array_split(self.ip_range, settings["threads"])
        for chunk in range_chunks:
            Process(name="check_range", target=self.check_range,
                    args=(chunk,)).start()

    def run_in_pool(self):
        p = Pool(settings["threads"])
        range_chunks = numpy.array_split(self.ip_range, settings["threads"])
        with p:
            p.map(self.check_range, range_chunks)


if __name__ == '__main__':
    app = TS_client()
    # ip = "192.168.3.1"
    # app.run_in_pool()

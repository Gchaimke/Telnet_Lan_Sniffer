import ipaddress
import json
from multiprocessing import Pool,Process
import re
import subprocess
import telnetlib
import numpy


settings_path = open(r"settings.json", "r")
settings = json.load(settings_path)
settings_path.close()
re_ping_ok = re.compile(r"from \d+.\d+.\d+.\d+: bytes=\d+ time=\d+ms TTL=\d+")


class LanSnif:
    def __init__(self):
        self.ip_range = list(ipaddress.IPv4Network(settings["range"]))
        pass

    def sniff_network(self, chunk_ips):
        stop_ip = ipaddress.IPv4Address(settings["stop_ip"])
        for ip in chunk_ips:
            if ip > stop_ip:
                break
            response = subprocess.run(["ping", str(ip)], capture_output=True)
            # print(response)
            if(len(re.findall(re_ping_ok, str(response))) > 0):
                print("#"*16+f"\t {ip}\t is accessble \t\t"+"#"*16)
                self.start_telnet_for_ip(ip)
            else:
                print("="*16+f"\t {ip}\t is not accessble \t"+"="*16)
        return

    def start_telnet_for_range(self, chunk_ips):
        stop_ip = ipaddress.IPv4Address(settings["stop_ip"])
        for ip in chunk_ips:
            if ip > stop_ip:
                break
            self.start_telnet(ip)
            print(f"start processing ip {ip}")
            ip += 1

        pass

    def start_telnet_for_ip(self,ip):
        port = settings["port"]
        timeout = settings["timeout"]
        users = settings["users"]
        try:
            with telnetlib.Telnet(str(ip), int(port), float(timeout)) as session:
                session.read_until(b"login: ")
                for user in users:
                    print(
                        f"try login with user {user['name']} and password {user['pass']}")
                    session.write(b"%s\n" % user['name'])
                    session.read_until(b"password: ")
                    session.write(b"%s\n" % user['pass'])
                    print(session.read_all().decode('ascii'))
                print(f"end processing ip {ip}")
        except Exception as ex:
            print(f"{ip} {ex}")

        pass

    def run_in_process(self):
        range_chunks = numpy.array_split(self.ip_range, settings["threads"])
        for chunk in range_chunks:
            Process(name="ping_cleanup", target=self.sniff_network,
                    args=(chunk,)).start()
            # Process(target=app.get_telnet_data_from_ip, args=(chunk,)).start()

    def run_in_pool(self):
        p = Pool(settings["threads"])
        range_chunks = numpy.array_split(self.ip_range, settings["threads"])
        with p:
            p.map(self.sniff_network, range_chunks)
            # Process(target=app.get_telnet_data_from_ip, args=(chunk,)).start()


if __name__ == '__main__':
    app = LanSnif()
    # app.run_in_process()
    app.run_in_pool()

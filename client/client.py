import json
import time
import os
import socket
import requests
import subprocess
import psutil
from datetime import datetime


# 配置
def get_config():
    with open("./config.json", "r") as f:
        config = json.load(f)
        if "server_url" not in config:
            raise ValueError("Missing 'server_url' in config.json")
        if "put_password" not in config:
            raise ValueError("Missing 'put_password' in config.json")
        return config


# 获取主机名
def get_hostname():
    return socket.gethostname()

# 获取活跃网卡的IP地址和MAC地址
def get_ip_and_mac():
    # 获取所有网络接口的地址信息
    addrs = psutil.net_if_addrs()
    # 获取所有网络接口的信息
    for interface, interface_addrs in addrs.items():
        for addr in interface_addrs:
            # 如果是IPv4地址，返回该地址的IP和MAC
            if addr.family == socket.AF_INET:
                ipaddress = addr.address
                if ipaddress == '127.0.0.1':
                    continue
                # 获取该接口的MAC地址
                macaddress = None
                for iface in interface_addrs:
                    if iface.family == psutil.AF_LINK:
                        macaddress = iface.address
                        break
                if macaddress:
                    return ipaddress, macaddress
    return None, None

# 重启网络服务
def restart_network():
    print("IP address not found, restarting networking...")
    subprocess.run(["sudo", "systemctl", "restart", "networking"])

# 发送数据到FastAPI
def send_record_to_server(name, ipaddress, macaddress):
    config = get_config()

    data = {
        "name": name,
        "ip_address": ipaddress,
        "mac_address": macaddress,
        "put_password": config["put_password"],
    }

    # 发送请求
    try:
        response = requests.put(
            config["server_url"],
            params=data,
        )
        if response.status_code == 200:
            print(f"Record sent successfully: {data}")
        else:
            print(f"Failed to send record: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")

def main():
    while True:
        # 获取服务器信息
        hostname = get_hostname()
        ipaddress, macaddress = get_ip_and_mac()

        # 如果 IP 地址为空，则重启网络
        if ipaddress is None:
            restart_network()
            # 重试获取 IP 地址
            ipaddress, macaddress = get_ip_and_mac()

        if ipaddress is None:
            print("Unable to retrieve IP address after restart, skipping...")
        else:
            send_record_to_server(hostname, ipaddress, macaddress)

        time.sleep(float(get_config()["interval_seconds"]))

if __name__ == "__main__":
    main()

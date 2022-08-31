import socket
import time
import csv
import argparse
import os
import uuid
import glob
import sys
import logging
import concurrent.futures

logging.basicConfig(level=logging.INFO)

def read_hosts_ports(csv_to_read: str) -> list:
    host_port_list = []
    if csv_to_read is None:
        csv_to_read = "host_port.csv"
    with open(csv_to_read) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # skip header of csv file to read into memory
        next(csv_reader)
        for row in csv_reader:
            host_port_list.append(row)
    return host_port_list

def check_socket(host_port_list: list) -> list:
    row_data = []
    host = host_port_list[0]
    port = int(host_port_list[1])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.8)
        pinged_time = time.strftime("%H:%M:%S",time.localtime())
        start_time = time.perf_counter()
        try:
            result = s.connect_ex((host,port))
            s.setblocking(0)
            if result == 0:
                logging.debug(f"Port {port} is open for {host}")
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()),host,port,True,pinged_time,elapsed_time])
            else:
                logging.debug(f"Port {port} is closed for {host}")
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()),host,port,False,pinged_time,elapsed_time])
        except socket.gaierror:
            sys.exit("[-] Hostname Could Not Be Resolved")
        except socket.error:
            sys.exit("[-] Server not responding")
    return row_data

host_port_data = read_hosts_ports("host_port.csv")
future_to_host = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    for data in host_port_data:
        future_to_host.append(executor.submit(check_socket,data))

for future in concurrent.futures.as_completed(future_to_host):
    row_list = future.result()
    
    for row in row_list:
        print(f"[+] Wrote ping result of {row[1],row[2]} to monitoring file.")
    # row = future_to_host[future]
    # try:
    #     data = future.result()
    # except Exception as exc:
    #     print(f"{row} generated an exception: {exc}")
    # else:
    #     print(data)

# multi_thread()

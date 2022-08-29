import csv
import socket
import time
import uuid
import logging
logging.basicConfig(level=logging.DEBUG)

host_port_list = []
with open('host_port.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    header = next(csv_reader)
    for row in csv_reader:
        host_port_list.append(row)
    print(host_port_list)


def generate_row_data(host: str, port: int) -> list:
    row_data = []
    port = int(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.5)
        pinged_time = time.strftime("%H:%M:%S",time.localtime())
        start_time = time.perf_counter()
        try:
            s.connect((host,port))
            logging.debug(f"Port {port} is open for {host}")
            elapsed_time = (time.perf_counter()-start_time) * 1000
            row_data.append([str(uuid.uuid4()),host,port,True,pinged_time,elapsed_time])
        except Exception:
            elapsed_time = (time.perf_counter()-start_time) * 1000
            row_data.append([str(uuid.uuid4()),host,port,False,pinged_time,elapsed_time])
    return row_data

row_list = []
for row in host_port_list:
        host=row[0]
        port=row[1]
        row_list.append(generate_row_data(host,port))


def generate_row_data(host_port_list: list) -> list:
    row_data = []
    for row in host_port_list:
        host=row[0]
        port=int(row[1])
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)
            pinged_time = time.strftime("%H:%M:%S",time.localtime())
            start_time = time.perf_counter()
            try:
                s.connect((host,port))
                logging.debug(f"Port {port} is open for {host}")
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()),host,port,True,pinged_time,elapsed_time])
            except Exception:
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()),host,port,False,pinged_time,elapsed_time])
    return row_data

generate_row_data(host_port_list)
import socket
import time
import csv
import uuid
import sys
import logging
import concurrent.futures

###############################################################################################################
# Variables you can configure
###############################################################################################################

HOST_PORT_LIST = [
    ['google.com', '443'],
    ['google.com', '8000'],
    ['apple.com', '8080'],
    ['apple.com', '443'],
    ['apple.com', '9000']
]

TIME_TO_STOP = "19:00:00"

INTERVAL = 1.5

###############################################################################################################
# Do not change anything below this.
###############################################################################################################
logging.basicConfig(level=logging.INFO)
CSV_HEADER = ['ID','FQDN(IP)','PORT','Is_Up','Pinged_Time(Sec)','Response_Time(ms)']

banner = r"""
  _________.__  __              _____                 
 /   _____/|__|/  |_  ____     /     \   ____   ____  
 \_____  \ |  \   __\/ __ \   /  \ /  \ /  _ \ /    \ 
 /        \|  ||  | \  ___/  /    Y    (  <_> )   |  \
/_______  /|__||__|  \___  > \____|__  /\____/|___|  /
        \/               \/          \/            \/ 
        +-+-+-+-+-+-+-+ +-+-+ +-+-+-+-+-+-+-+-+-+
        |P|o|w|e|r|e|d| |b|y| |B|r|o|o|t|w|a|r|e|
        +-+-+-+-+-+-+-+ +-+-+ +-+-+-+-+-+-+-+-+-+
            
    https://github.com/brootware
    https://brootware.github.io   
"""


def check_socket(host_port_list: list) -> list:
    row_data = []
    host = host_port_list[0]
    port = int(host_port_list[1])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.8)
        pinged_time = time.strftime("%H:%M:%S", time.localtime())
        start_time = time.perf_counter()
        try:
            result = s.connect_ex((host, port))
            s.setblocking(0)
            if result == 0:
                logging.debug(f"Port {port} is open for {host}")
                # print(f"Port {port} is open for {host}")
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()), host, port, True, pinged_time, elapsed_time])
            else:
                logging.debug(f"Port {port} is closed for {host}")
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()), host, port, False, pinged_time, elapsed_time])
        except socket.gaierror:
            sys.exit("[-] Hostname Could Not Be Resolved")
        except socket.error:
            sys.exit("[-] Server not responding")
    return row_data


def site_monitor_loop(time_to_stop: str, time_interval: int) -> None:
    print("Press CTRL+C in the terminal if you want to stop monitoring.")
    # read host data once
    host_port_data = HOST_PORT_LIST
    generated_file = f"monitor_{str(uuid.uuid1())}.csv"
    condition_to_run = True   
    
    with open(f'{generated_file}','w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        while condition_to_run:
            future_to_host = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for data in host_port_data:
                    future_to_host.append(executor.submit(check_socket, data))

            for future in concurrent.futures.as_completed(future_to_host):
                row_list = future.result()
                for row in row_list:
                    print(f"[+] Wrote ping result of {row[1],row[2]} to {generated_file}.")
                    writer.writerow(row)

            current_time = time.localtime()

            logging.debug(time_to_stop)
            if current_time > time_to_stop:
                iso_time = time.strftime("%H:%M:%S", time_to_stop)
                print(f"[+] It's after {iso_time} now, stopping this script.")
                condition_to_run = False

            # Interval in seconds
            if time_interval is None:
                time.sleep(1.5)
            else:
                time.sleep(float(time_interval))
                logging.debug(time_interval) 


def main():
    print(banner)
    current_date = time.strftime("%Y %m %d")
    time_to_stop = time.strptime(f"{current_date} {TIME_TO_STOP}", "%Y %m %d  %H:%M:%S")
    site_monitor_loop(time_to_stop, INTERVAL)


if __name__ == "__main__":
    main()
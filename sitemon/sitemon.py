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
help_menu = """
    SiteMon - A python tool to monitor status of list of sites without any external libraries.
    Example usage:\n
        sitemon file.csv
        sitemon file.csv --time 19:00:00
        sitemon file --interval 2
        sitemon file.csv --time 19:00:00 --interval 2
    """

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
                # print(f"Port {port} is open for {host}")
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

def site_monitor_loop(csv_to_read: str, time_to_stop: str, time_interval: int) -> None:
    print("Press CTRL+C in the terminal if you want to stop monitoring.")
    # read host data once
    host_port_data = read_hosts_ports(csv_to_read)
    generated_file = f"monitor_{str(uuid.uuid1())}.csv"
    condition_to_run = True   
    
    with open(f'{generated_file}','w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        while condition_to_run:
            future_to_host = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for data in host_port_data:
                    future_to_host.append(executor.submit(check_socket,data))

            for future in concurrent.futures.as_completed(future_to_host):
                row_list = future.result()
                for row in row_list:
                    print(f"[+] Wrote ping result of {row[1],row[2]} to {generated_file}.")
                    writer.writerow(row)

            current_time = time.localtime()
            # Check if time_to_stop is not supplied by the user and put default
            if time_to_stop is None:
                time_to_stop = "19:00:00"
                current_date = time.strftime("%Y %m %d")
                time_to_stop = time.strptime(f"{current_date} {time_to_stop}", "%Y %m %d  %H:%M:%S")

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

def arg_helper()-> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Supply a list of host and ports to monitor in csv format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "host",
        help="Supply a list of host and ports to monitor in csv format.",
        nargs="*",
        default=sys.stdin
    )
    parser.add_argument(
        "-t",
        "--time",
        help="""
            Time to stop monitoring. Please enter the time in HH:MM:SS format. Default="19:00:00"
            """
    )
    parser.add_argument(
        "-i",
        "--interval",
        help="""
            Option to put time interval in seconds. 
            Usage: sitemon google.com:443 -i 1
            """,
        default=1.5
    )
    parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        default=True,
        help='Search through subfolders'
    )
    parser.add_argument(
        '-e',
        '--extension',
        default='',
        help='File extension to filter by.'
    )
    return parser

def recursive_file_search(full_path: str, extension: str, recursive: bool) -> set:
    full_paths = [os.path.join(os.getcwd(), path) for path in full_path]
    files = set()
    for path in full_paths:
        if os.path.isfile(path):
            file_name, file_ext = os.path.splitext(path)
            if extension in ('', file_ext):
                files.add(path)
        elif recursive:
            full_paths += glob.glob(path + '/*')
    return files

def is_it_file(file_path: str) -> bool:
    return os.path.isfile(file_path) or os.path.isdir(file_path)

def execute_sitemon_logic():
    parser = arg_helper()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # If there is no input argument and no piped input, print help menu and exit
        if sys.stdin.isatty():
            print(help_menu)
            parser.print_help(sys.stderr)
            sys.exit(1)

    # This is detecting if it's a text or file input and redacting argument supplied like - prk 'This is my ip: 127.0.0.1.'
    is_text = is_it_file(args.host[0])
    if not is_text:
        print(help_menu)
        sys.exit(1)
        # core_redact.process_text(args.host)

    # This is redacting all the files.
    files = recursive_file_search(args.host, args.extension, args.recursive)

    for file in files:
        try:
            if args.time:
                try:
                    current_date = time.strftime("%Y %m %d")
                    args.time = time.strptime(f"{current_date} {args.time}", "%Y %m %d  %H:%M:%S")
                    site_monitor_loop(file,args.time,args.interval)
                except ValueError:
                    sys.exit(f"[-] The time you entered is incorrect. Try again in HH:MM:SS format")
            else:
                site_monitor_loop(file,args.time,args.interval)
        except KeyboardInterrupt:
            print(f"[-] The monitoring process is stopped by the user. Goodbye!")
        

def main():
    print(banner)
    execute_sitemon_logic()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # result = loop.run_until_complete(execute_sitemon_logic())


if __name__ == "__main__":
    main()

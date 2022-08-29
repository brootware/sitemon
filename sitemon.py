import socket
import time
import asyncio
import csv
import argparse
import os
import uuid
import glob
import sys
import logging

logging.basicConfig(level=logging.INFO)
CSV_HEADER = ['ID','FQDN(IP)','PORT','Is_Up','Pinged_Time(Sec)','Response_Time(ms)']

help_menu = """
    SiteMon - A python script to monitor status of a site without any external libraries.
    Example usage:\n
        sitemon file.csv
        sitemon file.csv --time 19:00:00
        sitemon file --interval 2
        sitemon file.csv --time 19:00:00 --interval 2
    """

async def generate_row_data(host_port_list: list) -> list:
    row_data = []
    for row in host_port_list:
        host=row[0]
        port=int(row[1])
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)
            pinged_time = time.strftime("%H:%M:%S",time.localtime())
            start_time = time.perf_counter()
            try:
                await s.connect((host,port))
                logging.debug(f"Port {port} is open for {host}")
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()),host,port,True,pinged_time,elapsed_time])
            except Exception:
                elapsed_time = (time.perf_counter()-start_time) * 1000
                row_data.append([str(uuid.uuid4()),host,port,False,pinged_time,elapsed_time])
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

async def site_monitor_loop(csv_to_read: str, time_to_stop: str, time_interval: int) -> None:
    print("Press CTRL+C in the terminal if you want to stop monitoring.")
    # read host data once
    host_port_data = read_hosts_ports(csv_to_read)
    generated_file = f"monitor_{str(uuid.uuid1())}.csv"
    condition_to_run = True   
    
    with open(f'{generated_file}','w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        while condition_to_run:
            row_list = await generate_row_data(host_port_data)
            for row in row_list:
                print(f"[+] Wrote ping result of {row[1],row[2]} to monitoring file.")
                writer.writerow(row)

            current_time = time.localtime()
            # Check if time_to_stop is not supplied by the user and put default
            if time_to_stop is None:
                time_to_stop = "19:00:00"
                current_date = time.strftime("%Y %m %d")
                time_to_stop = time.strptime(f"{current_date} {time_to_stop}", "%Y %m %d  %H:%M:%S")

            if current_time > time_to_stop:
                iso_time = time.strftime("%H:%M:%S", time_to_stop)
                print(f"[+] It's after {iso_time} now, stopping this script.")
                condition_to_run = False

            # Interval in seconds
            if time_interval is None:
                time.sleep(1.5)
            else:
                time.sleep(float(time_interval))

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

async def execute_sitemon_logic():
    parser = arg_helper()
    args = parser.parse_args()

    # This is redacting all the files.
    files = recursive_file_search(args.host, args.extension, args.recursive)

    for file in files:
        try:
            if args.time:
                try:
                    current_date = time.strftime("%Y %m %d")
                    args.time = time.strptime(f"{current_date} {args.time}", "%Y %m %d  %H:%M:%S")
                    await site_monitor_loop(file,args.time,args.interval)
                except ValueError:
                    sys.exit(f"[-] The time you entered is incorrect. Try again in HH:MM:SS format")
            else:
                await site_monitor_loop(file,args.time,args.interval)
        except KeyboardInterrupt:
            print(f"[-] The monitoring process is stopped by the user. Goodbye!")
        

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(execute_sitemon_logic())


if __name__ == "__main__":
    main()

import socket
import time
import concurrent.futures
import csv
import argparse
import os
import uuid
import glob
import sys
import logging

logging.basicConfig(level=logging.DEBUG)
CSV_HEADER = ['ID','FQDN(IP)','PORT','Is_Up','Pinged_Time(Sec)','Response_Time(ms)']

help_menu = """
    PyRedactKit - Redact and Un-redact any sensitive data from your text files!
    Example usage:\n
        prk 'This is my ip: 127.0.0.1. My email is brute@gmail.com. My favorite secret link is github.com'
        prk [file/directory_with_files]
        prk redacted_file --unredact .hashshadow.json
        prk file --customfile custom.json
        echo 'This is my ip: 127.0.0.1. My email is brute@gmail.com. My favorite secret link is github.com' | prk
    """

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


def read_hosts_ports() -> list:
    host_port_list = []
    with open('host_port.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # skip header of csv file to read into memory
        next(csv_reader)
        for row in csv_reader:
            host_port_list.append(row)
    return host_port_list

def process_from_list(host_port_list: str = read_hosts_ports()) -> list:
    for row in host_port_list:
        host=row[0]
        port=row[1]
        row_list = generate_row_data(host,port)
    return row_list


def site_monitor_loop(time_to_stop: str) -> None:
    print("Press CTRL+C in the terminal if you want to stop monitoring.")
    # read host data once
    host_data = read_hosts_ports()
    generated_file = f"monitor_{str(uuid.uuid1())}.csv"
    condition_to_run = True   
    
    with open(f'{generated_file}','w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        while condition_to_run:
            current_time = time.strftime("%H:%M:%S",time.localtime())
            if current_time > time_to_stop:
                iso_time = time.strftime("%H:%M:%S", time_to_stop)
                print(f"[ + ] It's after {iso_time} now, stopping this script.")
                condition_to_run = False

            row_list = process_from_list(host_data)
            for row in row_list:
                writer.writerow(row)


def arg_helper()-> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Supply a list of host and ports to monitor in csv format. E.g: google.com,443",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "host",
        help="Supply a list of host and ports to monitor in csv format. E.g: google.com,443",
        nargs="*",
        default=sys.stdin
    )
    parser.add_argument(
        "-s",
        "--stop",
        help="""
            Time to stop monitoring. Please enter the time in HH:MM:SS format
            """,
        default="19:00:00"
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

def is_it_file(file_path: str) -> bool:
    return os.path.isfile(file_path) or os.path.isdir(file_path)

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

def execute_sitemon_logic():
    parser = arg_helper()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # If there is no input argument and no piped input, print help menu and exit
        if sys.stdin.isatty():
            print(help_menu)
            parser.print_help(sys.stderr)
            sys.exit(1)

        # This is reading in from linux piped stdin to redact. - echo 'google.com:443' | sitemon.py
        stdin = parser.parse_args().text.read().splitlines()
        print(f"[-] Single IP feature not implemented yet.")
        # core_redact.process_text(stdin)
        sys.exit(1)

    # This is detecting if it's a text or file input and redacting argument supplied like - prk 'This is my ip: 127.0.0.1.'
    is_text = is_it_file(args.text[0])
    if not is_text:
        print(f"[-] Single IP feature not implemented yet.")
        # core_redact.process_text(args.text)

    # This is redacting all the files.
    files = recursive_file_search(args.host, args.extension, args.recursive)

def main():
    site_monitor_loop()


if __name__ == "__main__":
    main()

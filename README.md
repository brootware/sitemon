<br><br>

<h1 align="center">SiteMon 📈📝</h1>

<p align="center">
  <a href="/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg"/></a>
  <!-- <img alt="PyPI - Downloads" src="https://pepy.tech/badge/commonregex-improved/month"> -->
   <!-- <img alt="PyPI - Downloads" src="https://pepy.tech/badge/commonregex-improved"> -->
   <a href="https://twitter.com/brootware"><img src="https://img.shields.io/twitter/follow/brootware?style=social" alt="Twitter Follow"></a>
   <!-- <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/commonregex-improved"> <img alt="PyPI" src="https://img.shields.io/pypi/v/commonregex-improved">
   <a href="https://sonarcloud.io/summary/new_code?id=brootware_commonregex-improved"><img src="https://sonarcloud.io/api/project_badges/measure?project=brootware_commonregex-improved&metric=alert_status" alt="reliability rating"></a>
   <img alt="GitHub Workflow Status" src="https://img.shields.io/github/workflow/status/brootware/commonregex-improved/CI?label=CI&branch=main"> -->
</p>

<p align="center">
  A daemon tool to monitor the status and response time of multiple sites without any external libraries like requests or ICMP (pings).
</p>

<br><br>

## Features

A monitoring daemon that reads in a list of hosts and ports to ping and records the response time in CSV format.

- Uses socket-level pinging 🔌
- Asynchronous, non-blocking pings on the list of defined hosts and ports 🚀
- Captures response time in milliseconds(ms) ⚡
- Written in pure Python without any external libraries. 🐍

## Installation

Clone and activate a virtual environment.

```bash
git clone https://github.com/brootware/sitemon.git
python -m venv venv
source ./venv/bin/activate
```

Install dependencies from [`pyproject.toml`](./pyproject.toml)

```bash
pip install pyproject.toml
poetry install
```

## Usage

Make sure you got a csv file in this format for the agent to read in.

```csv
<!-- file.csv -->
host,port
google.com,443
google.com,8000
apple.com,8080
apple.com,443
apple.com,9000
```

To monitor a list of hosts and ports from a CSV file.

```bash
sitemon file.csv
```

To specify what time you would like to stop monitoring.

```bash
sitemon file.csv --time 19:00:00
```

To specify the time interval between each ping in seconds.

```bash
sitemon file --interval 2
```

## Optional help menu

```bash
usage: sitemon [-h] [-t TIME] [-i INTERVAL] [-r] [-e EXTENSION] [host ...]

Supply a list of host and ports to monitor in csv format.

positional arguments:
  host                  Supply a list of host and ports to monitor in csv format. (default: <_io.TextIOWrapper
                        name='<stdin>' mode='r' encoding='utf-8'>)

options:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  Time to stop monitoring. Please enter the time in HH:MM:SS format. Default="19:00:00"
                        (default: None)
  -i INTERVAL, --interval INTERVAL
                        Option to put time interval in seconds. Usage: sitemon google.com:443 -i 1 (default: 1.5)
  -r, --recursive       Search through subfolders (default: True)
  -e EXTENSION, --extension EXTENSION
                        File extension to filter by. (default: )
```

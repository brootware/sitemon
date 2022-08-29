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
  A daemon tool to monitor the status of multiple sites without any external libraries.
</p>

<br><br>

## Features

A monitoring daemon that reads in a list of hosts and ports to ping them and get response time in CSV format.

- Uses socket-level pinging without any external libraries 🔌
- Asynchronously ping the list of hosts on the defined ports 🚀
- Captures response time in milliseconds(ms) ⚡

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
```

## Usage

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

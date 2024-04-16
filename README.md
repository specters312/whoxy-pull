
# Whoxy Domain Fetcher

This Python script fetches non-expired domains related to a specific company name or email address using the Whoxy Reverse WHOIS API. It leverages caching to avoid unnecessary requests and provides an option to skip the expiry date check.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Example](#example)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)
- [License](#license)

## Installation

Before running the script, you need to ensure Python 3 and `pip` are installed on your system. Install the required Python packages using:

```bash
pip install requests tqdm
```

## Usage

The script can be executed from the command line with the following parameters:

- `api_key`: Your Whoxy API key.
- `search_value`: The company name or email address to search for domains.
- `--skip`: Optional flag to skip the expiry date check for domains.

Example command:

```bash
python whoxy_domain_fetcher.py <api_key> "<search_value>" --skip
```

## Features

- **Caching**: Reduces the number of API requests by caching domain data.
- **Expiry Check**: Optionally skips checking whether domains are expired.
- **Progress Bar**: Displays a progress bar for the fetching process.

## Dependencies

- Python 3.6 or higher.
- `requests`: For making HTTP requests.
- `tqdm`: For displaying progress bars.

## Configuration

No additional configuration is required beyond the installation steps and command-line arguments.

## Example

Fetching domains associated with the email "example@email.com" without skipping expiry checks:

```bash
python whoxy_domain_fetcher.py YOUR_API_KEY "example@email.com"
```


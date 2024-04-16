#!/bin/python3
import json
import argparse
import os
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
import time

# Global Variables
cache_duration = 60  # Cache duration in minutes
request_delay = 5    # Request delay in seconds

def is_domain_expired(expiry_date):
    try:
        expiry_datetime = datetime.strptime(expiry_date, "%Y-%m-%d")
        return expiry_datetime < datetime.now()
    except ValueError:
        return False

def read_cache(cache_file):
    if os.path.exists(cache_file):
        cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if cache_age < timedelta(minutes=cache_duration):
            try:
                with open(cache_file, 'r') as file:
                    return json.load(file)
            except Exception as e:
                print(f"Error reading cache: {e}")
    return None

def write_cache(cache_file, data):
    try:
        with open(cache_file, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        print(f"Error writing cache: {e}")

def extract_domains_from_cache(cache_file, output_file):
    if not os.path.exists(cache_file):
        print(f"Cache file not found: {cache_file}")
        return

    try:
        with open(cache_file, 'r') as file:
            cache_data = json.load(file)

        if not cache_data:
            print("No domains found in the cache file.")
            return

        with open(output_file, 'w') as file:
            for domain in cache_data:
                file.write(f"{domain}\n")

        print(f"Domains extracted to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")

    # Delete the cache file after processing
    try:
        os.remove(cache_file)
        print(f"Cache file {cache_file} deleted successfully.")
    except OSError as e:
        print(f"Error deleting cache file {cache_file}: {e}")

def get_domains(api_key, search_type, search_value, skip_expiry_check):
    cache_file = f"whoxy_cache_{search_value}.json"
    cache_data = read_cache(cache_file)

    if not cache_data:
        domain_list = []
        url = f"https://api.whoxy.com/?key={api_key}&reverse=whois&{search_type}={search_value.replace(' ','+')}&mode=micro&page=1"
        response = requests.get(url)
        data = json.loads(response.text)

        if data.get('status') != 1:
            print("Error: API request failed.")
            return

        total_pages = data.get('total_pages', 1)

        for page in tqdm(range(1, total_pages + 1), desc="Fetching domains"):
            try:
                url = f"https://api.whoxy.com/?key={api_key}&reverse=whois&{search_type}={search_value}&mode=micro&page={page}"
                response = requests.get(url)
                data = json.loads(response.text)

                if 'search_result' not in data or data['search_result'] == []:
                    continue

                for result in data['search_result']:
                    if skip_expiry_check or ('expiry_date' in result and not is_domain_expired(result['expiry_date'])):
                        domain_list.append(result['domain_name'])

                if page < total_pages:
                    time.sleep(request_delay)

            except Exception as e:
                print(f"Error on page {page}: {e}")
                continue

        write_cache(cache_file, domain_list)
        output_file = f"domains_{search_value}.txt"
        extract_domains_from_cache(cache_file, output_file)

    else:
        domain_list = cache_data
        output_file = f"domains_{search_value}.txt"
        extract_domains_from_cache(cache_file, output_file)

    if not domain_list:
        print("No non-expired domains found")
    else:
        print("\n".join(domain_list))

def main():
    parser = argparse.ArgumentParser(description="Find non-expired domains using Whoxy Reverse WHOIS API.")
    parser.add_argument("api_key", help="Your Whoxy API key")
    parser.add_argument("search_value", help="The company name or email address to search for domains")
    parser.add_argument("--skip", help="Skip the expiry date check for domains", action="store_true")
    args = parser.parse_args()

    search_value = None
    search_type = None
    if '@' in args.search_value:
        search_type = 'email'
    elif args.search_value:
        search_type = 'company'
    else:
        print("You must provide either --company_name or --email argument or include '@' in the API key for auto detection")
        return

    get_domains(args.api_key, search_type, args.search_value, args.skip)

if __name__ == "__main__":
    main()


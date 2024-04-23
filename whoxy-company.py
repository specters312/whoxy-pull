#!/bin/python3
import json
import argparse
import os
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
import time

# Global Variables
cache_duration = 43200  # Cache duration in minutes
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

def extract_domains_from_cache(cache_file, output_file, filter_names=None):
    if not os.path.exists(cache_file):
        print(f"Cache file not found: {cache_file}")
        return

    try:
        with open(cache_file, 'r') as file:
            cache_data = json.load(file)

        if not cache_data:
            print("No domains found in the cache file.")
            return

        filtered_domains = []
        with open(output_file, 'w') as file:
            for domain in cache_data:
                if filter_names and not any(name in domain for name in filter_names):
                    continue
                file.write(f"{domain}\n")
                filtered_domains.append(domain)

        if filtered_domains:
            print(f"Filtered domains extracted to: {output_file}")
        else:
            print("No domains matched the filter criteria.")

    except Exception as e:
        print(f"Error: {e}")

def get_domains(api_key, search_type, search_value, skip_expiry_check, filter_names):
    cache_file = f"whoxy_cache_{search_value}_{search_type}.json"
    cache_data = read_cache(cache_file)

    if not cache_data:
        domain_list = []
        url = f"https://api.whoxy.com/?key={api_key}&reverse=whois&{search_type}={search_value.replace(' ', '+')}&mode=micro&page=1"
        response = requests.get(url)
        data = json.loads(response.text)

        if data.get('status') != 1:
            print("Error: API request failed.")
            return [], search_type

        total_pages = data.get('total_pages', 1)

        for page in tqdm(range(1, total_pages + 1), desc=f"Fetching domains by {search_type}"):
            try:
                url = f"https://api.whoxy.com/?key={api_key}&reverse=whois&{search_type}={search_value}&mode=micro&page={page}"
                response = requests.get(url)
                data = json.loads(response.text)

                if 'search_result' not in data or data['search_result'] == []:
                    continue

                for result in data['search_result']:
                    if not skip_expiry_check and ('expiry_date' not in result or is_domain_expired(result['expiry_date'])):
                        continue
                    domain_list.append(result['domain_name'])

                if page < total_pages:
                    time.sleep(request_delay)

            except Exception as e:
                print(f"Error on page {page}: {e}")
                continue

        write_cache(cache_file, domain_list)
    else:
        domain_list = cache_data

    if domain_list:
        output_file = f"domains_{search_value.lower().replace(' ','_')}_{search_type}.txt"
        extract_domains_from_cache(cache_file, output_file, filter_names)

    return domain_list, search_type

def main():
    parser = argparse.ArgumentParser(description="Find non-expired domains using Whoxy Reverse WHOIS API.")
    parser.add_argument("api_key", help="Your Whoxy API key")
    parser.add_argument("search_value", help="The name, company name, or email address to search for domains")
    parser.add_argument("--skip", help="Skip the expiry date check for domains", action="store_true")
    parser.add_argument("--filter", help="Comma-separated names to filter the domains after fetching", type=lambda s: [item.strip() for item in s.split(',')])
    args = parser.parse_args()

    if '@' in args.search_value:
        search_type = 'email'
    else:
        search_type = 'company'

    domain_list, search_type_used = get_domains(args.api_key, search_type, args.search_value, args.skip, args.filter)
    if not domain_list and search_type == 'company':
        # If no domains found with 'company', retry with 'name'
        print("No domains found under 'company'. Retrying with 'name'...")
        domain_list, search_type_used = get_domains(args.api_key, 'name', args.search_value, args.skip, args.filter)

if __name__ == "__main__":
    main()
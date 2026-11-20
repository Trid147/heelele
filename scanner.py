import asyncio
import json
import httpx
from typing import Callable, Dict, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

async def check_site(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, site_name: str, site_data: dict, username: str) -> Dict | None:
    url = site_data['url'].format(username=username)
    error_type = site_data.get('error_type', 'status_code')

    async with semaphore:
        try:
            response = await client.get(url, follow_redirects=True)

            success = {'site': site_name, 'url': url, 'status': 'Found'}

            if error_type == 'status_code':
                if response.status_code == 200:
                    return success
            elif error_type == 'redirect':
                if response.status_code == 200 and str(response.url).rstrip('/') == url.rstrip('/'):
                    return success
            elif error_type == 'error_text':
                if response.status_code == 200 and site_data['error_text'] not in response.text:
                    return success
            elif error_type == 'success_text':
                if response.status_code == 200 and site_data['success_text'] in response.text:
                    return success

        except httpx.RequestError:
            return None
    
    return None

async def scan_username(usernames: List, sites_file: str = 'sites.json', on_progress: Callable[[int, int, int], None] | None = None) -> List[Dict]:
    with open(sites_file, 'r', encoding='utf-8') as file:
        sites = json.load(file)

    semaphore = asyncio.Semaphore(30)
    timeout = httpx.Timeout(5.0, connect=3.0)

    async with httpx.AsyncClient(headers=HEADERS, timeout=timeout, http2=True) as client:
        tasks = [check_site(client, semaphore, name, data, username) for username in usernames for name, data in sites.items()]

        total = len(tasks)
        completed = 0
        found_results = []

        for task in asyncio.as_completed(tasks):
            result = await task
            completed += 1
            if result is not None:
                found_results.append(result)

            if on_progress:
                on_progress(completed, total, len(found_results))

    return found_results
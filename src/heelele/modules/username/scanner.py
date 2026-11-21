import asyncio
import json
import httpx
from typing import Callable, Dict, List
from importlib import resources

from heelele.modules.username.extractor import extract_metadata

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def load_sites() -> dict:
    data_file = resources.files('heelele.modules.username').joinpath('sites.json')
    return json.loads(data_file.read_text(encoding='utf-8'))

async def check_site(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, site_name: str, site_data: dict, username: str, extract: bool = False) -> Dict | None:
    url = site_data['url'].format(username=username)
    error_type = site_data.get('error_type', 'status_code')
    real_url = site_data.get('real_url', None)

    async with semaphore:
        try:
            response = await client.get(url, follow_redirects=True)

            if response.status_code != 200:
                return None

            found = False
            if error_type == 'status_code':
                found = True
            elif error_type == 'redirect':
                if str(response.url).rstrip('/') == url.rstrip('/'):
                    found = True
            elif error_type == 'error_text':
                if site_data['error_text'] not in response.text:
                    found = True
            elif error_type == 'success_text':
                if site_data['success_text'] in response.text:
                    found = True

            if found:
                metadata = extract_metadata(response.text, site_data.get('extract', {})) if extract else {}
                if real_url: url = site_data['real_url'].format(username=username)
                return {'site': site_name, 'url': url, 'status': 'Found', 'username': username, "metadata": metadata}

        except httpx.RequestError:
            return None
    
    return None

async def scan_username(usernames: List, on_progress: Callable[[int, int, int], None] | None = None, extract: bool = False) -> List[Dict]:
    sites = load_sites()

    semaphore = asyncio.Semaphore(30)
    timeout = httpx.Timeout(5.0, connect=3.0)

    async with httpx.AsyncClient(headers=HEADERS, timeout=timeout, http2=True) as client:
        tasks = [check_site(client, semaphore, name, data, username, extract) for username in usernames for name, data in sites.items()]

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
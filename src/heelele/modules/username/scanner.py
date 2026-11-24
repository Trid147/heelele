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

async def get_current_ip(proxy: str | None = None) -> str | None:
    try:
        async with httpx.AsyncClient(proxy=proxy, timeout=8.0) as client:
            response = await client.get('https://api.ipify.org')
            if response.status_code == 200:
                return response.text.strip()
    except httpx.RequestError:
        return None
    return None

async def detect_tor_proxy() -> str | None:
    for port in (9050, 9150):
        proxy_url = f'socks5h://127.0.0.1:{port}'
        if await get_current_ip(proxy_url):
            return proxy_url
    return None

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

async def scan_username(usernames: List, on_progress: Callable[[int, int, int], None] | None = None, extract: bool = False, proxy: str | None = None) -> List[Dict]:
    sites = load_sites()

    semaphore = asyncio.Semaphore(30)
    timeout_value = 15.0 if proxy else 5.0
    timeout = httpx.Timeout(timeout_value, connect=10.0 if proxy else 3.0)

    async with httpx.AsyncClient(headers=HEADERS, timeout=timeout, proxy=proxy) as client:
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
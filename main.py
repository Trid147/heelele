#!/usr/bin/env python3
import asyncio
from colorama import Fore, init
from scanner import scan_username
from loading import loading

init(autoreset=True)

@loading
async def scan_with_loading(username):
    return await scan_username(username)

async def main():
    print(Fore.GREEN + 'Welcome to heelele!')
    username = str(input('Enter a username: '))

    found_profiles = await scan_with_loading(username)

    print(Fore.GREEN + 'Results:')

    if not found_profiles:
        print('Nothing found.')
    else:
        for item in found_profiles:
            print(f'[+] {item['site']}: {item['url']}')

if __name__ == '__main__':
    asyncio.run(main())
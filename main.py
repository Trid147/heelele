#!/usr/bin/env python3
import asyncio
from scanner import scan_username
from loading import loading

@loading
async def scan_with_loading(username):
    return await scan_username(username)

async def main():
    print('Welcome to heelele!')
    username = str(input('Enter a username: '))

    found_profiles = await scan_with_loading(username)

    print('Results:')

    if not found_profiles:
        print('Nothing found.')
    else:
        for item in found_profiles:
            print(f'[+] {item['site']}: {item['url']}')

if __name__ == '__main__':
    asyncio.run(main())
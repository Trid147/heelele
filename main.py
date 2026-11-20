#!/usr/bin/env python3
import asyncio
import itertools
import sys
from colorama import Fore, init
from scanner import scan_username
from mutations import generate_variations

init(autoreset=True)

async def scan_with_loading(username):
    return await scan_username(username)

async def main():
    print(Fore.GREEN + 'Welcome to heelele!')
    username = input('Enter a username: ')
    deep = input('Enable deep scan with variations? (y/n): ').strip().lower() == 'y'

    targets = generate_variations(username) if deep else [username]
    spinner = itertools.cycle(r'\|/-')

    def show_progress(completed: int, total: int, found_count: int):
        percent = int((completed / total) * 100)
        char = next(spinner)

        sys.stdout.write('\x1b[1A\x1b[2K')
        sys.stdout.write(f'\r{Fore.CYAN}[{char}] Scanning: {completed}/{total} ({percent}%) | Found: {Fore.GREEN}{found_count}\n')
        sys.stdout.flush()

    found_profiles = await scan_username(targets, on_progress=show_progress)
    print(Fore.GREEN + 'Results:')

    if not found_profiles:
        print('Nothing found.')
    else:
        for item in found_profiles:
            print(f'[+] {item['site']}: {item['url']}')

if __name__ == '__main__':
    asyncio.run(main())
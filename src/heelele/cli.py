#!/usr/bin/env python3
import asyncio
import argparse
import itertools
import sys
from colorama import Fore, init
from heelele.modules.username.scanner import scan_username
from heelele.modules.username.mutations import generate_variations

init(autoreset=True)

async def main():
    parser = argparse.ArgumentParser(description='Heelele - Username Search OSINT Tool')
    parser.add_argument('username', help='Target username')
    parser.add_argument('-d', '--deep', action='store_true', help='Enables deep scan with mutations')
    parser.add_argument('-o', '--output', help='Saves found results to a file')
    args = parser.parse_args()

    print(Fore.GREEN + 'Welcome to heelele!\n')
    username = args.username
    deep = args.deep

    targets = generate_variations(username) if deep else [username]
    spinner = itertools.cycle(r'\|/-')

    def show_progress(completed: int, total: int, found_count: int):
        percent = int((completed / total) * 100)
        char = next(spinner)
        sys.stdout.write(f'\r{Fore.CYAN}[{char}] Scanning: {completed}/{total} ({percent}%) | Found: {Fore.GREEN}{found_count}')
        sys.stdout.flush()

    found_profiles = await scan_username(targets, on_progress=show_progress)
    print('\n' + Fore.GREEN + 'Results:')

    if not found_profiles:
        print(Fore.CYAN + 'Nothing found.')
    else:
        for item in found_profiles:
            print(f'{Fore.CYAN}[+] {item['site']} ({Fore.YELLOW}{item['username']}{Fore.CYAN}): {item['url']}')
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as file:
                for item in found_profiles:
                    file.write(f'[+] {item['site']} ({item['username']}): {item['url']}\n')
            print(f'\n{Fore.YELLOW} Saved {len(found_profiles)} results to {args.output}')

#pyproject.toml specifies on this function only
def entry_point():
    asyncio.run(main())

if __name__ == '__main__':
    entry_point()
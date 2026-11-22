#!/usr/bin/env python3
import asyncio
import argparse
import itertools
import sys
from colorama import Fore, init
from pathlib import Path
from heelele.modules.username.scanner import scan_username
from heelele.modules.username.mutations import generate_variations

init(autoreset=True)

async def main():
    parser = argparse.ArgumentParser(description='Heelele - Username Search OSINT Tool')
    parser.add_argument('username', nargs='?', help='Target username')
    parser.add_argument('--wordlist', help='Path to a wordlist file')
    parser.add_argument('-d', '--deep', action='store_true', help='Enables deep scan with mutations')
    parser.add_argument('-o', '--output', help='Saves found results to a file')
    parser.add_argument('-m', '--metadata', action='store_true', help='Outputs web page metadata')
    args = parser.parse_args()

    if not args.username and not args.wordlist:
        print(Fore.RED + 'Error: Provide a username or --wordlist!')
        return

    print(Fore.GREEN + 'Welcome to heelele!\n')

    targets = []

    if args.username:
        targets.append(args.username.strip())

    if args.wordlist:
        wordlist = Path(args.wordlist)
        if not wordlist.is_file():
            print(Fore.RED + f'Error: {wordlist} file not found.')
            return

        with open(wordlist, 'r', encoding='utf-8') as file:
            targets.extend(line.strip() for line in file if line.strip())

    if args.deep:
        expanded = set()
        for target in targets:
            expanded.update(generate_variations(target))
        targets = list(expanded)
    else:
        targets = list(dict.fromkeys(targets))

    spinner = itertools.cycle(r'\|/-')

    def show_progress(completed: int, total: int, found_count: int):
        percent = int((completed / total) * 100)
        char = next(spinner)
        sys.stdout.write(f'\r{Fore.CYAN}[{char}] Scanning: {completed}/{total} ({percent}%) | Found: {Fore.GREEN}{found_count}')
        sys.stdout.flush()

    found_profiles = await scan_username(targets, on_progress=show_progress, extract=args.metadata)
    print('\n' + Fore.GREEN + 'Results:')

    if not found_profiles:
        print(Fore.CYAN + 'Nothing found.')
    else:
        for item in found_profiles:
            print(f'{Fore.CYAN}[+] {item['site']} ({Fore.YELLOW}{item['username']}{Fore.CYAN}): {item['url']}')
            if args.metadata:
                for k, v in item.get('metadata', {}).items():
                    print(f'    {Fore.YELLOW}↳ {k.capitalize()}: {Fore.WHITE}{v}')
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
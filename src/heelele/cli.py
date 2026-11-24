#!/usr/bin/env python3
import asyncio
import argparse
import itertools
import sys
from colorama import Fore, init
from pathlib import Path
from heelele.modules.username.scanner import scan_username, get_current_ip, detect_tor_proxy
from heelele.modules.username.mutations import generate_variations
from heelele.core.exporter import export_results
from heelele.core.banner import print_banner

init(autoreset=True)

async def main():
    parser = argparse.ArgumentParser(description='Heelele - Username Search OSINT Tool')
    parser.add_argument('username', nargs='?', help='Target username')
    parser.add_argument('--wordlist', help='Path to a wordlist file')
    parser.add_argument('--format', choices=['txt', 'json', 'csv'], help='Force output format')
    parser.add_argument('--proxy', help='Proxy URL')
    parser.add_argument('-q', '--no-banner', action='store_true', help='Hide the startup ASCII banner')
    parser.add_argument('-t', '--tor', action='store_true', help='Route traffic through local Tor SOCKS5 proxy')
    parser.add_argument('-d', '--deep', action='store_true', help='Enables deep scan with mutations')
    parser.add_argument('-o', '--output', help='Saves found results to a file')
    parser.add_argument('-m', '--metadata', action='store_true', help='Outputs web page metadata')
    args = parser.parse_args()
    
    if not args.no_banner:
        print(Fore.GREEN + 'Welcome to heelele!')
        print_banner()

    if not args.username and not args.wordlist:
        print(Fore.RED + 'Error: Provide a username or --wordlist!')
        return

    proxy_url = args.proxy

    if args.tor:
        print(Fore.YELLOW + '[*] Detecting active Tor services...')
        proxy_url = await detect_tor_proxy()
        if not proxy_url:
            print(Fore.RED + 'Error: Tor is not running! Start Tor browser or the tor service first.')
            return
        print(Fore.GREEN + f'[+] Tor proxy active!')

    if proxy_url:
        print(Fore.YELLOW + f'[*] Checking proxy connection ({proxy_url})...')
        exit_ip = await get_current_ip(proxy_url)
        if not exit_ip:
            print(Fore.RED + 'Error: Could not connect to proxy.')
            return
        print(Fore.GREEN + f'[+] Proxy active! Exit IP: {exit_ip}\n')


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

    found_profiles = await scan_username(targets, on_progress=show_progress, extract=args.metadata, proxy=proxy_url)
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
            saved_fmt = export_results(found_profiles, args.output, args.format)
            print(f'\n{Fore.YELLOW} Saved {len(found_profiles)} results to {args.output} ({saved_fmt})')

#pyproject.toml specifies on this function only
def entry_point():
    asyncio.run(main())

if __name__ == '__main__':
    entry_point()
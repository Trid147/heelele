from colorama import Fore, Style

BANNER = rf"""{Fore.CYAN}
  _   _           _      _      
 | | | | ___  ___| | ___| | ___ 
 | |_| |/ _ \/ _ \ |/ _ \ |/ _ \
 |  _  |  __/  __/ |  __/ |  __/
 |_| |_|\___|\___|_|\___|_|\___|  {Fore.YELLOW}v0.4.0{Style.RESET_ALL}
 {Fore.GREEN}Async CIS OSINT Reconnaissance Tool{Style.RESET_ALL}
"""

def print_banner(): print(BANNER)
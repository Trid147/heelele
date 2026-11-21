import re
from selectolax.lexbor import LexborHTMLParser as HTMLParser
from typing import Dict

def extract_metadata(html: str, rules: Dict[str, str]) -> Dict[str, str]:
    if not rules:
        return {}
    
    tree = HTMLParser(html)
    extracted = {}

    for field, selector in rules.items():
        if selector.startswith('meta:'):
            prop = selector.split('meta:', 1)[1]
            node = tree.css_first(f'meta[property="{prop}"], meta[name="{prop}"]')
            if node:
                content = node.attributes.get('content')
                if content:
                    value = content.strip()
                    if value:
                        extracted[field] = value
        elif selector.startswith('regex:'):
            pattern = selector.split('regex:', 1)[1]
            match = re.search(pattern, html)
            if match:
                value = match.group(1) if match.groups else match.group(0)
                if value.strip():
                    extracted[field] = value
        else:
            node = tree.css_first(selector)
            if node:
                value = node.text(strip=True)
                if value:
                    extracted[field] = value

    return extracted

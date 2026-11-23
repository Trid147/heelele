import csv
import json
from pathlib import Path
from typing import Dict, List

def export_results(results: List[Dict], output_path: str, fmt: str | None = None) -> str:
    path = Path(output_path)
    export_format = (fmt or path.suffix.lstrip('.')).lower()

    if export_format == 'json':
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        return 'JSON'
    elif export_format == 'csv':
        meta_keys = sorted({key for item in results for key in item.get('metadata', {}).keys()})
        fieldnames = ['site', 'username', 'url', 'status'] + meta_keys

        with open(path, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for item in results:
                row = {'site': item.get('site', ''), 'username': item.get('username', ''), 'url': item.get('url', ''), 'status': item.get('status', 'Found')}
                row.update(item.get('metadata', {}))
                writer.writerow(row)
        return 'CSV'
    else:
        with open(path, 'w', encoding='utf-8') as file:
            for item in results:
                file.write(f'[+] {item['site']} ({item['username']}): {item['url']}\n')
                for k, v in item.get('metadata', {}).items():
                    file.write(f'    ↳ {k.capitalize()}: {v}\n')
        return 'TXT'
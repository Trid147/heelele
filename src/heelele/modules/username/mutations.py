from typing import List

def generate_variations(username: str) -> List:
    base = username.strip()
    variations = set()

    variations.add(base)
    variations.add(base.lower())
    variations.add(base.capitalize())

    common_affixes = [
        f'{base}_',
        f'_{base}',
        f'{base}1',
        f'{base}01',
        f'{base}67',
        f'{base}69',
        f'{base}147',
        f'{base}123',
        f'{base}228',
        f'{base}777',
        f'{base}666',
        f'the_{base}',
        f'real_{base}',
        f'im_{base}',
        f'super_{base}',
        f'ultra_{base}',
        f'{base}_official',
        f'{base}_ru',
        f'{base}_tv',
        f'{base}_play',
        f'{base}_exe'
    ]
    variations.update(common_affixes)

    for year in range(1990, 2030):
        variations.add(f'{base}{year}')
        variations.add(f'{base}_{year}')

    return list(variations)
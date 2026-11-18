import asyncio
import itertools
import sys
from functools import wraps

def loading(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        stop = asyncio.Event()

        async def spin():
            for char in itertools.cycle(r'\|/-'):
                if stop.is_set():
                    break
                sys.stdout.write(f'\rScanning started... {char}')
                sys.stdout.flush()
                await asyncio.sleep(0.1)

        spinner = asyncio.create_task(spin())
        try:
            result = await func(*args, **kwargs)
        except Exception:
            stop.set()
            await spinner
            print('\rScanning failed!   ')
            raise
        else:
            stop.set()
            await spinner
            print('\rScanning completed!   ')
            return result

    return wrapper
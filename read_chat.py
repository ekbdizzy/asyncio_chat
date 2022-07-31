import asyncio
import argparse
import datetime

import aiofiles
from environ import Env

from streaming_tools import open_connection


def add_timestamp(message: str | bytes, stamp_format: str = "[%d.%m.%Y %H:%M]") -> str:
    """Add timestamp and decode bytes to string if needed."""
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    timestamp = datetime.datetime.now().strftime(stamp_format)
    return f'{timestamp} {message.strip()}'


async def read_stream(host: str, port: int, filename: str) -> None:
    """Show messages from chat to console and save history to file."""
    async with open_connection(host=host, port=port) as connection:
        async with aiofiles.open(filename, 'a') as file:
            while True:
                reader, writer = connection
                phrase = await reader.readline()
                phrase_with_timestamp = add_timestamp(phrase)
                print(phrase_with_timestamp)
                await file.write(f'{phrase_with_timestamp}\n')

if __name__ == '__main__':

    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, help='Host name')
    parser.add_argument('--port', dest='port', type=int, help='Port number')
    parser.add_argument('--history', dest='filename', type=str, help='File to save history')
    args = parser.parse_args()

    host = args.host or env.str('HOST', 'minechat.dvmn.org')
    port = args.port or env.int('PORT_READ', 5000)
    filename = args.filename or env.str('FILENAME', 'chat.history')

    asyncio.run(read_stream(host, port, filename))

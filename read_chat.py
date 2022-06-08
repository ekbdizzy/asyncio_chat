import asyncio
import argparse
import os.path
import datetime

import aiofiles
from environ import Env


def add_timestamp(message: str | bytes, stamp_format: str = "[%d.%m.%Y %H:%M]") -> str:
    """Add timestamp and decode bytes to string if needed."""
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    timestamp = datetime.datetime.now().strftime(stamp_format)
    return f'{timestamp} {message.strip()}'


async def tcp_echo_client(host: str, port: int, filename: str) -> None:
    """Show messages from chat to console and save history to file."""
    reader, writer = await asyncio.open_connection(host=host, port=port)
    phrase = await reader.readline()
    async with aiofiles.open(filename, 'a') as file:
        phrase_with_timestamp = add_timestamp(phrase)
        print(phrase_with_timestamp)
        await file.write(phrase_with_timestamp)


if __name__ == '__main__':

    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, help='Host name')
    parser.add_argument('--port', dest='port', type=int, help='Port number')
    parser.add_argument('--history', dest='filename', type=str, help='File to save history')
    args = parser.parse_args()

    host = args.host or env.str('HOST', 'minechat.dvmn.org')
    port = args.port or env.int('PORT', 5000)
    filename = args.filename or env.str('FILENAME', 'chat.history')

    if os.path.exists(filename):
        os.remove(filename)

    while True:
        asyncio.run(tcp_echo_client(host, port, filename))

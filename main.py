import asyncio
import argparse
import contextlib
import json
import logging

import aiofiles
from environ import Env

env = Env()
env.read_env()
logger = logging.getLogger('sender')


@contextlib.asynccontextmanager
async def open_connection(host: str, port: int) -> tuple:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


async def register(connection: asyncio.StreamReader, username: str) -> dict | None:
    reader, writer = connection

    await reader.readline()
    writer.write(f'\n'.encode())

    await reader.readline()
    writer.write(f'{username}\n'.encode())

    message = await reader.readline()
    credentials = json.loads(message.decode())
    if not credentials:
        logging.error("Server Error: can't get token")
        return

    with aiofiles.open('credentials.json', 'w') as file:
        await file.write(json.dumps(credentials))
        logging.info("Username and token saved.")

    return credentials


async def authorize(connection: asyncio.StreamReader, token: str) -> bool:
    reader, writer = connection

    text = await reader.readline()
    logger.info(text.decode())

    writer.write(f"{token}\n".encode())
    await writer.drain()

    response = await reader.readline()
    try:
        assert json.loads(response) is not None
        return True
    except AssertionError:
        logging.error('The token is invalid. Check the token or register again.')
        return False


async def _send_message(writer, message):
    writer.write(f'{message}\n\n'.encode())
    await writer.drain()


async def submit_message(args):
    async with open_connection(args.host, args.port) as connection:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, default='minechat.dvmn.org', help='Host name')
    parser.add_argument('--port', dest='port', type=int, default=5050, help='Port number')
    parser.add_argument('-m', '--message', dest='message', help='Message text')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    asyncio.run(submit_message(args))


if __name__ == '__main__':
    main()

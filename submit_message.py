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


def sanitize(string: str) -> str:
    """Replace \n and \t from string. Can be updated with new replacements."""
    if string:
        string = string.replace('\n', ' ')
        string = string.replace('\t', '    ')
        return string
    return ""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        dest='host',
        type=str,
        default='minechat.dvmn.org',
        help='Host name, default is: minechat.dvmn.org'
    )
    parser.add_argument(
        '--port',
        dest='port',
        type=int,
        default=5050,
        help='Port number, default is: 5050'
    )
    parser.add_argument(
        '--token',
        dest='token',
        type=str,
        help='Token of registered user.'
    )
    parser.add_argument(
        '--username',
        dest='username',
        type=str,
        help='Username of registered user.'
    )
    parser.add_argument(
        '--message',
        dest='message',
        required=True,
        help='Message text (required)'
    )
    return parser.parse_args()


@contextlib.asynccontextmanager
async def open_connection(host: str, port: int) -> tuple:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


async def register(connection, username: str) -> dict | None:
    reader, writer = connection

    await reader.readline()
    writer.write(f'\n'.encode())

    await reader.readline()
    writer.write(f'{sanitize(username)}\n'.encode())

    response = await reader.readline()
    credentials = json.loads(response.decode())
    if not credentials:
        logging.error("Server Error: can't get token")
        return

    async with aiofiles.open('credentials.json', 'w') as file:
        await file.write(json.dumps(credentials))
        logging.info("Username and token saved.")

    return credentials


async def authorize(connection, token: str) -> bool:
    reader, writer = connection

    text = await reader.readline()
    logger.debug(text.decode())

    writer.write(f"{sanitize(token)}\n".encode())
    logger.debug(f'Sent token_or_username {token}')
    await writer.drain()

    response = await reader.readline()
    try:
        assert json.loads(response) is None
        logging.error('The token is invalid. Check the token or register again.')
        return False
    except AssertionError:
        return True


async def send_message(connection, message):
    _, writer = connection
    writer.write(f'{sanitize(message)}\n\n'.encode())
    await writer.drain()


async def submit_message(args):
    if args.token:
        async with open_connection(args.host, args.port) as connection:
            if await authorize(connection, args.token):
                await send_message(connection, args.message)

    else:
        async with open_connection(args.host, args.port) as connection:
            await register(connection, args.username)
            await send_message(connection, args.message)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(submit_message(args))


if __name__ == '__main__':
    main()

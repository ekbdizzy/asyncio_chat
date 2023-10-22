import asyncio
import argparse
import json
import logging

import aiofiles
from environ import Env

from streaming_tools import open_connection


logger = logging.getLogger('sender')


def sanitize(string: str) -> str:
    """Replace \n and \t from string. Can be updated with new replacements."""
    string = string.replace('\n', ' ')
    string = string.replace('\t', '    ')
    return string


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
        default='',
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


async def register(connection, username: str) -> dict | None:
    reader, writer = connection

    await reader.readline()
    writer.write(f'\n'.encode())
    await writer.drain()

    await reader.readline()
    writer.write(f'{sanitize(username)}\n'.encode())
    await writer.drain()

    response = await reader.readline()
    credentials = json.loads(response.decode())
    if not credentials:
        logging.error("Server Error: can't get token")
        return

    async with aiofiles.open('credentials.json', 'w') as file:
        await file.write(json.dumps(credentials))
        logging.info("Username and token saved.")

    return credentials


async def authorize(connection, token: str) -> dict | bool:
    reader, writer = connection

    text = await reader.readline()
    logger.debug(text.decode())

    writer.write(f"{sanitize(token)}\n".encode())
    await writer.drain()
    logger.debug(f'Sent token_or_username {token}')

    response = await reader.readline()
    if json.loads(response):
        return json.loads(response)
    logging.error('The token is invalid. Check the token or register again.')
    return False


async def send_message(connection, message):
    _, writer = connection
    writer.write(f'{sanitize(message)}\n\n'.encode())
    await writer.drain()


async def submit_message(args):
    async with open_connection(args.host, args.port) as connection:
        if not (args.token and await authorize(connection, args.token)):
            await register(connection, args.username)
        await send_message(connection, args.message)


def main():
    env = Env()
    env.read_env()
    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(submit_message(args))


if __name__ == '__main__':
    main()

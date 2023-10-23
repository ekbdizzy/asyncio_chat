import asyncio
import contextlib
import datetime
import logging
import json

import aiofiles

logger = logging.getLogger('sender')


@contextlib.asynccontextmanager
async def open_connection(host: str, port: int) -> tuple:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


def add_timestamp(message: str | bytes, stamp_format: str = "[%d.%m.%Y %H:%M]") -> str:
    """Add timestamp and decode bytes to string if needed."""
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    timestamp = datetime.datetime.now().strftime(stamp_format)
    return f'{timestamp} {message.strip()}'


def sanitize(string: str) -> str:
    """Replace \n and \t from string. Can be updated with new replacements."""
    string = string.replace('\n', ' ')
    string = string.replace('\t', '    ')
    return string


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

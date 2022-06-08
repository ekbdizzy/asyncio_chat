import asyncio
import argparse
import contextlib
import json
import logging

from environ import Env

env = Env()
env.read_env()
logger = logging.getLogger('sender')


@contextlib.asynccontextmanager
async def open_connection(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


async def authorize(connection, token):
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


async def write_message(writer, args):
    writer.write(f'{args.message}\n\n'.encode())
    await writer.drain()


async def send_message(args):
    async with open_connection(host=args.host, port=args.port) as connection:
        reader, writer = connection
        token = env('ACCOUNT_TOKEN')
        authorized = await authorize(connection, token)
        if authorized:
            await write_message(writer, args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, default='minechat.dvmn.org', help='Host name')
    parser.add_argument('--port', dest='port', type=int, default=5050, help='Port number')
    parser.add_argument('-m', '--message', dest='message', help='Message text')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    asyncio.run(send_message(args))


if __name__ == '__main__':
    main()

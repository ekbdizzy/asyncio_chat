import asyncio
import argparse
import logging

from environ import Env

env = Env()
env.read_env()
logger = logging.getLogger('sender')


async def write_message(message):
    reader, writer = await asyncio.open_connection(
        host=env('HOST'), port=5050
    )

    text = await reader.readline()
    logger.info(text.decode())

    writer.write(f"{env('ACCOUNT_TOKEN')}\n".encode())
    await writer.drain()

    text = await reader.readline()
    logger.info(text.decode())

    writer.write(f'{message}\n\n'.encode())
    await writer.drain()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--message', dest='message', help='Message text')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(write_message(args.message))


if __name__ == '__main__':
    main()

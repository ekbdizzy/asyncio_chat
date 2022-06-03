import asyncio
import argparse

from environ import Env

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--message', dest='message', help='Message text')

env = Env()
env.read_env()


async def write_message(message):
    reader, writer = await asyncio.open_connection(
        host=env('HOST'), port=5050
    )

    await reader.readline()
    writer.write(f"{env('ACCOUNT_TOKEN')}\n".encode())
    await writer.drain()

    phrase = await reader.readline()
    print(phrase)

    writer.write(f'{message}\n\n'.encode())
    await writer.drain()


if __name__ == '__main__':
    args = parser.parse_args()
    asyncio.run(write_message(args.message))

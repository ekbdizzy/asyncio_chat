import asyncio
import argparse
import os.path
import datetime

import aiofiles

HOST = 'minechat.dvmn.org'
PORT = 5000
FILENAME = 'messages.txt'

parser = argparse.ArgumentParser()
parser.add_argument('--host', dest='host', default=HOST, type=str, help='Host name')
parser.add_argument('--port', dest='port', default=5000, type=int, help='Port number')
parser.add_argument('--history', dest='filename', default=FILENAME, type=str, help='File to save history')


async def tcp_echo_client(host, port, filename, message=""):
    reader, writer = await asyncio.open_connection(
        host=host, port=port
    )

    phrase = await reader.readline()

    async with aiofiles.open(filename, 'a') as file:
        phrase_with_timestamp = f'{datetime.datetime.now().strftime("[%d.%m.%Y %H:%M]")} {phrase.decode("utf-8")}'
        print(phrase_with_timestamp)
        await file.write(phrase_with_timestamp)


if __name__ == '__main__':
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
    args = parser.parse_args()
    while True:
        asyncio.run(tcp_echo_client(args.host, args.port, args.filename, ''))

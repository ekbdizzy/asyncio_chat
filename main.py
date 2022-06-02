import asyncio
import os.path
import datetime

import aiofiles

HOST = 'minechat.dvmn.org'
PORT = 5000
FILENAME = 'messages.txt'


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        host=HOST, port=PORT
    )

    phrase = await reader.readline()

    async with aiofiles.open(FILENAME, 'a') as file:
        phrase_with_timestamp = f'{datetime.datetime.now().strftime("[%d.%m.%Y %H:%M]")} {phrase.decode("utf-8")}'
        print(phrase_with_timestamp)
        await file.write(phrase_with_timestamp)


if __name__ == '__main__':
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
    while True:
        asyncio.run(tcp_echo_client(''))

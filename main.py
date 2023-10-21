import argparse
import asyncio
import time

from environ import Env

from streaming_tools import open_connection, add_timestamp
import gui

loop = asyncio.get_event_loop()

messages_queue = asyncio.Queue()
sending_queue = asyncio.Queue()
status_updates_queue = asyncio.Queue()


async def generate_msgs(queue: asyncio.Queue):
    while True:
        queue.put_nowait(time.time())
        await asyncio.sleep(1)


async def greeting(queue: asyncio.Queue):
    queue.put_nowait('Hi there')
    queue.put_nowait('Welcome to the chat')


async def read_msgs(host: str, port: int, queue: asyncio.Queue):
    """Read messages from server."""
    async with open_connection(host, port) as connection:
        while True:
            reader, writer = connection
            phrase = await reader.readline()
            stamped_phrase = add_timestamp(phrase)
            queue.put_nowait(stamped_phrase)



async def main():

    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, help='Host name')
    parser.add_argument('--port_read', dest='port_read', type=int, help='Read port number')
    args = parser.parse_args()

    host = args.host or env.str('HOST', 'minechat.dvmn.org')
    port_read = args.port_read or env.int('PORT_READ', 5000)

    loop = await asyncio.gather(
        gui.draw(messages_queue, sending_queue, status_updates_queue),
        greeting(messages_queue),
        generate_msgs(messages_queue),
        read_msgs(host, port_read, messages_queue),
    )

    loop.run_until_complete(gui.draw(messages_queue, sending_queue, status_updates_queue))


if __name__ == "__main__":
    asyncio.run(main())


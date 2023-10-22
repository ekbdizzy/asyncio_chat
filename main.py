import argparse
import asyncio
import time
import logging
from tkinter import messagebox
import aiofiles
from environ import Env

from streaming_tools import open_connection, add_timestamp
from submit_message import authorize, send_message
import gui

messages_queue = asyncio.Queue()
sending_queue = asyncio.Queue()
saving_queue = asyncio.Queue()
status_updates_queue = asyncio.Queue()


class InvalidToken(Exception):
    def __init__(self):
        messagebox.showinfo("Invalid Token", "Your token is not valid. Please check it and try again.")


async def load_msg_history(filepath: str, queue: asyncio.Queue):
    """Load messages history and place it in the beginning of messages."""
    async with aiofiles.open(filepath) as file:
        contents = await file.read()
        await queue.put(contents.strip())


async def generate_msgs(queue: asyncio.Queue):
    while True:
        queue.put_nowait(time.time())
        await asyncio.sleep(1)



async def send_msgs(host, port, queue):
    async with open_connection(host, port) as connection:
        creds = await authorize(connection, token)
        if not creds:
            raise InvalidToken
        while True:
            message = await queue.get()
            await send_message(connection, message)


async def save_msgs(filepath: str, queue: asyncio.Queue):
    """Save messages from the queue (which had been read from server) to the chat history file."""
    while True:
        async with aiofiles.open(filepath, 'a') as file:
            phrase = await queue.get()
            await file.write(f'{phrase}\n')


async def read_msgs(host: str, port: int, queue: asyncio.Queue):
    """Read messages from server."""
    async with open_connection(host, port) as connection:
        while True:
            reader, writer = connection
            phrase = await reader.readline()
            stamped_phrase = add_timestamp(phrase)
            queue.put_nowait(stamped_phrase)
            await saving_queue.put(stamped_phrase)


async def main():

    loop = await asyncio.gather(
        gui.draw(messages_queue, sending_queue, status_updates_queue),
        load_msg_history(filepath, messages_queue),
        # generate_msgs(messages_queue),
        read_msgs(host, port_read, messages_queue),
        save_msgs(filepath, saving_queue),
        send_msgs(host, port_write, sending_queue),
        return_exceptions=True,
    )

    loop.run_until_complete(gui.draw(messages_queue, sending_queue, status_updates_queue))


if __name__ == "__main__":

    env = Env()
    env.read_env()

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, help='Host name')
    parser.add_argument('--port_read', dest='port_read', type=int, help='Read port number')
    parser.add_argument('--history', dest='filepath', type=str, help='File to save history')
    parser.add_argument('--port_write', dest='port_write', type=int, default=5050, help='Write port number')
    parser.add_argument('--token', dest='token', type=str, help='Token of registered user.')
    parser.add_argument('--username', dest='username', default='', type=str, help='Username of registered user.')

    args = parser.parse_args()

    host = args.host or env.str('HOST', 'minechat.dvmn.org')
    port_read = args.port_read or env.int('PORT_READ', 5000)
    filepath = args.filepath or env.str('FILEPATH', 'chat.history')
    port_write = args.port_write or env.int('PORT_WRITE', 5050)
    token = args.token or env.str("ACCOUNT_TOKEN")
    username = args.username

    asyncio.run(main())


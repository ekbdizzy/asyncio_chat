import argparse
import asyncio
import logging
import socket

from anyio import create_task_group, run
from async_timeout import timeout
import aiofiles
from environ import Env
from tkinter import messagebox, TclError

import gui
from streaming_tools import authorize, send_message, open_connection, add_timestamp

CONNECTION_TIMEOUT = 5
READ_TIMEOUT = 5
PING_TIMEOUT = 2

messages_queue = asyncio.Queue()
sending_queue = asyncio.Queue()
saving_queue = asyncio.Queue()
watchdog_queue = asyncio.Queue()
status_updates_queue = asyncio.Queue()


class InvalidToken(Exception):
    def __init__(self):
        messagebox.showinfo("Invalid Token", "Your token is not valid. Please check it and try again.")


async def load_msg_history(filepath: str, queue: asyncio.Queue):
    """Load messages history and place it in the beginning of messages."""
    async with aiofiles.open(filepath) as file:
        contents = await file.read()
        await queue.put(contents.strip())


async def send_msgs(host, port, queue):
    status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)
    async with open_connection(host, port) as connection:
        status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)
        await watchdog_queue.put("Prompt before auth")
        creds = await authorize(connection, token)
        if not creds:
            raise InvalidToken
        event = gui.NicknameReceived(creds["nickname"])
        await watchdog_queue.put("Authorization done")
        status_updates_queue.put_nowait(event)

        while True:
            message = await queue.get()
            await send_message(connection, message)
            await watchdog_queue.put("Message sent")


async def save_msgs(filepath: str, queue: asyncio.Queue):
    """Save messages from the queue (which had been read from server) to the chat history file."""
    while True:
        async with aiofiles.open(filepath, 'a') as file:
            phrase = await queue.get()
            await file.write(f'{phrase}\n')


async def read_msgs(host: str, port: int, queue: asyncio.Queue):
    """Read messages from server."""
    status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.INITIATED)
    async with open_connection(host, port) as connection:
        status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)
        while True:
            reader, writer = connection
            phrase = await asyncio.wait_for(reader.readline(), READ_TIMEOUT)
            stamped_phrase = add_timestamp(phrase)
            queue.put_nowait(stamped_phrase)
            await watchdog_queue.put("New message in chat")
            await saving_queue.put(stamped_phrase)


async def watch_for_connection(queue: asyncio.Queue):
    while True:
        try:
            async with timeout(CONNECTION_TIMEOUT) as cm:
                message = await queue.get()
                watchdog_logger.info(message)
        except asyncio.TimeoutError:
            if cm.expired:
                watchdog_logger.warning(f"{CONNECTION_TIMEOUT}s timeout is elapsed")
                raise ConnectionError


async def ping(queue: asyncio.Queue):
    """Send the blank messages to the server to test the connection."""
    while True:
        queue.put_nowait("")
        await asyncio.sleep(PING_TIMEOUT)


async def handle_connection():
    while True:
        try:
            async with create_task_group() as task_group:
                task_group.start_soon(read_msgs, host, port_read, messages_queue)
                task_group.start_soon(send_msgs, host, port_write, sending_queue)
                task_group.start_soon(watch_for_connection, watchdog_queue)
                task_group.start_soon(ping, sending_queue)
        except* (ConnectionError, TimeoutError, socket.gaierror):
            logger.debug("Reconnect")
            status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.INITIATED)
            status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.INITIATED)
            status_updates_queue.put_nowait(gui.NicknameReceived("unknown"))
            await asyncio.sleep(1)


async def main():
    async with create_task_group() as task_group:
        task_group.start_soon(gui.draw, messages_queue, sending_queue, status_updates_queue)
        task_group.start_soon(load_msg_history, filepath, messages_queue)
        task_group.start_soon(save_msgs, filepath, saving_queue)
        task_group.start_soon(handle_connection)

if __name__ == "__main__":
    env = Env()
    env.read_env()

    logger = logging.getLogger("main")
    logger_handler = logging.StreamHandler()
    logger_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_fmt)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logger_handler)

    watchdog_logger = logging.getLogger(name="watchdog_logger")
    watchdog_handler = logging.StreamHandler()
    watchdog_logger_fmt = logging.Formatter(fmt='[%(created)d] Connection is alive. %(message)s')
    watchdog_handler.setFormatter(watchdog_logger_fmt)
    watchdog_logger.setLevel(logging.DEBUG)
    watchdog_logger.addHandler(watchdog_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, help='Host name')
    parser.add_argument('--port_read', dest='port_read', type=int, help='Read port number')
    parser.add_argument('--history', dest='filepath', type=str, help='File to save history')
    parser.add_argument('--port_write', dest='port_write', type=int, default=5050, help='Write port number')
    parser.add_argument('--token', dest='token', type=str, help='Token of registered user.')

    args = parser.parse_args()

    host = args.host or env.str('HOST', 'minechat.dvmn.org')
    port_read = args.port_read or env.int('PORT_READ', 5000)
    filepath = args.filepath or env.str('FILEPATH', 'chat.history')
    port_write = args.port_write or env.int('PORT_WRITE', 5050)
    token = args.token or env.str("ACCOUNT_TOKEN")

    try:
        run(main)
    except* InvalidToken:
        logger.debug('Incorrect token. Exit.')
    except* (KeyboardInterrupt, TclError, asyncio.exceptions.CancelledError):
        logger.debug('The chat is closed. Exit.')

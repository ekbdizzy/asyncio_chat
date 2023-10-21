import asyncio
import time
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

loop = await asyncio.gather(
    gui.draw(messages_queue, sending_queue, status_updates_queue),
    greeting(messages_queue),
    generate_msgs(messages_queue),
)

async def main():
    loop.run_until_complete(gui.draw(messages_queue, sending_queue, status_updates_queue))


if __name__ == "__main__":
    asyncio.run(main())


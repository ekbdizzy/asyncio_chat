import asyncio
import contextlib


@contextlib.asynccontextmanager
async def open_connection(host: str, port: int) -> tuple:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

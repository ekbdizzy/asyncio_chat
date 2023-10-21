import asyncio
import contextlib
import datetime


@contextlib.asynccontextmanager
async def open_connection(host: str, port: int) -> tuple:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


def add_timestamp(message: str | bytes, stamp_format: str = "[%d.%m.%Y %H:%M]") -> str:
    """Add timestamp and decode bytes to string if needed."""
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    timestamp = datetime.datetime.now().strftime(stamp_format)
    return f'{timestamp} {message.strip()}'
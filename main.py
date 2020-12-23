import asyncio

HOST = "minechat.dvmn.org"
PORT = 5000


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        host=HOST, port=PORT
    )


    print(f'Send {message!r}')
    writer.write(message.encode())

    data  = await reader.read(100)
    print(f"Received {data.decode()!r}")

    print("Close the connection")
    writer.close()

asyncio.run(tcp_echo_client("Hello"))



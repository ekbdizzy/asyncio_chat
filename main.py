import asyncio

HOST = "minechat.dvmn.org"
PORT = 5000


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        host=HOST, port=PORT
    )

    # print(f'Send {message!r}')
    # writer.write(message.encode())

    data = await reader.readline()
    print(f"{data.decode()!r}")

    # print("Close the connection")
    # writer.close()


if __name__ == "__main__":
    while True:
        asyncio.run(tcp_echo_client(""))

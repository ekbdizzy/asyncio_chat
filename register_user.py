import asyncio
import json

HOST = 'minechat.dvmn.org'
PORT = 5050


async def register_user(username):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    await reader.readline()
    writer.write(f'\n'.encode())

    await reader.readline()
    writer.write(f'{username}\n'.encode())

    message = await reader.readline()
    credentials = json.loads(message.decode())
    print(credentials)
    return credentials


if __name__ == '__main__':
    asyncio.run(register_user('new_user'))

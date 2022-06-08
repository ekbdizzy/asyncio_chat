## CLI chat client on asyncio.
Chat client with CLI interface for minechat.dvmn.org.
It's a lesson of [Async Python](https://dvmn.org/modules/async-python/) course by Devman. 
---
## Install

1. Create [virtualenv](https://docs.python.org/3/library/venv.html) of Python > 3.7 and activate it:

```bash
python3 -m virtualenv venv
source venv/bin/activate
```

2. Install requirements

```bash
pip install -r requirements.txt
```

3. You also can create `.env` file to save ENVIRONMENT variables and use it instead of CLI args.

```bash
HOST=minechat.dvmn.org
PORT=5000
FILENAME=chat.history
```
---
## Run scripts

### Read chat
You can run script with args:
* `--host` hostname, default is `minechat.dvmn.org`
* `--port` port number, default is `5000`
* `--history` filepath to save history, default is `chat.history`

```bash
python read_chat.py --host minechat.dvmn.org --port 5000 --history 'chat.history'
```
---

### Write message to chat

You can run script with args:
* `--message` (REQUIRED) message you want to send.
* `--host` hostname, default is `minechat.dvmn.org`
* `--port` port number, default is `5050`
* `--username` registers new user with this username and sends message from his name 
* `--token` if token, tries to log in and send message from that account.

```bash
python submit_message.py --message
```


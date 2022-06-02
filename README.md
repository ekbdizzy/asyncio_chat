## Simple chat on asyncio

## How to run

1. Create [virtualenv](https://docs.python.org/3/library/venv.html) of Python > 3.7 and activate it:

```bash
python3 -m virtualenv venv
source venv/bin/activate
```

2. Install requirements

```bash
pip install -r requirements.txt
```

3. Run script with args:

* `--host` your_hostname, default `minechat.dvmn.org`
* `--port` port number, default `5000`
* `--history` filepath to save history, default `chat.history`
*

```bash
python main.py --host your_hostname --port YOUR_PORT --history file_to_save_history
```

4. You also can create `.env` file to save ENVIRONMENT variables and use it instead of CLI args.

```bash
HOST=minechat.dvmn.org
PORT=5000
FILENAME=chat.history
```

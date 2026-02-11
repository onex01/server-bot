# Bot for Telegram that manages your server

The functionality is very limited, but it may be more convenient than connecting via SSH to see the load on your host.
You can send prepared commands, or write your own if they are supported. View the status of your servers, load on CPU, RAM, SWAP, DISK, Enternet.

Before use, you must have a `.env` file created in the root of the bot
```
BOT_TOKEN=You_bot_token
ADMIN_IDS=1234567890
```
In `config.py` you can write your web services and monitor them. This is located in the line `SERVICES = {}`, write your services using `,`, for example, I left mine in the source code.

In `commands.py` you can add your own commands that you need. In the line `predefined_commands = {}`, I also left basic shortcut commands in the example
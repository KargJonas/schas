# S.C.H.A.S. - Supreme Channel Help Assistent Service

#### The number 1. JKU Discord support bot.

## Getting started

### Set up Discord API access

- Open Discord app overview [here](https://discord.com/developers/applications)
- Click on `New Application`
- Choose application name
- Go to `General Information` section
- Choose a name for your bot (this is only shown in your Discord API dashboard)
- Go to the `Bot` section
- Choose a username. This will be visible in Discord
- Toggle `MESSAGE CONTENT INTENT` to true
- Save changes
- Click "Reset Token" below "username", to get your API access token.
  You'll need to put this into the .env file - see below

### Create `.env` file

To set up the token you will have to create a `.env` file in the root of the project.
It should look like this:
```
TOKEN=<your_api_token_here>
```

The reason we put this in a `.env` file instead of a python variable is that API keys are considered sensitive information.
Anyone with this key could use your API access, which is why we don't want it directly in the source code.

The `.env` is excluded by the `.gitignore` rules, which makes it a lot more difficult to accidentally commit your API access token,

### How to start the bot

```bash
python3 bot.py
```

In the log, you should be able to find a `Bot invite link` that you can click to add the bot to your server.

```
$ python3 bot.py 
2025-01-03 23:03:00 INFO     discord.client logging in using static token
Loaded extension 'calendar'
Logged in as S.C.H.A.S.
discord.py API version: 2.4.0
Python version: 3.10.12
Running on: Linux 6.8.0-49-generic (posix)
Bot invite link: https://discord.com/oauth2/authorize?client_id=1324822783283608180&scope=bot+applications.commands&permissions=3072
-------------------
```

### Add new functionality

New features should be added as "cogs" inside the `/cogs` directory.
You can do this by simply creating a new file inside of that dir.
You can also have a look at `/cogs/calendar` as a reference.
Cogs are similar to plugins. All files inside `/cogs` will be loaded automatically, so you don't need to register your cog anywhere.

Have a look at `/database/models.py`. This file contains the DB schema.
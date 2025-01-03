# S.C.H.A.S. - Supreme Channel Help Assistent Service

#### The number 1. JKU Discord support bot.

## Getting started

### Set up Discord API access

- Create a Discord bot [here](https://discord.com/developers/applications)
  - Choose a name (this is only shown in your Discord API dashboard)
  - Go to the `Bot` section
  - Choose a username. This will be visible in Discord
  - Toggle "message content intent to true"
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

### Add new functionality

New features should be added as "cogs" inside the `/cogs` directory.
You can do this by simply creating a new file inside of that dir.
You can also have a look at `/cogs/calendar` as a reference.
Cogs are similar to plugins. All files inside `/cogs` will be loaded automatically, so you don't need to register your cog anywhere.

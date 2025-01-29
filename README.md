# S.C.H.A.S. - Supreme Channel Help Assistent Service

This JKU Discord Bot is designed to help students and faculty stay updated with their schedules, on-campus meal options, occupancy levels at the JKU Mensa, and the latest news and events from JKU. 
It also provides helpful navigation for campus rooms. Below is an overview of the bot’s capabilities and how to get started.

## Team
- Lorenz Bader k12212953
- Philip Buchegger k12204693
- Jonas Karg k12213152

## Features
### Calendar Integration
- Set and validate your KUSSS calendar link, then retrieve daily schedules or upcoming tests.
- Navigation links for campus rooms, utilizing Google Maps to provide directions.

### Food / Mensa Menus
- Retrieve the latest menus from the JKU Mensa and Raab Mensa.
- Seamlessly display vegetarian and non-vegetarian options, along with approximate prices.

### Mensa Occupancy
- Estimate current and future occupancy levels at the JKU Mensa, allowing you to plan your meals around busy times.

### News and Events
- Fetch the most recent news from the official JKU news page.
- Retrieve upcoming events from the JKU events page.
- Optional parameter to specify how much news or event items to display.

### ÖH Events
- Fetches upcoming ÖH JKU events

### Custom Help Command
- A personalized help command (“!help” or “!h”) that lists all available commands and provides basic usage instructions.
- Automatically triggered if a user enters an unknown command.

## Command Overview
Below are some of the main commands (you can see them all via “!help” or “!h” in Discord) (brackets [] are optional parameters and angle brackets <> are required parameters):

- `!setCalendar [link]`
Sets your personal KUSSS calendar link, validates it, and stores it for further use.

- `!testInfo`
Lists your upcoming tests based on the KUSSS calendar data.

- `!calendarInfo [dd.mm.yyyy]`
Fetches your schedule for a specific date.

- `!where <room>`
Provides a Google Maps navigation link for a room on campus.

- `!getMensaFood`
Shows the weekly menu from the JKU Mensa.

- `!getRaabFood`
Shows the weekly menu from the Raab Mensa.

- `!mensaStatus [weekday]`
Displays real-time occupancy info and forecasts for the JKU Mensa (weekday = Monday, Tuesday, ...).

- `!getNews [number]`
Fetches recent news items from the JKU news page (3 items by default, max 9).

- `!getEvents [number]`
Fetches upcoming events from the JKU events page (3 items by default, max 9).

- `!getOehEvents`
Fetches upcoming ÖH events.

- `!help or !h`
Shows your custom help command with detailed usage instructions.

## How to run the bot locally

### Set up Discord API access (if API key not given)

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

### How to run the bot

#### Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Install dependencies
```bash
python3 -m pip install -r requirements.txt
```

#### Run the bot
```bash
python3 bot.py
```

In the log, you should be able to find a `Bot invite link` that you can click *to add the bot to your server*.

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

If you need a server to test the bot on, feel free to join our [Schas Test Server](https://discord.gg/esjqgDc6Bs) (A.k.a STS).

import logging
import os
import platform
import random

from pathlib import Path
from discord.ext import commands, tasks
from dotenv import load_dotenv
import discord

from database.database import DatabaseManager
from util.load_json import load_json


# Load config
config = load_json("config.json")

# Start logging
logger = logging.getLogger(config.logging.name)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler(filename=config.logging.file, encoding="utf-8", mode="w"))


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(config.prefix),
            intents=intents,
            help_command=None,
        )
        self.logger = logger
        self.config = config
        self.database = None

    # Load all cogs from the cogs directory.
    async def load_cogs(self) -> None:
        cogs_dir = Path(__file__).parent / "cogs"
        for file in cogs_dir.glob("*.py"):
            extension = file.stem
            try:
                await self.load_extension(f"cogs.{extension}")
                self.logger.info(f"Loaded extension '{extension}'")
            except Exception as e:
                self.logger.error(f"Failed to load extension {extension}\n{type(e).__name__}: {e}")

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        # Update the bot's status message.
        statuses = ["with calendars!", "with scheduling!", "with time!"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        # Wait until the bot is ready before starting the status task.
        await self.wait_until_ready()

    # Initialize the bot's components.
    async def setup_hook(self) -> None:
        await self.load_cogs()
        
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        
        self.database = DatabaseManager()

        # This just defines the permissions required by this bot
        # these will be encoded into the invite link.
        # This way, users who want to add the bot to their server can see what they agree to.
        permissions = discord.Permissions(
            send_messages=True,
            read_messages=True,
            
            ### could be that we will need these for some features:
            # embed_links=True,
            # attach_files=True,
            # read_message_history=True,
        )

        # Generate and print invite link
        invite_link = discord.utils.oauth_url(
            self.user.id,
            permissions=permissions
        )

        self.logger.info(f"Bot invite link: {invite_link}")
        self.logger.info("-------------------")

    # Handle command errors.
    async def on_command_error(self, context: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"Please slow down - Try again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            #display help command if command not found
            help_cmd = self.get_command("help")
            if help_cmd:
                await context.invoke(help_cmd)
        else:
            raise error


def main():
    load_dotenv()
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("No token found in .env file")
    
    bot = DiscordBot()
    bot.run(token)


# Start the bot.
if __name__ == "__main__":
    main()

# cogs/calendar.py
import discord
from discord.ext import commands
from database.models import User
import requests
import re
from datetime import datetime

from util.load_json import load_json


# Load config
config = load_json("config.json")

class Calendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Validates the KUSSS calendar URL and returns the calendar content if valid.
    # Returns None if invalid or unreachable.
    async def fetch_and_validate_calendar(self, url: str, dm_channel) -> str | None:
        # Check URL format
        if not re.match(r'https://www\.kusss\.jku\.at/kusss/published-calendar\.action\?token=[\w-]+&lang=\w+', url):
            await dm_channel.send("Invalid link format.")
            return None
        
        try:
            # Try to fetch the calendar
            response = requests.get(url, timeout=5)
            
            # Check if request was successful
            if response.status_code != 200:
                await dm_channel.send(f"Could not load calendar from link: Got status code {response.status_code}.")
                return None
            
            # Check if content type is iCal
            content_type = response.headers.get('content-type', '').lower()
            if 'text/calendar' not in content_type:
                await dm_channel.send(f"Could not load calendar from link: Invalid content type.")
                return None
            
            calendar_content = response.text

            # Check calendar size (512KB limit)
            if len(calendar_content.encode('utf-8')) > config.limits.max_cal_size_bytes:
                return None

            # Verify it starts with BEGIN:VCALENDAR
            if not calendar_content.strip().startswith('BEGIN:VCALENDAR'):
                await dm_channel.send(f"Could not load calendar from link: Invalid file content.")
                return None
                
            return calendar_content
            
        except (requests.RequestException, ValueError):
            await dm_channel.send(f"Could not load calendar from link: Request failed.")
            return None

    @commands.command(name="setcalendar", description="Set your KUSSS calendar link")
    async def setcalendar(self, ctx):
        await ctx.send(f"I've sent you a DM {ctx.author.mention}!")
        
        try:
            # Create private channel for user
            dm_channel = await ctx.author.create_dm()

            # Ask user for link
            await dm_channel.send(
                "Please send your KUSSS calendar link.\n" +
                f"You can find it at: {config.links.kusss_cal_page}"
            )
            
            # Keep asking until we get a valid link or timeout
            while True:

                # Wait until user sends the link
                msg = await self.bot.wait_for('message', timeout=config.limits.user_timeout_duration)
                
                if msg.content.lower() == 'cancel':
                    await dm_channel.send("Calendar setup cancelled.")
                    return
                
                calendar_data = await self.fetch_and_validate_calendar(msg.content, dm_channel)
                
                if not calendar_data:
                    continue

                # Check if user already exists in DB
                session = self.bot.database.get_session()
                user = session.query(User).get(str(ctx.author.id))

                # Create new user or update existing user
                if user is None:
                    user = User(
                        id=str(ctx.author.id),
                        calendar_link=msg.content,
                        calendar_cache=calendar_data,
                        cached_at=datetime.utcnow()
                    )
                    session.add(user)
                else:
                    user.calendar_link = msg.content
                    user.calendar_cache = calendar_data
                    user.cached_at = datetime.utcnow()
                
                # Persist changes
                session.commit()
                session.close()
                
                await dm_channel.send("Your calendar link has been updated!")
                break

        except discord.Forbidden:
            await ctx.send("I couldn't send you a DM.\nPlease check your privacy settings and try again.")
        except TimeoutError:
            await dm_channel.send("Time's up!\nPlease try again.")

async def setup(bot):
    await bot.add_cog(Calendar(bot))

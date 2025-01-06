# cogs/calendar.py
import re
from datetime import datetime, timezone, timedelta

import discord
import requests
from discord.ext import commands

from calendarHelpers.IcalStudentCalendar import IcalStudentCalendar
from database.models import User
from util.load_json import load_json

# Load config
config = load_json("config.json")

hoursToCache = 3
hoursToCacheError = 24


class Calendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Validates the KUSSS calendar URL and returns the calendar content if valid.
    # Returns None if invalid or unreachable.
    async def fetch_and_validate_calendar(self, url: str) -> str | None:
        # Check URL format
        if not re.match(r'https://www\.kusss\.jku\.at/kusss/published-calendar\.action\?token=[\w-]+&lang=\w+', url):
            raise CalendarInvalidLinkFormat

        try:
            # Try to fetch the calendar
            response = requests.get(url, timeout=5)

            # Check if request was successful
            if response.status_code != 200:
                raise CalendarHTTPException(response.status_code)

            # Check if content type is iCal
            content_type = response.headers.get('content-type', '').lower()
            if 'text/calendar' not in content_type:
                raise CalendarInvalidContent

            calendar_content = response.text

            # Check calendar size (512KB limit)
            if len(calendar_content.encode('utf-8')) > config.limits.max_cal_size_bytes:
                raise CalendarSizeException

            # Verify it starts with BEGIN:VCALENDAR
            if not calendar_content.strip().startswith('BEGIN:VCALENDAR'):
                raise CalendarInvalidContent

            return calendar_content

        except (requests.RequestException, ValueError):
            raise CalendarRequestFailed

    async def fetch_and_validate_calendar_dm_errors(self, url: str, dm_channel) -> str | None:
        try:
            return self.fetch_and_validate_calendar(url)
        except CalendarHTTPException as e:
            await dm_channel.send(f"Could not load calendar from link: Got status code {e.code}.")
        except CalendarInvalidContent:
            await dm_channel.send("Could not load calendar from link: Invalid content type.")
        except CalendarSizeException:
            return None
        except CalendarRequestFailed:
            await dm_channel.send("Could not load calendar from link: Request failed.")
        except CalendarInvalidLinkFormat:
            await dm_channel.send("Invalid link format.")

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

                calendar_data = await self.fetch_and_validate_calendar_dm_errors(msg.content, dm_channel)

                if not calendar_data:
                    continue
                session = self.bot.database.get_session()
                try:
                    # Check if user already exists in DB
                    user = session.query(User).get(str(ctx.author.id))

                    # Create new user or update existing user
                    if user is None:
                        user = User(
                            id=str(ctx.author.id),
                            calendar_link=msg.content,
                            calendar_cache=calendar_data,
                            cached_at=datetime.now(timezone.utc)
                        )
                        session.add(user)
                    else:
                        user.calendar_link = msg.content
                        user.calendar_cache = calendar_data
                        user.cached_at = datetime.now(timezone.utc)
                finally:
                    session.commit()
                    session.close()

                await dm_channel.send("Your calendar link has been updated!")
                break

        except discord.Forbidden:
            await ctx.send("I couldn't send you a DM.\nPlease check your privacy settings and try again.")
        except TimeoutError:
            await dm_channel.send("Time's up!\nPlease try again.")

    def getCalendarInfo(self, authorId):
        session = self.bot.database.get_session()
        content = None
        try:
            user = session.query(User).get(str(authorId))
            if user is None:
                return None
            else:
                content = user.calendar_cache
                if user.cached_at < datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
                        hours=hoursToCache) or user.calendar_cache is None:
                    content = self.fetch_and_validate_calendar(user.calendar_link)
                    if content is not None:
                        user.calendar_cache = content
                        user.cached_at = datetime.now(timezone.utc)
                        session.commit()
                    elif user.calendar_cache is None or user.cached_at < datetime.now(timezone.utc).replace(
                            tzinfo=None) - timedelta(
                        hours=hoursToCacheError):
                        raise CalendarInvalid()
                    content = user.calendar_cache
                    session.commit()

        finally:
            session.close()
        return IcalStudentCalendar(content)

    @commands.command(name="getRoomsForToday", description="Set your KUSSS calendar link")
    async def getEventsForDay(self, ctx):
        try:
            calendar = self.getCalendarInfo(ctx.author.id)
        except Exception:
            ctx.send("Something is wrong with your calendar. Please set it again using setcalendar.")
            return

        events = calendar.getEventsForDay(datetime.now(timezone.utc))
        # events = calendar.getEventsForDay(datetime(2025, 1, 8))

        if len(events) == 0:
            await ctx.send("You have no events today!")
            return

        text = "Alright here are your events for today:\n\n"

        for event in events:
            timestamp: int = int(event.startTime.timestamp())
            text += f"{event.title} with {event.lecturer} at <t:{timestamp}:t> in {event.room}\n"

        await ctx.send(text)


class CalendarHTTPException(Exception):
    def __init__(self, code):
        self.code = code


class CalendarInvalidContent(Exception):
    pass


class CalendarSizeException(Exception):
    pass


class CalendarRequestFailed(Exception):
    pass


class CalendarInvalidLinkFormat(Exception):
    pass


class CalendarInvalid(Exception):
    pass


async def setup(bot):
    await bot.add_cog(Calendar(bot))

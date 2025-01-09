# cogs/calendar.py
import re
from datetime import datetime, timezone, timedelta

import discord
import requests
from discord.ext import commands

from calendarHelpers.IcalStudentCalendar import IcalStudentCalendar
from database.models import User
from util.load_json import load_json

import xml.etree.ElementTree as ET

# Load config
config = load_json("config.json")

hoursToCache = 3
hoursToCacheError = 24


def find_coordinates_in_gpx(room_name):

    file_path = "resources/JKU.gpx"

    room_name = room_name.lower().replace(" ", "")

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        namespace = {'': 'http://www.topografix.com/GPX/1/1'}

        for wpt in root.findall('wpt', namespace):
            #check if name matches
            name_tag = wpt.find('{http://www.topografix.com/GPX/1/1}name')
            if name_tag is not None:
                normalized_name = name_tag.text.lower().replace(" ", "")

                if room_name == normalized_name:
                    lat = wpt.attrib.get('lat')
                    lon = wpt.attrib.get('lon')
                    return lat, lon

        return None

    except ET.ParseError as e:
        print(f"Error parsing the GPX file: {e}")
        return None
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
        return None

def generate_google_maps_link(lat, lon):
    base_url = "https://www.google.com/maps/dir/?api=1"
    destination = f"&destination={lat},{lon}"
    return base_url + destination

def generate_events_text(events, init_text):
    text = f"{init_text}\n\n"

    for event in events:
        timestamp: int = int(event.startTime.timestamp())
        coordinates = find_coordinates_in_gpx(event.room)
        if coordinates:
            lat, lon = coordinates
            link = generate_google_maps_link(lat, lon)
            text += f"{event.title} with {event.lecturer} at <t:{timestamp}:t> in [{event.room}]({link})\n"
        else:
            text += f"{event.title} with {event.lecturer} at <t:{timestamp}:t> in {event.room}\n"
            text += f"❌ Sorry room navigation failed for {event.room}\n"

    return text

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
            return await self.fetch_and_validate_calendar(url)
        except CalendarHTTPException as e:
            await self.send_dm(f"Could not load calendar from link: Got status code {e.code}.", dm_channel)
        except CalendarInvalidContent:
            await self.send_dm("Could not load calendar from link: Invalid content type.", dm_channel)
        except CalendarSizeException:
            await self.send_dm("Your calendar file is too big.", dm_channel)
        except CalendarRequestFailed:
            await self.send_dm("Could not load calendar from link: Request failed.", dm_channel)
        except CalendarInvalidLinkFormat:
            await self.send_dm("Invalid link format.", dm_channel)

    @staticmethod
    async def send_dm(error_text: str, ctx):
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(f"I've sent you a DM {ctx.author.mention}!")
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send(
                f"The following error occured when setting your calender: {error_text}\n" +
                "Please send your KUSSS calendar link like described bellow!.\n" +
                f"You can find it at: {config.links.kusss_cal_page}\n" +
                f"Send it using the following command: {config.prefix}setcalendar <link>"
            )

    @commands.command(name="setcalendar", description="Set your KUSSS calendar link")
    async def setcalendar(self, ctx):
        try:
            content = ctx.message.content.replace(f"{config.prefix}setcalendar", "").strip()
            calendar_data = await self.fetch_and_validate_calendar_dm_errors(content, ctx)

            if not calendar_data:
                ctx.send("Something went wrong. Please try again.")
                return
            session = self.bot.database.get_session()
            try:
                # Check if user already exists in DB
                user = session.query(User).get(str(ctx.author.id))

                # Create new user or update existing user
                if user is None:
                    user = User(
                        id=str(ctx.author.id),
                        calendar_link=content,
                        calendar_cache=calendar_data,
                        cached_at=datetime.now(timezone.utc)
                    )
                    session.add(user)
                else:
                    user.calendar_link = content
                    user.calendar_cache = calendar_data
                    user.cached_at = datetime.now(timezone.utc)
            finally:
                session.commit()
                session.close()

            await ctx.send("Your calendar link has been updated!")

        except discord.Forbidden:
            await ctx.send("I couldn't send you a DM.\nPlease check your privacy settings and try again.")

    async def getCalendarInfo(self, authorId):
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
                    content = await self.fetch_and_validate_calendar(user.calendar_link)
                    if content is not None:
                        user.calendar_cache = content
                        user.cached_at = datetime.now(timezone.utc)
                        session.commit()
                    elif user.calendar_cache is None or user.cached_at < datetime.now(timezone.utc).replace(
                            tzinfo=None) - timedelta(
                        hours=hoursToCacheError):
                        raise CalendarInvalid()
                    content = user.calendar_cache

        finally:
            session.close()
        return IcalStudentCalendar(content)

    @commands.command(name="calendarinfo", description="Get information about a specific day's calendar")
    async def getEventsForDay(self, ctx, *, date_input: str = None):
        try:
            calendar = await self.getCalendarInfo(ctx.author.id)
        except Exception:
            await ctx.send("Something is wrong with your calendar. Please set it again using setcalendar.")
            return

        #check if date is provided
        try:
            if date_input:
                event_date = datetime.strptime(date_input, "%d.%m.%Y").replace(tzinfo=timezone.utc)
            else:
                event_date = datetime.now(timezone.utc)
        except ValueError:
            await ctx.send("Invalid date format. Please use dd.mm.yyyy.")
            return

        events = calendar.getEventsForDay(event_date)

        if len(events) == 0:
            await ctx.send(f"You have no events on {event_date.strftime('%d.%m.%Y')}!")
            return

        await ctx.send(
            generate_events_text(events, f"Alright, here are your events for {event_date.strftime('%d.%m.%Y')}:"))

    @commands.command(name="testinfo", description="Get information on your upcoming tests")
    async def getTests(self, ctx):
        # try:
        calendar = await self.getCalendarInfo(ctx.author.id)
        # except Exception:
        # await ctx.send("Something is wrong with your calendar. Please set it again using setcalendar.")
        # return

        events = calendar.getNextTests(datetime.now(timezone.utc))
        # events = calendar.getEventsForDay(datetime(2025, 1, 8))

        if len(events) == 0:
            await ctx.send("You have no future tests in calendar!")
            return

        await ctx.send(generate_events_text(events, "Alright here are future Tests:"))

    @commands.command(name="where", description="Get navigation for a specific room")
    async def where(self, ctx, *, room_name: str):

        coordinates = find_coordinates_in_gpx(room_name)

        if coordinates:
            lat, lon = coordinates
            link = generate_google_maps_link(lat, lon)
            await ctx.send(f"Here's the navigation link for {room_name}: [{room_name}]({link})")
        else:
            await ctx.send(f"❌ Sorry room navigation failed for {room_name}\n")


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

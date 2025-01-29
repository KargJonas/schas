import re
from datetime import datetime, timezone, timedelta
from typing import Any, Coroutine

import discord
import requests
from discord.ext import commands

from calendarHelpers.IcalStudentCalendar import IcalStudentCalendar
from cogs.calendar import CalendarInvalidLinkFormat, CalendarHTTPException, CalendarSizeException, \
    CalendarInvalidContent, CalendarRequestFailed
from database.models import User
from util.load_json import load_json

from discord.ext import commands
from util.load_json import load_json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import cachetools.func

import xml.etree.ElementTree as ET


class GetOehEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Validates the KUSSS calendar URL and returns the calendar content if valid.
    # Returns None if invalid or unreachable.
    @cachetools.func.ttl_cache(maxsize=1, ttl=12 * 60 * 60)
    def fetchOehEventsCached(self) -> dict[str, str]:
        option = Options()
        option.headless = True
        option.add_experimental_option("prefs", {'safebrowsing.enabled': 'true'})
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        option.add_argument("--headless")
        driver = webdriver.Chrome(option)
        try:
            url = "https://oeh.jku.at/oeh-services/veranstaltungen"
            driver.get(url)
            elements = driver.find_elements(By.XPATH, "//article")
            events = {}
            for element in elements:
                # Get the first and second <div> elements within the article
                divs = element.find_elements(By.XPATH, "./div")
                if len(divs) >= 2:
                    first_div = divs[0]
                    second_div = divs[1]

                    # Example: Retrieve and print text or attributes from the <div> elements
                    first_div_content = first_div.text
                    second_div_content = second_div.text
                    second_div_content = second_div_content[:second_div_content.rfind("\n")]
                    events[first_div_content] = second_div_content
        finally:
            driver.quit()
        return events


    @commands.command(name="getOehEvents", description="Get information about a specific day's calendar")
    async def getOehEvents(self, ctx, *, date_input: str = None):
        events = self.fetchOehEventsCached()
        output = ""
        for k, v in events.items():
            output += "\n\📆 **" + k + "** "
            v = v.split("\n")
            output += "**" + v[0] + "**\n"
            output += "       Where: " + v[1] + "\n"
            output += "       When: " + v[2] + "\n"

        await ctx.send(output)

async def setup(bot):
    await bot.add_cog(GetOehEvents(bot))






















from discord.ext import commands
from util.load_json import load_json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import datetime

config = load_json("config.json")

hoursToCache = 3
hoursToCacheError = 24


class Food(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getmensafood", description="Get this weeks Mensa Menus")
    async def getmensafood(self, ctx):
        option = Options()
        option.headless = True
        option.add_experimental_option("prefs", {'safebrowsing.enabled': 'true'})
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        driver = webdriver.Chrome(option)

        url = "https://www.mensen.at/standort/mensa-jku/"

        days_list = []

        response = ""

        await ctx.send("Hold on, this might take a second...")

        try:
            driver.get(url)

            days = driver.find_elements(By.XPATH, "/html/body/div/div[2]/main/article/div/section[2]/div/div[2]/div[2]")

            for day in days[0].find_elements(By.XPATH, './*'):
                spans = day.find_elements(By.TAG_NAME, 'span')

                if len(spans) >= 2:
                    day_text = spans[1].text.strip()
                    days_list.append(day_text)

            for i in range(1, len(days_list) + 1):
                response += "------------\n\n"
                response += f"📆**{days_list[i - 1]}**\n"

                whole_selection = driver.find_element(By.XPATH,
                                                      f'/html/body/div/div[2]/main/article/div/section[2]/div/div[2]/div/div[{i}]')

                child_elements = whole_selection.find_elements(By.XPATH, './*')

                for index, element in enumerate(child_elements, start=1):
                    try:
                        menu_name = element.find_element(By.XPATH, './/h3').text
                        food_name = element.find_element(By.XPATH, './/ul/li/div/span[@class="font-bold"]').text
                        description = element.find_element(By.XPATH, './/ul/li/div/span[2]').text
                        price = element.find_element(By.XPATH,
                                                     './/div[@class="flex flex-col items-end justify-between flex-shrink-0 gap-1"]/span[@class="font-bold"]').text

                        response += f"**{menu_name}**\n"
                        response += f"{food_name}\n"
                        response += f"{description}\n"
                        response += f"{price}\n"
                        response += "\n"
                    except Exception:
                        continue

        finally:
            driver.quit()

        await ctx.send(response)

    @commands.command(name="getkhgfood", description="Get this week's KHG Mensa Menus")
    async def getkhgfood(self, ctx):
        option = Options()
        option.headless = True
        option.add_experimental_option("prefs", {'safebrowsing.enabled': 'true'})
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        driver = webdriver.Chrome(option)

        url = "https://www.dioezese-linz.at/khg/mensa/menueplan"
        driver.get(url)

        week_info = driver.find_element(By.CSS_SELECTOR, ".swslang strong span").text
        kw, _ = week_info.split("KW ")[1].split(" ", maxsplit=1)
        kw = int(kw)

        start_of_week = datetime.datetime.strptime(f"2025-W{kw - 1}-1", "%Y-W%U-%w")
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

        table_rows = driver.find_elements(By.CSS_SELECTOR, ".sweTable1 tr")
        current_day = None
        veggie = False

        response = ""

        for row in table_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 1:
                current_day = cells[0].text.strip()
                if current_day in days:
                    day_index = days.index(current_day)
                    date = start_of_week + datetime.timedelta(days=day_index)
                    response += "------------\n\n"
                    response += f"📆 {date.strftime('%d.%m.')}\n"
                    veggie = False
            elif len(cells) == 3 and current_day:
                meal = cells[0].text.strip()
                price_regular = cells[2].text.strip()
                if meal:
                    if not veggie:
                        response += f"Menü Veggie (mit Suppe und Salat)\n"
                        veggie = True
                    else:
                        response += f"Menü Herzhaft (mit Suppe und Salat)\n"

                    response += f"{meal}\n"
                    response += f"€ {price_regular}\n\n"

        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(Food(bot))
from discord.ext import commands
from util.load_json import load_json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import datetime
from datetime import datetime, timedelta

import time

config = load_json("config.json")

hoursToCache = 3
hoursToCacheError = 24


class Food(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getmensafood", description="Get this weeks Mensa Menus")
    async def getmensafood(self, ctx):

        await ctx.send("Hold on, this might take a second...")

        option = Options()
        option.headless = True
        option.add_experimental_option("prefs", {'safebrowsing.enabled': 'true'})
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        driver = webdriver.Chrome(option)

        url = "https://www.mensen.at/standort/mensa-jku/"

        days_list = []
        response = ""

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
                if len(days_list) > 1:
                    response += f"📆**{days_list[i - 1]}**\n\n"
                else:
                    today = datetime.today()
                    formatted_date = today.strftime("%d.%m")
                    response += f"📆**{formatted_date}**\n\n"

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

        try:
            url = "https://www.dioezese-linz.at/khg/mensa/menueplan"
            driver.get(url)

            week_info = driver.find_element(By.CSS_SELECTOR, ".swslang").text

            week_line = week_info.split(",")[0]
            week_number = int(week_line.split("KW")[1].strip())

            year = datetime.now().year
            start_of_week = datetime.strptime(f"{year}-W{week_number}-1", "%Y-W%U-%w")

            days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
            day_index_map = {day: i for i, day in enumerate(days)}

            table_rows = driver.find_elements(By.CSS_SELECTOR, ".sweTable1 tr")

            current_day = None
            response = ""
            vegi = True

            for row in table_rows:
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) == 1:
                    day_text = cells[0].text.strip()
                    if day_text in days:
                        current_day = day_text
                        day_index = day_index_map[current_day]
                        day_date = start_of_week + timedelta(days=day_index)
                        response += "------------\n\n"
                        response += f"**📆 {current_day}, {day_date.strftime('%d.%m.')}**\n\n"

                elif len(cells) == 3 and current_day:
                    dish = cells[0].text.strip()
                    if len(dish) > 0:
                        price = "€ 5,20"

                        if vegi:
                            response += "**Menü Veggie**\n"
                            vegi = False
                        else:
                            response += "**Menü Herzhaft**\n"
                            price = "€ 6,30"
                            vegi = True

                        response += f"{dish}\n"
                        response += f"{price}\n\n"

            await ctx.send(response)

        finally:
            driver.quit()

    @commands.command(name="getraabfood", description="Get this week's Raab Mensa Menus")
    async def getraabfood(self, ctx):

        await ctx.send("Hold on, this might take a second...")

        option = Options()
        option.headless = True
        option.add_experimental_option("prefs", {'safebrowsing.enabled': 'true'})
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        driver = webdriver.Chrome(option)

        url = "https://www.mittag.at/w/raabmensa"
        driver.get(url)

        dl_element = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/dl')

        driver.execute_script("arguments[0].scrollIntoView(true);", dl_element)
        time.sleep(1)

        days = dl_element.find_elements(By.TAG_NAME, 'dt')
        menus = dl_element.find_elements(By.TAG_NAME, 'dd')

        response = ""
        for i, (day, menu) in enumerate(zip(days, menus)):
            if i > 0:
                #website needs scrolling for content to load
                driver.execute_script("window.scrollBy(0, 50);")
                time.sleep(0.5)

            date = day.text.strip()
            menu_text = menu.get_attribute('innerHTML').replace('<br>', '\n').strip()
            menu_lines = [line.strip() for line in menu_text.split('\n') if line.strip()]

            response += f"------------\n\n\📆 **{date}**\n\n"

            if "MENÜ 1" in menu_lines and "MENÜ 2" in menu_lines:
                menu1_start = menu_lines.index("MENÜ 1") + 1
                menu2_start = menu_lines.index("MENÜ 2") + 1

                menu1_lines = menu_lines[menu1_start:menu2_start - 1]
                menu2_lines = menu_lines[menu2_start:]

                response += f"**Menü Herzhaft**\n{' '.join(menu1_lines)}\n\n"
                response += f"**Menü Veggie**\n{' '.join(menu2_lines)}\n\n"
            else:
                response += "No information for this day!\n\n"

        response += "------------"

        await ctx.send(response)

        driver.quit()

async def setup(bot):
    await bot.add_cog(Food(bot))
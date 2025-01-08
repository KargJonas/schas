from discord.ext import commands
from util.load_json import load_json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

config = load_json("config.json")

hoursToCache = 3
hoursToCacheError = 24


class Food(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getmensafood", description="Get Todays Mensa Menues")
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
                response += f"**{days_list[i - 1]}**\n"

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
                    except Exception as e:
                        continue

        finally:
            driver.quit()

        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(Food(bot))
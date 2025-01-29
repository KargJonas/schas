from discord.ext import commands
from util.load_json import load_json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class News(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getnews", description="Get the most recent JKU news")
    async def getnews(self, ctx, count: int = None):
        option = Options()
        option.headless = True
        option.add_experimental_option("prefs", {'safebrowsing.enabled': 'true'})
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        option.add_argument("--headless")
        driver = webdriver.Chrome(option)

        url = "https://www.jku.at/news-events/news/"
        news_items = []

        if count and count > 9:
            await ctx.send("Can't fetch more than 9 news items.")
            return
        
        if count and count < 1:
            await ctx.send("Please use a valid number.")
            return

        if not count:
            count = 3

        await ctx.send("Hold on, this might take a second...")

        try:
            driver.get(url)
            news_elements = driver.find_elements(By.CSS_SELECTOR, ".news_list_item")

            for entry in news_elements:
                datetime = entry.find_element(By.CSS_SELECTOR, "time").text
                title = entry.find_element(By.CSS_SELECTOR, 'h2.title span[itemprop="headline"]').text
                description = entry.find_element(By.CSS_SELECTOR, 'div[itemprop="description"] p').text
                link = "https://www.jku.at" + entry.find_element(By.CSS_SELECTOR, "div.moreon a").get_attribute("href")
                
                text = ""
                text += f"📆 {datetime}\n"
                text += f"**{title}**\n"
                text += f"{description}\n"
                text += f"Link: {link}\n"
                text += "------------"
                news_items.append(text)

        finally:
            driver.quit()

        news_items = news_items[0:count]
        news_items.reverse()

        for item in news_items:
            await ctx.send(item)

        await ctx.send("Use `!getnews <number>` to get more.")

async def setup(bot):
    await bot.add_cog(News(bot))
import discord

from discord.ext import commands
from util.load_json import load_json

config = load_json("config.json")

hoursToCache = 3
hoursToCacheError = 24


class Food(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getmensafood", description="Get Todays Mensa Menues")
    async def getmensafood(self, ctx):
        await ctx.send("Test")

async def setup(bot):
    await bot.add_cog(Food(bot))
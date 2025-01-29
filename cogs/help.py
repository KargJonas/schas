from discord.ext import commands
import discord


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h"], description="Get information on what the Bot can do")
    async def help(self, ctx):
        embed = discord.Embed(
            title="JKU Bot Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )

        calendar_commands = """
        `!setcalendar <link>` - Set your KUSSS calendar link
        `!calendarinfo [dd.mm.yyyy]` - Get your schedule for a specific day
        `!testinfo` - Get information about your upcoming tests
        `!where <room>` - Get navigation link to a specific room
        """
        embed.add_field(name="📅 Calendar Commands", value=calendar_commands, inline=False)

        food_commands = """
        `!getmensafood` - Get JKU Mensa menus for the week
        `!getkhgfood` - Get KHG Mensa menus for the week
        `!getraabfood` - Get Raab Mensa menus for the week
        """
        embed.add_field(name="🍽️ Food Commands", value=food_commands, inline=False)

        mensa_status_commands = """
                `!mensa_status [weekday]` - Get JKU Mensa occupancy. weekday = Monday, Tuesday, ...
                """
        embed.add_field(name="🍽️ Mensa Status Commands", value=mensa_status_commands, inline=False)

        news_commands = """
        `!getnews [number]` - Get recent JKU news (default: 3, max: 9)
        `!getevents [number]` - Get upcoming JKU events (default: 3, max: 9)
        """
        embed.add_field(name="📰 News & Events", value=news_commands, inline=False)

        help_command = """
        `!help` or `!h` - Display this help message
        """
        embed.add_field(name="❓ Help", value=help_command, inline=False)

        embed.set_footer(text="Optional parameters are shown in [brackets]. Required parameters are shown in <angular brackets>.")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))

async def setup(bot):
    await bot.add_cog(Help(bot))
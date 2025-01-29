import discord
from discord.ext import commands


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

        embed.add_field(name="Calendar Info", value="To use the bot in full capacity you must set up your calendar  with `!setcalendar`", inline=False)

        calendar_commands = """
        `!setCalendar <link>` - Set your KUSSS calendar link
        `!calendarInfo [dd.mm.yyyy]` - Get your schedule for a specific day
        `!testInfo` - Get information about your upcoming tests
        `!where <room>` - Get navigation link to a specific room
        """
        embed.add_field(name="📅 Calendar Commands", value=calendar_commands, inline=False)

        food_commands = """
        `!getMensaFood` - Get JKU Mensa menus for the week
        `!getKhgFood` - Get KHG Mensa menus for the week
        `!getRaabFood` - Get Raab Mensa menus for the week
        """
        embed.add_field(name="🍽️ Food Commands", value=food_commands, inline=False)

        mensa_status_commands = """
                `!mensaStatus [weekday]` - Get JKU Mensa occupancy. weekday = Monday, Tuesday, ...
                """
        embed.add_field(name="🍽️ Mensa Status Commands", value=mensa_status_commands, inline=False)

        news_commands = """
        `!getNews [number]` - Get recent JKU news (default: 3, max: 9)
        `!getEvents [number]` - Get upcoming JKU events (default: 3, max: 9)
        """
        embed.add_field(name="📰 News & Events", value=news_commands, inline=False)

        event_commands = """
                `!getOehEvents` - Get next ÖH events
                """
        embed.add_field(name="📰 ÖH Events", value=event_commands, inline=False)

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
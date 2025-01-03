from discord.ext import commands
from database.models import User

class Calendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setcalendar", description="Set your calendar link")
    async def setcalendar(self, ctx):
        await ctx.send("Please provide your calendar link:", ephemeral=True)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            session = self.bot.database.get_session()
            
            # Create or update user
            user = session.query(User).get(str(ctx.author.id))
            if user is None:
                user = User(
                    id=str(ctx.author.id),
                    calendar_link=msg.content
                )
                session.add(user)
            else:
                user.calendar_link = msg.content
            
            session.commit()
            session.close()
            
            await ctx.send("Calendar link has been saved!")
            
        except TimeoutError:
            await ctx.send("Time's up! Please try again.")

async def setup(bot):
    await bot.add_cog(Calendar(bot))

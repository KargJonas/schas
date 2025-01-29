from discord.ext import commands
import datetime


hours = [11, 12, 13, 14]
closing_times = [14.5, 14.5, 14.5, 14.5, 13.5, 0, 0]
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# occupancy data (11am-3pm, Monday-Friday)
# this was scraped from google maps
occupancy_data = [
    [0.714, 0.773, 0.724, 0.675, 0.339],  # 11:00
    [0.951, 1.000, 0.949, 0.842, 0.468],  # 12:00
    [0.675, 0.744, 0.773, 0.625, 0.339],  # 13:00
    [0.339, 0.418, 0.468, 0.339, 0.000],  # 14:00
]

class Mensa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # interpolate occupancy for any time between operating hours.
    # time_float should be in 24h format (e.g., 11.5 for 11:30)
    def interpolate_occupancy(self, day_idx, time_float):
        if time_float < 11.0 or time_float > 14.0:
            return None
            
        # get occupancy in the hours before/after the desired timestamp
        lower_hour_idx = int(time_float) - 11
        upper_hour_idx = min(lower_hour_idx + 1, 3)
        lower_occupancy = occupancy_data[lower_hour_idx][day_idx]
        upper_occupancy = occupancy_data[upper_hour_idx][day_idx]
                
        # use regular linear interpolation
        factor = time_float - int(time_float)
        interpolated = lower_occupancy + (upper_occupancy - lower_occupancy) * factor
        return interpolated

    def get_occupancy_percentage(self, day_idx, time_float=None):
        if time_float is None:
            # Get current time if no time provided
            current_time = datetime.datetime.now()
            time_float = current_time.hour + current_time.minute/60.0
            
        occupancy = self.interpolate_occupancy(day_idx, time_float)
        return int(occupancy * 100) if occupancy is not None else None

    def get_status_emoji(self, percentage):
        if percentage is None:
            return "❌"  # or some other appropriate indicator
        if percentage >= 80:
            return "🔴"
        elif percentage >= 50:
            return "🟡"
        else:
            return "🟢"

    def get_opening_hours_text(self, day_idx):
        if day_idx <= 3:  # monday - thursday
            return "Opening hours are 11:00-14:30"
        elif day_idx == 4:  # friday
            return "Opening hours are 11:00-13:30"
        else:  # Weekend
            return "Closed on weekends"

    @commands.command(
        name="mensaStatus",
        description="Get JKU Mensa occupancy. Use '!mensa_status' for current time or '!mensa_status Monday' for a specific day"
    )
    async def mensa_status(self, ctx, day: str = None):
        current_time = datetime.datetime.now()
        
        if day:
            day = day.capitalize()
            try:
                day_idx = days.index(day)
            except ValueError:
                await ctx.send("Invalid day! Please use Monday, Tuesday, Wednesday, Thursday, or Friday.")
                return
                
            response = f"📊 **Expected JKU Mensa Occupancy for {day}**\n"
            response += f"_{self.get_opening_hours_text(day_idx)}_\n\n"
            
            # full day forecast
            for hour in range(11, int(closing_times[day_idx])):
                for minute in [0, 30]:
                    time_float = hour + minute/60.0
                    if time_float >= closing_times[day_idx]:
                        continue
                    occupancy = self.get_occupancy_percentage(day_idx, time_float)
                    if occupancy is not None:
                        status = self.get_status_emoji(occupancy)
                        status_emoji = "🔴" if occupancy >= 80 else "🟡" if occupancy >= 50 else "🟢"
                        response += f"{status_emoji} {hour:02d}:{minute:02d} - {occupancy}% occupancy\n"
                        
            await ctx.send(response)
            return

        # handle current time request
        day_idx = current_time.weekday()
        
        # check if its weekend
        if day_idx >= 5:
            await ctx.send(f"❌ The Mensa is closed on weekends.")
            return

        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_float = current_hour + current_minute/60.0
        
        if current_time_float < 11 or current_time_float >= closing_times[day_idx]:
            await ctx.send(f"❌ The Mensa is currently closed. {self.get_opening_hours_text(day_idx)}.")
            return

        # get current occupancy using interpolation
        occupancy = self.get_occupancy_percentage(day_idx, current_time_float)
        status = self.get_status_emoji(occupancy)

        # generate response
        response = f"📊 **JKU Mensa Status**\n"
        response += f"**Current expected occupancy**: {status} {occupancy}% occupancy\n\n"  # Added percentage

        # add forecast for remaining time slots until closing
        response += "**Forecast:**\n"
        next_time = current_time_float
        while next_time < closing_times[day_idx]:
            next_time += 0.5  # Add 30 minutes
            if next_time >= closing_times[day_idx]:
                break
            next_occupancy = self.get_occupancy_percentage(day_idx, next_time)
            if next_occupancy is not None:
                next_status = self.get_status_emoji(next_occupancy)
                next_hour = int(next_time)
                next_minute = int((next_time - next_hour) * 60)
                response += f"{next_status} {next_hour:02d}:{next_minute:02d} - {next_occupancy}% occupancy\n"

        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(Mensa(bot))
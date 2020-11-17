import discord, asyncio, pickle
from discord.ext import commands
from Model import Server, Member, Advertisement

class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot : commands.Bot = bot
        self.hidden = True
def setup(bot):
    bot.add_cog(Fun(bot))
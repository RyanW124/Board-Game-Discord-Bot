from discord.ext import commands
from discord import Status, Game
import os, pickle, discord
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='.', help_command=None, intents=intents)





@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name='.help'), status=Status.online)
    for i in ['data', 'ads', 'mute', 'autorole']:
        try:
            with open(i+'.dat', 'rb'):
                pass
        except:
            with open(i+'.dat', 'wb') as f:
                pickle.dump([], f)
            print(f'Made new {i}.dat file')
    for i in ['boards', 'opposite']:
        try:
            with open(i+'.dat', 'rb'):
                pass
        except:
            with open(i+'.dat', 'wb') as f:
                pickle.dump({}, f)
            print(f'Made new {i}.dat file')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print('Finish loading '+ filename[:-3])
    print('Allement is ready')
@bot.command()
async def reload(ctx):
    for i in ['data', 'ads', 'mute', 'autorole']:
        try:
            os.remove(f'{i}.dat')
        except FileNotFoundError:
            pass
        with open(i + '.dat', 'wb') as f:
            pickle.dump([], f)
    for i in ['boards', 'opposite']:
        try:
            os.remove(f'{i}.dat')
        except FileNotFoundError:
            pass
        with open(i + '.dat', 'wb') as f:
            pickle.dump({}, f)
'''
@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed()
    embed.title = f'❌ Error'
    embed.color = discord.Color.red()
    
    if isinstance(error, commands.NoPrivateMessage):
        pass
    await ctx.send(embed=embed)
'''


bot.run('Nzc0OTExNTgxODYzNTQyODA0.X6eqpg.cq-By4oxryW225Tci0eO1JeRVhE')

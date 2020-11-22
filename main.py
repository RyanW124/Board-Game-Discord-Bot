from discord.ext import commands
from discord import Status, Game
import os, pickle, discord
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='.', help_command=None, case_insensitive=True, intents=intents)
#hi
@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name='.help'), status=Status.online)
    for i in ['data', 'ads', 'mute', 'autorole', 'users']:
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
async def del_all(ctx):
    ctx.guild: discord.Guild
    for i in ctx.guild.categories:
        i: discord.CategoryChannel
        if i.name.lower() not in ["text channels", 'voice channels']:
            for channel in i.channels:
                await channel.delete()
            await i.delete()
@bot.command()
async def reload(ctx):
    for i in ['data', 'ads', 'mute', 'autorole', 'users']:
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
    await ctx.send('Done')

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed()
    embed.title = f'❌ Error'
    embed.color = discord.Color.red()
    
    if isinstance(error, commands.NoPrivateMessage):
        embed.description = "This command could only be used in a server"
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.description = "Missing required argument"
    elif isinstance(error, commands.BotMissingPermissions):
        embed.description = "Bot is missing required permissions"
    elif isinstance(error, commands.MissingPermissions):
        embed.description = "You don't have the permissions to run the command"
    elif isinstance(error, commands.UserInputError):
        embed.description = "User input error"
    elif isinstance(error, commands.CheckFailure):
        embed.description = "This command could only be used by bot owner"
    else:
        raise error
    await ctx.send(embed=embed)


try:
    bot.run('Nzc0OTExNTgxODYzNTQyODA0.X6eqpg.cq-By4oxryW225Tci0eO1JeRVhE')
except:
    for i in ['data', 'ads', 'mute', 'autorole', 'users']:
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
    bot.run('Nzc0OTExNTgxODYzNTQyODA0.X6eqpg.cq-By4oxryW225Tci0eO1JeRVhE')

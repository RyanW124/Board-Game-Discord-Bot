import discord
from discord.ext import commands
import pickle
from Model import Server, Member


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_guild=True)
    async def mute(self, ctx: discord.Context, member: discord.Member, time : int):
        if member.top_role.position >= ctx.author.top_role.position:
            embed = discord.Embed()
            embed.title = '❌ Error: Can\'t mute member with higher or equal role to you'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        mute = None
        if server.mute:
            mute = ctx.guild.get_role(server.mute)
            if not mute:
                perms = discord.Permissions(send_messages=False, read_messages=True)
                mute = await ctx.guild.create_role(name='Muted', permissions=perms)
        else:
            perms = discord.Permissions(send_messages=False, read_messages=True)
            mute = await ctx.guild.create_role(name='Muted', permissions=perms)
        




    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason):
        if user not in await ctx.guild.bans():
            embed = discord.Embed()
            embed.title = f'❌ Error: {user.name} not banned from server'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        embed = discord.Embed()
        embed.title = f'✅ Success: Unbanned {user.name}'
        embed.description = f'Reason: {reason}'
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        await ctx.guild.unban(user, reason)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member.top_role.position >= ctx.author.top_role.position:
            embed = discord.Embed()
            embed.title = '❌ Error: Can\'t ban member with higher or equal role to you'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        try:
            await member.ban(reason=reason)
        except:
            embed = discord.Embed()
            embed.title = f'❌ Error: Bot doesn\'t have permissions to kick {member.name}'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        embed = discord.Embed()
        embed.title = f'✅ Success: Banned {member.name}'
        embed.description = f'Reason: {reason}'
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason = None):
        if member.top_role.position >= ctx.author.top_role.position:
            embed = discord.Embed()
            embed.title = '❌ Error: Can\'t kick member with higher or equal role to you'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        try:
            await member.kick(reason=reason)
        except:
            embed = discord.Embed()
            embed.title = f'❌ Error: Bot doesn\'t have permissions to kick {member.name}'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        embed = discord.Embed()
        embed.title = f'✅ Success: Kicked {member.name}'
        embed.description = f'Reason: {reason}'
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)


    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_permissions(manage_guild=True)
    async def warn(self, ctx, member:discord.Member, *, reason = None):
        if member.top_role.position>=ctx.author.top_role.position:
            embed = discord.Embed()
            embed.title = '❌ Error: Can\'t warn member with higher or equal role to you'
            embed.color = discord.Color.red()
            await ctx.send(embed = embed)
            return
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server = Server.search(ctx.guild.id, data)
        if not server:
            server = Server(ctx.guild.id)
            data.append(server)
        m = server.get_member(member.id)
        if not m:
            m = server.new_member(member.id)
        m.warns += 1
        if server.autokick:
            if m.warns>=server.autokick:
                embed = discord.Embed()
                embed.title = f'✅ Success: Warned {member.name} they now have {str(m.warns)} warning{"s" if m.warns > 1 else ""}'
                embed.description = f'Reason: {reason}'
                embed.set_footer(text = f'Autokicked {member.name}')
                embed.color = discord.Color.green()
                await ctx.send(embed=embed)
                dm = await member.create_dm()
                await dm.send(
                    f'You have been warned for {reason}\nYou now have {str(m.warns)} warning{"s" if m.warns > 1 else ""}')
                await dm.send(f'You have been kicked from {ctx.guild.name}')
                try:
                    await member.kick(reason = f'Autokick: Warnings exceeded {str(server.autokick)}')
                except:
                    embed = discord.Embed()
                    embed.title = f'❌ Error: Bot doesn\'t have permissions to kick {member.name}'
                    embed.color = discord.Color.red()
                    await ctx.send(embed=embed)
                with open('data.dat', 'wb') as f:
                    pickle.dump(data, f)
                return
        embed = discord.Embed()
        embed.title = f'✅ Success: Warned {member.name} they now have {str(m.warns)} warning{"s" if m.warns>1 else ""}'
        embed.description=f'Reason: {reason}'
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        dm = await member.create_dm()
        await dm.send(f'You have been warned for {reason}\nYou now have {str(m.warns)} warning{"s" if m.warns>1 else ""}')
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command(aliases=['gak'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def getautokick(self, ctx):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server = Server.search(ctx.guild.id, data)
        if not server:
            await ctx.send("This server does not have autokick yet, use *.setautokick* to set one")
            return
        if not server.autokick:
            await ctx.send("This server does not have autokick yet, use *.setautokick* to set one")
            return
        await ctx.send(f'This server\'s autokick is {str(server.autokick)}')

    @commands.command(aliases = ['sak'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setautokick(self, ctx, num : int = None):
        if num is int:
            if num == 1 or num <0:
                embed = discord.Embed()
                embed.title = f'❌ Error: num can\'t be negative nor equal to 1'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                return
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server = Server.search(ctx.guild.id, data)
        if not server:
            server = Server(ctx.guild.id)
            data.append(server)
        server.autokick = num if num!=0 else None
        embed = discord.Embed()
        if server.autokick:
            embed.title = f'✅ Success: Members would be automatically kicked when they get warned and their warnings exceed {str(num)}'
        else:
            embed.title = f'✅ Success: Disabled this server\'s autokick'
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def delwarn(self, ctx, member: discord.Member, num:int = None):
        async def error():
            embed = discord.Embed()
            embed.title = f'❌ Error: {member.name} does not have any warnings'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
        if num is int:
            if num<1:
                embed = discord.Embed()
                embed.title = f'❌ Error: num has to be greater than 0'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                return
        if member.top_role.position >= ctx.author.top_role.position:
            embed = discord.Embed()
            embed.title = '❌ Error: Can\'t delete warnings from member with higher or equal role to you'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return

        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server = Server.search(ctx.guild.id, data)
        if not server:
            await error()
            return
        m = server.get_member(member.id)
        if num is int:
            if num > m.warns:
                num = None

        if not m:
            await error()
            return
        m.warns -= num if num else m.warns
        embed = discord.Embed()
        embed.title = f'✅ Success: Deleted {str(num) if num else "all"} warning{"s" if num != 1 else ""} from {member.name} they now have {str(m.warns)} warning{"s" if m.warns != 1 else ""}'
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command()
    @commands.guild_only()
    async def getwarn(self, ctx, member: discord.Member):
        async def call(num):
            embed = discord.Embed()
            embed.title = f'{member.name} has {str(num)} warning{"s" if num != 1 else ""}'
            embed.color = discord.Color.blue()
            await ctx.send(embed=embed)
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server = Server.search(ctx.guild.id, data)
        if not server:
            await call(0)
            return
        m = server.get_member(member.id)

        if not m:
            await call(0)
            return
        await call(m.warns)



def setup(bot):
  bot.add_cog(Moderation(bot))
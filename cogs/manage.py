import discord, asyncio
from discord.ext import commands, tasks
import pickle
from Model import Server, Member, Mute, Autorole
from datetime import datetime
from copy import deepcopy
from Tools import senddm

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.hidden = False
    @commands.Cog.listener()
    async def on_ready(self):
        self.check_mute.start()

    @tasks.loop(seconds=15)
    async def check_mute(self):
        with open('mute.dat', 'rb') as f:
            mutes = pickle.load(f)
        todel=[]
        for i in mutes:
            if not i.time:
                continue

            if i.time<datetime.utcnow():
                try:
                    await self.bot.get_guild(i.guild).get_member(i.id).remove_roles(self.bot.get_guild(i.guild).get_role(i.mute), reason='Time\'s up')

                    todel.append(i)
                except Exception as f:
                    print(f)
        for i in todel:
            mutes.remove(i)
        with open('mute.dat', 'wb') as f:
            pickle.dump(mutes, f)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_guild=True)
    async def unmute(self, ctx: discord, member: discord.Member):
        with open('mute.dat', 'rb') as f:
            mutes = pickle.load(f)
        todel=[]
        for i in mutes:
            if i.id==member.id:
                x = i
                break
        else:
            embed = discord.Embed()
            embed.title = '❌ Error: Member is not muted'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        try:
            await self.bot.get_guild(x.guild).get_member(x.id).remove_roles(self.bot.get_guild(x.guild).get_role(x.mute),
                                                                            reason='Unmuted')
            mutes.remove(x)
            embed = discord.Embed()
            embed.title = f'✅ Success: Unmuted {member.name}'
            embed.set_footer(text=f'Unmuted by {ctx.author.name}')
            embed.color = discord.Color.green()
            await ctx.send(embed=embed)
            with open('mute.dat', 'wb') as f:
                pickle.dump(mutes, f)
        except:
            pass
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_guild=True)
    async def mute(self, ctx: discord, member: discord.Member, time : int = None):
        if time!=None and not 1<=time<=43200:
            embed = discord.Embed()
            embed.title = '❌ Error: Time has to be between 1 and 43200'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        if member.top_role.position >= ctx.author.top_role.position:
            embed = discord.Embed()
            embed.title = '❌ Error: Can\'t mute member with higher or equal role to you'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        with open('mute.dat', 'rb') as f:
            mutes = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        if not server:

            server = Server(ctx.guild.id)
            data.append(server)
        for i in mutes:
            if i.guild == ctx.guild.id and i.id == member.id:
                embed = discord.Embed()
                embed.title = f'❌ Error: {member.name} is already muted'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                return
        if server.mute:
            mute = ctx.guild.get_role(server.mute)
            if not mute:
                perms = discord.Permissions(send_messages=False, read_messages=True)
                mute = await ctx.guild.create_role(name='Muted', permissions=perms, reason="Do not delete")
                server.mute = mute.id
                for i in ctx.guild.text_channels:
                    perms = i.overwrites_for(mute)
                    perms.send_messages = False
                    await i.set_permissions(mute, overwrite=perms, reason="Muted!")
                try:
                    mute.position = ctx.guild.me.top_role.position - 1
                except:
                    pass
        else:
            perms = discord.Permissions(send_messages=False, read_messages=True)
            mute = await ctx.guild.create_role(name='Muted', permissions=perms, reason="Do not delete")
            server.mute = mute.id
            for i in ctx.guild.text_channels:
                perms = i.overwrites_for(mute)
                perms.send_messages = False
                await i.set_permissions(mute, overwrite=perms, reason="Muted!")
            try:
                mute.position = ctx.guild.me.top_role.position - 1
            except:
                pass

        try:
            await member.add_roles(mute, reason=f'Muted by {ctx.author.name}')
        except:
            embed = discord.Embed()
            embed.title = f'❌ Error: Bot doesn\'t have permissions to edit roles for {member.name}'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        mutes.append(Mute(member.id, time, mute.id, ctx.guild.id))
        embed = discord.Embed()
        embed.title = f'✅ Success: Muted {member.name}'
        embed.set_footer(text=f'Muted by {ctx.author.name}')
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        with open('mute.dat', 'wb') as f:
            pickle.dump(mutes, f)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)



    @commands.group(name='autorole')
    async def autorole(self, ctx):
        pass

    @tasks.loop(seconds=5)
    async def check_reactions(self):
        with open('autorole.dat', 'rb') as f:
            data = pickle.load(f)
        for i in data:
            try:
                channel: discord.TextChannel = self.bot.get_channel(i.ch_id)

                if channel:
                    msg: discord.Message = await channel.fetch_message(i.id)

                    if msg:
                        for r in msg.reactions:
                            if r.emoji in i.roles:
                                try:
                                    role: discord.Role = channel.guild.get_role(i.roles[r.emoji])
                                except:
                                    continue
                                if role:
                                    async for user in r.users():
                                        member: discord.Member = channel.guild.get_member(user.id)
                                        if not user.bot:
                                            if role in member.roles:
                                                await member.remove_roles(role, reason='Autorole')
                                                await senddm(user, f"Removed {role.name} from your roles")

                                            else:
                                                await member.add_roles(role, reason='Autorole')
                                                await senddm(user, f"Added {role.name} to your roles")
                                            await r.remove(user)
            except:
                pass
    @autorole.command(name='new')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_guild=True)
    async def autorole_new(self, ctx):
        with open('autorole.dat', 'rb') as f:
            data = pickle.load(f)
        roles = {}
        final_embed = discord.Embed(title="React to get roles")
        final_embed.set_footer(text='Not finished')
        final_message: discord.Message = await ctx.send(embed=final_embed)
        for num in range(30):
            await ctx.send(f"You have 30 seconds to mention the role{'' if num==0 else ' or type done to finish'}.")
            try:
                def check(message):
                    return message.author == ctx.author

                message = await self.bot.wait_for('message', timeout=30.0, check=check)

            except asyncio.TimeoutError:
                embed = discord.Embed()
                embed.title = '❌ Error: Took too long to respond. Please redo command'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                await final_message.delete()
                return
            if num != 0 and message.content.lower() == 'done':
                final_embed.set_footer(text="")
                break
            for i in ctx.guild.roles:
                if i.mention == message.content:
                    role: discord.Role = i
                    break
            else:
                embed = discord.Embed()
                embed.title = f'❌ Error: {message.content} is not a valid role mention'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                await final_message.delete()
                return
            await ctx.send(f"You have 30 seconds to type an emoji for {role.name}")
            try:
                def check(message):
                    return message.author == ctx.author

                message = await self.bot.wait_for('message', timeout=30.0, check=check)

            except asyncio.TimeoutError:
                embed = discord.Embed()
                embed.title = '❌ Error: Took too long to respond. Please redo command'
                embed.color = discord.Color.red()
                await final_message.delete()
                await ctx.send(embed=embed)
                return
            try:
                await final_message.add_reaction(message.content[0])
            except:
                embed = discord.Embed()
                embed.title = '❌ Error: Invalid emoji. Please redo command'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                await final_message.delete()
                return
            roles[message.content[0]] = role.id
            final_embed.add_field(name=f'{message.content[0]}: {role.name}', value='** **')
            await final_message.edit(embed=final_embed)
        else:
            embed = discord.Embed()
            embed.title = 'You may only have up to 30 roles'
            embed.color = discord.Color.blue()
            await ctx.send(embed=embed)
            final_embed.set_footer(text="")
        await final_message.edit(embed=final_embed)
        data.append(Autorole(final_message.id, ctx.channel.id, roles))
        with open('autorole.dat', 'wb') as f:
            pickle.dump(data, f)
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
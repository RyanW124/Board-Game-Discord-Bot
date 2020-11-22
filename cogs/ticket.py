import discord, asyncio, pickle
from discord.ext import commands, tasks
from Model import Server, Member, Advertisement, Ticket
from Tools import senddm

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot : commands.Bot = bot
        self.hidden = False
        self.check_reactions.start()



    @commands.command()
    @commands.guild_only()
    async def staffs(self, ctx: commands.Context):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        if not server:
            server = Server(ctx.guild.id)
            data.append(server)
        embed = discord.Embed()
        embed.title = f'Staffs'
        if server.ticket_staffs:
            for i in server.ticket_staffs:
                role = ctx.guild.get_role(i)
                if role:
                    embed.add_field(name=role.name, value=role.mention, inline=False)

        else:
            embed.description = 'This server does not have any roles yet'
        embed.color = discord.Color.blue()
        await ctx.send(embed=embed)

    @commands.command(aliases=['tr'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(send_messages=True, add_reactions=True)
    async def ticket_react(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        if not server:
            server = Server(ctx.guild.id)
            data.append(server)
        if not channel:
            channel = ctx.channel
        embed = discord.Embed()
        embed.title = f'Tickets'
        embed.color = discord.Color.blue()
        embed.description = 'React to 📩 to create a ticket'
        msg = await channel.send(embed=embed)
        await msg.add_reaction('📩')
        server.ticket_react = (ctx.channel.id, msg.id)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)

    @tasks.loop(seconds=5)
    async def check_reactions(self):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        for i in data:
            if i.ticket_react:
                channel: discord.TextChannel = self.bot.get_channel(i.ticket_react[0])
                if channel:
                    msg: discord.Message = await channel.fetch_message(i.ticket_react[1])
                    if msg:
                        for r in msg.reactions:
                            if r.emoji == '📩':
                                async for users in r.users():
                                    if not users.bot:
                                            await r.remove(users)
                                            server = channel.guild
                                            for s in server.categories:
                                                if s.id == i.ticket_category:
                                                    c = await s.create_text_channel(f'{users.name}\'s ticket')
                                                    embed = discord.Embed(color=discord.Color.blue())
                                                    embed.title = users.name
                                                    embed.set_image(url=users.avatar_url)
                                                    if i.ticket_msg:
                                                        embed.description = i.ticket_msg
                                                    await c.send(embed=embed)
                                                    mentions = ''
                                                    for tag in i.ticket_staffs:
                                                        staff = server.get_role(tag)
                                                        if staff:
                                                            mentions += staff.mention + ' '
                                                    await c.send(mentions)
                                                    i.new_ticket(users.id, c.id)
                                                    # embed = discord.Embed()
                                                    # embed.title = f'✅ Success: Created ticket at {c.mention}'
                                                    # embed.set_footer(text=server.name)
                                                    # embed.color = discord.Color.green()
                                                    # await ctx.send(embed=embed)
                                                    # break
                                            else:

                                                cat: discord.CategoryChannel = await server.create_category(
                                                    'Tickets', reason='Category for tickets')
                                                i.ticket_category = cat.id
                                                perms = cat.overwrites_for(server.me)
                                                perms.view_channel = True
                                                await cat.set_permissions(server.me, overwrite=perms)
                                                perms = cat.overwrites_for(server.default_role)
                                                perms.view_channel = False
                                                await cat.set_permissions(server.default_role, overwrite=perms)
                                                for x in i.ticket_staffs:
                                                    staff = server.get_role(x)
                                                    if staff:
                                                        perms = cat.overwrites_for(staff)
                                                        perms.view_channel = True
                                                        await cat.set_permissions(staff, overwrite=perms,
                                                                                  reason="Staff")
                                                await senddm(users, discord.Embed(title="You opened a ticket", color=discord.Color.green()), True)
                                                c = await cat.create_text_channel(f'{users.name}\'s ticket')
                                                embed = discord.Embed(color=discord.Color.blue())
                                                embed.title = users.name
                                                embed.set_image(url=users.avatar_url)
                                                if i.ticket_msg:
                                                    embed.description = i.ticket_msg
                                                await c.send(embed=embed)
                                                mentions = ''
                                                for tag in i.ticket_staffs:
                                                    staff = server.get_role(tag)
                                                    if staff:
                                                        mentions += staff.mention + ' '
                                                if mentions != '':
                                                    await c.send(mentions)
                                                i.new_ticket(users.id, c.id)
                                                # embed = discord.Embed()
                                                # embed.title = f'✅ Success: Created ticket at {c.mention}'
                                                # embed.set_footer(text=ctx.author.name)
                                                # embed.color = discord.Color.green()
                                                # await ctx.send(embed=embed)
                                            with open('data.dat', 'wb') as f:
                                                pickle.dump(data, f)
                                        # except Exception as e:
                                        #     print(f)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command(aliases=['rs'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def remove_staffs(self, ctx: commands.Context, *roles: discord.Role):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        if not server:
            server = Server(ctx.guild.id)
            data.append(server)
        text = ''
        if server.ticket_category:
            for i in ctx.guild.categories:
                if i.id == server.ticket_category:
                    category = i
                    break
            else:
                category = None
        for i in roles:
            if i.id in server.ticket_staffs:
                if i.id not in server.ticket_staffs:
                    if category:
                        perms = category.overwrites_for(i)
                        perms.view_channel = False
                        await category.set_permissions(i, overwrite=perms, reason="Staff")
                server.ticket_staffs.remove(i.id)
            text += i.mention + ', '
        if text != '':
            text = text[:-2]
        embed = discord.Embed()
        embed.title = f'✅ Success: Removed {text} from staffs'
        embed.set_footer(text=ctx.author.name)
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command(aliases=['ss'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def add_staffs(self, ctx: commands.Context, *roles: discord.Role):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        if not server:
            server = Server(ctx.guild.id)
            data.append(server)
        text = ''
        category = None
        if server.ticket_category:
            for i in ctx.guild.categories:
                if i.id == server.ticket_category:
                    category = i
                    break
            else:
                category = None

        for i in roles:
            if i.id not in server.ticket_staffs:
                if category:
                    perms = category.overwrites_for(i)
                    perms.view_channel = True
                    await category.set_permissions(i, overwrite=perms, reason="Staff")
                server.ticket_staffs.append(i.id)
            text += i.mention + ', '
        if text != '':
            text = text[:-2]
        embed = discord.Embed()
        embed.title = f'✅ Success: Added {text} to staffs'
        embed.set_footer(text=ctx.author.name)
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)


    @commands.command(aliases=['ct'])
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_guild=True)
    async def close_ticket(self, ctx: commands.Context):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        if not server:

            server = Server(ctx.guild.id)
            data.append(server)
        for i in server.tickets:
            if i.ch_id == ctx.channel.id:
                embed = discord.Embed()
                embed.title = f'✅ Success: Ticket Closing in 5 seconds.'
                embed.set_footer(text=ctx.author.name)
                embed.color = discord.Color.green()
                await ctx.send(embed=embed)
                break
        else:
            embed = discord.Embed()
            embed.title = f'❌ Error: Command could only be used in a ticket'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        asyncio.sleep(5)
        await ctx.channel.delete(reason=f'Ticket closed by {ctx.author.id}')

    @commands.command(aliases=['nt'])
    @commands.guild_only()
    @commands.cooldown(1, 30)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_guild=True)
    async def new_ticket(self, ctx: commands.Context):
        with open('data.dat', 'rb') as f:
            data = pickle.load(f)
        server: Server = Server.search(ctx.guild.id, data)
        if not server:

            server = Server(ctx.guild.id)
            data.append(server)

        for i in ctx.guild.categories:
            if i.id == server.ticket_category:
                c = await i.create_text_channel(f'{ctx.author.name}\'s ticket')
                embed = discord.Embed(color=discord.Color.blue())
                embed.title = ctx.author.name
                embed.set_image(url=ctx.author.avatar_url)
                if server.ticket_msg:
                    embed.description = server.ticket_msg
                await c.send(embed=embed)
                mentions = ''
                for tag in server.ticket_staffs:
                    staff = ctx.guild.get_role(tag)
                    if staff:
                        mentions += staff.mention + ' '
                if mentions != '':
                    await c.send(mentions)
                server.new_ticket(ctx.author.id, c.id)
                embed = discord.Embed()
                embed.title = f'✅ Success: Created ticket at {c.mention}'
                embed.set_footer(text=ctx.author.name)
                embed.color = discord.Color.green()
                await ctx.send(embed=embed)
                break
        else:

            cat:discord.CategoryChannel = await ctx.guild.create_category('Tickets', reason='Category for tickets')
            server.ticket_category = cat.id
            perms = cat.overwrites_for(ctx.guild.me)
            perms.view_channel = True
            await cat.set_permissions(ctx.guild.me, overwrite=perms)
            perms = cat.overwrites_for(ctx.guild.default_role)
            perms.view_channel = False
            await cat.set_permissions(ctx.guild.default_role, overwrite=perms)
            for i in server.ticket_staffs:
                staff = ctx.guild.get_role(i)
                if staff:
                    perms = cat.overwrites_for(staff)
                    perms.view_channel = True
                    await cat.set_permissions(staff, overwrite=perms, reason="Staff")
            c = await cat.create_text_channel(f'{ctx.author.name}\'s ticket')
            embed = discord.Embed(color=discord.Color.blue())
            embed.title = ctx.author.name
            embed.set_image(url=ctx.author.avatar_url)
            if server.ticket_msg:
                embed.description = server.ticket_msg
            await c.send(embed=embed)
            mentions = ''
            for tag in server.ticket_staffs:
                staff = ctx.guild.get_role(tag)
                if staff:
                    mentions += staff.mention + ' '
            await c.send(mentions)
            server.new_ticket(ctx.author.id, c.id)
            embed = discord.Embed()
            embed.title = f'✅ Success: Created ticket at {c.mention}'
            embed.set_footer(text=ctx.author.name)
            embed.color = discord.Color.green()
            await ctx.send(embed=embed)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)
        # except Exception as e:
        #     print(f)
        with open('data.dat', 'wb') as f:
            pickle.dump(data, f)


def setup(bot):
    bot.add_cog(Tickets(bot))
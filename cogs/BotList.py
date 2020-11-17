import discord, asyncio, pickle
from discord.ext import commands
from Model import Server, Member, Advertisement
from copy import deepcopy
from Tools import senddm

class ServerList(commands.Cog):

    def __init__(self, bot):
        self.bot : commands.Bot = bot
        self.hidden = False
        self.staff_list = []
    async def is_staff(ctx):
        return ctx.author.id in []

    @commands.command()
    @commands.check(is_staff)
    async def delete(self, ctx, guild_id, *, reason):
        """Hide"""
        with open('ads.dat', 'rb') as f:
            data = pickle.load(f)
        for i in deepcopy(data):
            if i.id == guild_id:
                data.remove(i)
                guild = await self.bot.get_guild(i.id)
                if guild:
                    embed = discord.Embed()
                    embed.title = 'Your advertisement have been taken down'
                    embed.description = f'Reason: {reason}'
                    embed.color = discord.Color.red()
                    senddm(guild.owner, embed, True)
                await ctx.send('Done')
                break
        with open('ads.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command()
    @commands.is_owner()
    async def new(self, ctx):
        await ctx.send("You have 30 seconds to type out the description (Maximum 300 characters")
        try:
            def check(message):
                return message.author == ctx.author

            message = await self.bot.wait_for('message', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.title = '❌ Error: Took too long to respond. Please redo command'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        if len(message.content) > 300:
            embed = discord.Embed()
            embed.title = f'❌ Error: Description cannot exceed 300 characters (You have {str(len(message.content))} characters). Please redo command'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        description = message.content
        embed = discord.Embed(title="You have 30 seconds to choose the color")
        colors = {'♥️': (discord.Color.red(), 'Red'), '💚': (discord.Color.green(), 'Green'),
                  '💛': (discord.Color.from_rgb(255, 255, 0), 'Yellow'),
                  '💙': (discord.Color.blue(), 'Blue'), '💜': (discord.Color.purple(), 'Purple'),
                  '🧡': (discord.Color.orange(), 'Orange')}
        for e in colors:
            embed.add_field(name=f'{e}: {colors[e][1]}', value='**\n**', inline=False)
        choose_color_message: discord.Message = await ctx.send(embed=embed)
        [await choose_color_message.add_reaction(e) for e in colors]
        try:
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == choose_color_message.id and reaction.emoji in colors

            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.title = '❌ Error: Took too long to respond. Please redo command'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        color = colors[reaction.emoji]

        await ctx.send("You have 30 seconds to mention out the channel to be invited to.")
        try:
            def check(message):
                return message.author == ctx.author

            message = await self.bot.wait_for('message', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.title = '❌ Error: Took too long to respond. Please redo command'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        for i in ctx.guild.text_channels:
            if i.mention == message.content:
                channel: discord.TextChannel = i
                break
        else:
            embed = discord.Embed()
            embed.title = f'❌ Error: {message.content} is not a valid channel mention'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return

        with open('ads.dat', 'rb') as f:
            data = pickle.load(f)
        invite = await channel.create_invite(reason='Server List Invite', unique=True)
        for i in deepcopy(data):
            if i.id == ctx.guild.id:
                data.remove(i)
        ad = Advertisement(ctx.guild.id, description, invite.url, color[0])
        data.append(ad)
        await ctx.send("Here's the sample page of the advertisement")
        embed = discord.Embed()
        embed.title = self.bot.get_guild(ctx.guild.id).name if self.bot.get_guild(ctx.guild.id) else str(ctx.guild.id)
        embed.description = description
        embed.color = color[0]
        embed.add_field(name='Invite: ', value=invite.url, inline=False)
        embed.add_field(name='Member Count: ',value=str(len(ctx.guild.members)), inline=False)
        if ctx.guild:
            if ctx.guild.icon_url:
                embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)
        with open('ads.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command(aliases=['rm'])
    @commands.is_owner()
    async def remove(self, ctx):
        with open('ads.dat', 'rb') as f:
            data = pickle.load(f)
        for i in deepcopy(data):
            if i.id == ctx.guild.id:
                data.remove(i)
                break
        else:
            embed = discord.Embed()
            embed.title = f'❌ Error: No advertisements found for this server'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        embed = discord.Embed()
        embed.title = f'✅ Success: Deleted advertisement'
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)
        with open('ads.dat', 'wb') as f:
            pickle.dump(data, f)

    @commands.command(aliases=['list'])
    async def all(self, ctx, page_num : int = 1):
        n=10
        with open('ads.dat', 'rb') as f:
            data = pickle.load(f)

        if not 1 <= page_num <= ((len(data)//n)+1 if (len(data)/n) % 1 != 0 else len(data)//n):
            embed = discord.Embed()
            embed.title = f'❌ Error: Page {str(page_num)} does not exist'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        embed = discord.Embed()
        embed.title = f'All Server Lists'
        num = 0
        for i in data[page_num*n-n:]:
            embed.add_field(name=str(page_num*n-n+1+num)+'. '+self.bot.get_guild(i.id).name if self.bot.get_guild(i.id) else str(i.id),
                            value=i.description+'\n', inline=False)
            num += 1
            if num==n:
                break
        embed.color = discord.Color.blue()
        embed.set_footer(text=f'Page {str(page_num)} of {str((len(data)//n)+1 if (len(data)/n) % 1 != 0 else len(data)//n)}')
        await ctx.send(embed=embed)

    @commands.command()
    async def server(self, ctx, server_num : int):
        with open('ads.dat', 'rb') as f:
            data = pickle.load(f)
        if not 1 <= server_num <= len(data):
            embed = discord.Embed()
            embed.title = f'❌ Error: Server {str(server_num)} does not exist'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        server = data[server_num-1]
        embed = discord.Embed()
        embed.title = self.bot.get_guild(ctx.guild.id).name if self.bot.get_guild(ctx.guild.id) else str(ctx.guild.id)
        embed.description = server.description
        embed.color = server.color
        embed.add_field(name='Invite: ', value=server.invite, inline=False)
        embed.add_field(name='Member Count: ', value=str(len(self.bot.get_guild(ctx.guild.id).members)) if self.bot.get_guild(ctx.guild.id) else 'N/A', inline=False)
        if self.bot.get_guild(ctx.guild.id):
            if self.bot.get_guild(ctx.guild.id).icon_url:
                embed.set_thumbnail(url=self.bot.get_guild(ctx.guild.id).icon_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ServerList(bot))
from discord.ext import commands
import discord
import pickle


class Others(commands.Cog):
    """Utilities"""

    def __init__(self, bot):
        self.hidden = False
        self.bot = bot


    @commands.command(aliases = ['report'])
    async def suggest(self, ctx, *, suggestion):
        """Suggest anything or report bugs with this command"""
        me = self.bot.get_user(702017044824064022)
        channel = await me.create_dm()
        await channel.send(f"{ctx.author.name}'s suggestion:\n\n{suggestion}")

    @commands.command()
    async def help(self, ctx, *cog):
        """Displays the help command
        Anything in angled brackets <> is a required argument. Square brackets [] mark an optional argument"""
        prefix = "."
        if not cog:
            embed = discord.Embed(title="Help", description=f"use `{prefix}help [category|command]` for more info",
                                  color=0x00FF00)
            embed.set_footer(text=f"Created by ||J||||e||||f||||f|| is me#4587")
            cog_desc = ''
            for x in self.bot.cogs:
                if not self.bot.cogs[x].hidden:
                    cmd = ''
                    cog_desc += f"__**{x}**__: {self.bot.cogs[x].__doc__}\n"
                    for y in self.bot.get_cog(x).get_commands():
                        cmd += f"`{prefix}{y}`,  "
                    cmd = cmd [:-3]
                    embed.add_field(name=f"\n__**{x}**__: {self.bot.cogs[x].__doc__}", value=cmd, inline=False)
            embed.add_field(name="Links:",
                            value="[Invite the bot](https://discord.com/api/oauth2/authorize?client_id=774911581863542804&permissions=1945370487&scope=bot) | [Bot Shop Server](https://discord.gg/FgcSSbV)",
                            inline=False)
            await ctx.send(embed=embed)
        else:
            if len(cog) > 1:
                await ctx.send("That is not a valid category")
            else:
                found = False
                for x in self.bot.cogs:
                    for y in cog:
                        if x == y:
                            # title="Help", description=f"**Category {cog[0]}:** {self.bot.cogs[cog[0]].__doc__}",
                            embed = discord.Embed(title="Help", color=0x00FF00)
                            scog_info = ''
                            for c in self.bot.get_cog(y).get_commands():
                                if not c.hidden:
                                    scog_info += f"\n**`{c.name}`**: {c.help}\n"
                            embed.add_field(name=f"\n{cog[0]} Category:\n{self.bot.cogs[cog[0]].__doc__}\n ",
                                            value=f"\n{scog_info}\n", inline=False)
                            found = True

            if not found:
                for x in self.bot.cogs:
                    for c in self.bot.get_cog(x).get_commands():
                        if c.name == cog[0]:
                            embed = discord.Embed(color=0x00FF00)
                            if len(c.aliases) == 0:
                                embed.add_field(name=f"{c.name}: {c.help}",
                                                value=f"Usage:\n `{prefix}{c.qualified_name} {c.signature}`")
                            else:
                                embed.add_field(name=f"{c.name}: {c.help}",
                                                value=f"Usage:\n `{prefix}{c.qualified_name} {c.signature}`\nAliases:\n `{c.aliases}`")
                            found = True
            if not found:
                embed = discord.Embed(
                    description="Command not found. Check that you have spelt it correctly and used capitals where appropriate")
            await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(title=None,
                              description='[Invite the bot](https://discord.com/api/oauth2/authorize?client_id=774911581863542804&permissions=1945370487&scope=bot) | [Bot Shop Server](https://discord.gg/FgcSSbV)',
                              color=0x0000FF)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Others(bot))
import discord, asyncio, pickle
from discord.ext import commands, tasks
from string import ascii_uppercase as caps
from Model import Server, Member, Advertisement, Poll


class Polls(commands.Cog):

    def __init__(self, bot):
        self.bot : commands.Bot = bot
        self.hidden = True
    @tasks.loop(seconds=5)
    async def check_polls(self):
        with open('polls.dat', 'rb') as f:
            data = pickle.load(f)
        for poll in data:
            poll: Poll
            channel: discord.TextChannel = self.bot.get_channel(poll.ch_id)
            if channel:
                message = await channel.fetch_message(poll.id)
                if message:
                    alphabets = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰',
                    '🇱', '🇲', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
                    for reaction in message.reactions:
                        if reaction.emoji in alphabets[:len(poll.answers)]:
                            for user in reaction.users():
                                if not user.bot:
                                    if user.id in poll.answers[alphabets[alphabets.index(reaction.emoji)]]:
                                        poll.answers[alphabets[alphabets.index(reaction.emoji)]].remove(user.id)
                                    else:
                                        poll.answers[alphabets[alphabets.index(reaction.emoji)]].append(user.id)
                                    await reaction.remove(user)

    @commands.command('np')
    @commands.guild_only()
    async def new_poll(self, ctx: commands.Context):

        await ctx.send("You have 30 seconds to type the question of the poll. (Maximum 300 characters)")

        try:
            def check(message):
                return message.author == ctx.author

            question = await self.bot.wait_for('message', timeout=30.0, check=check).content

        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.title = '❌ Error: Took too long to respond. Please redo command'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        if len(question) < 300:
            embed = discord.Embed()
            embed.title = '❌ Error: Too much characters, cannot exceed 300. Please redo command'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        choices = []
        for i in caps:
            await ctx.send(f"You have 30 seconds to type choice {i} (Maximum 300 characters). Or type *done* to finish.")
            try:
                def check(message):
                    return message.author == ctx.author

                choice = await self.bot.wait_for('message', timeout=30.0, check=check).content

            except asyncio.TimeoutError:
                embed = discord.Embed()
                embed.title = '❌ Error: Took too long to respond. Please redo command'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                return

            if len(choice) < 300:
                embed = discord.Embed()
                embed.title = '❌ Error: Too much characters, cannot exceed 300. Please redo command'
                embed.color = discord.Color.red()
                await ctx.send(embed=embed)
                return
            choices.append(choice)

        await ctx.send(f"You have 30 seconds to type the number of times a user can vote (has to be an integer between 1 and {str(len(choices))})")
        try:
            def check(message):
                return message.author == ctx.author

            num = await self.bot.wait_for('message', timeout=30.0, check=check).content

        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.title = '❌ Error: Took too long to respond. Please redo command'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        try:
            num = int(num)
        except:
            embed = discord.Embed()
            embed.title = '❌ Error: Not a valid integer'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        if not 1<=num<=len(choices):
            embed = discord.Embed()
            embed.title = f'❌ Error: Number of votes has to be an integer between 1 and {str(len(choices))}'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        with open('polls.dat', 'rb') as f:
            data = pickle.load(f)
        ch_dict = {i: [] for i in choices}
        embed = discord.Embed(title='Poll', description=f'{question}\n')
        for i in range(len(choices)):
            embed.add_field(name=f'{caps[i]}. {choices[i]}', value='**\n**', inline=False)
        embed.set_footer(text=f"Poll by {ctx.author.name}")
        msg = await ctx.send(embed=embed)
        for i in range(len(choices)):
            await msg.add_reaction('')
        data.append(Poll(msg.id, ctx.channel.id, question, ch_dict, num))
        with open('polls.dat', 'wb') as f:
            pickle.dump(data, f)
def setup(bot):
    bot.add_cog(Polls(bot))
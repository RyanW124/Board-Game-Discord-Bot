import Gomoku as g
import chess
import reversi as r
import connect4 as c4
import discord
from string import ascii_lowercase as alphabet
from Tools import senddm
from discord.ext import commands
import pickle, asyncio, os
from PIL import Image, ImageDraw, ImageFont
from random import shuffle

class BoardGames(commands.Cog):
    """Play gomoku with your friends"""
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

    @commands.group()
    async def Chess(self, ctx):
        pass

    @Chess.command(name='show')
    async def chess_show_cmd(self, ctx):
        with open("boards.dat", "rb") as f:
            data = pickle.load(f)

        if ctx.author.id in data:
            if not type(data[ctx.author.id]) == chess.Board:
                await ctx.send("You don't have a chess game in progress.")
                return
            if data[ctx.author.id].turn:
                await ctx.send("White to move...")
            else:

                await ctx.send("Black to move...")
            await self.chess_show(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
        else:
            await ctx.send("You don't have a game in progress.")

    async def chess_show(self, p : discord.Member, ch : discord.TextChannel, board, id):
        w, h = (790, 790)
        img = Image.new("RGB", (w, h))
        img1 = ImageDraw.Draw(img)
        alp = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i in range(9):
            if i != 8:
                img1.text((i * 90 + 95, 735), alp[i], font=ImageFont.truetype('Arial.ttf', 20))
                img1.text((20, i * 90 + 50), str(9 - (i + 1)), font=ImageFont.truetype('Arial.ttf', 20))

            img1.line([(60, i * 90 + 10), (780, i * 90 + 10)], fill=None, width=0)
            img1.line([(i * 90 + 60, 10), (i * 90 + 60, 730)], fill=None, width=0)

        for i in range(64):
            c = 7 - i // 8
            r = i % 8
            if board.piece_type_at(i):

                if board.piece_at(i).color:
                    t = "white"
                else:
                    t = "black"
                chess_img = Image.open(f"assets/{t}_{chess.piece_name(board.piece_type_at(i))}.png")
                chess_img = chess_img.resize((70, 70))
                img.paste(chess_img, (r * 90 + 70, c * 90 + 20))
        img.save(f"{str(id)}.png")
        await ch.send(file=discord.File(f"{str(id)}.png"))
        os.remove(f"{str(id)}.png")

    @Chess.command(name='move')
    async def chess_move(self, ctx, moves):
        """Moves a piece using long form. For example, **;move e2e4**"""
        with open("boards.dat", "rb") as f:
            data = pickle.load(f)
        if not ctx.author.id in data:
            await ctx.send("You're not in a game")
            return
        if not type(data[ctx.author.id]) == chess.Board:
            await ctx.send("You don't have a chess game in progress.")
            return
        board = data[ctx.author.id]
        if ctx.author.id == board.p1:
            oppo = board.p2
            if not board.turn:
                await ctx.send("Its not your turn yet")
                return
        if ctx.author.id == board.p2:
            oppo = board.p1
            if board.turn:
                await ctx.send("Its not your turn yet")
                return

        move = moves.lower()
        try:
            if chess.Move.from_uci(move) in board.legal_moves:
                board.push(chess.Move.from_uci(move))
                await ctx.send("Completed move " + move)
                await senddm(self.bot.get_user(oppo), f"{ctx.author.name} moved " + move)
                if board.is_game_over():
                    if board.is_checkmate():
                        await senddm(self.bot.get_user(oppo), f"{ctx.author.name} won by checkmate")
                        await ctx.send(f"You checkmated {self.bot.get_user(oppo).name}")
                    elif board.is_stalemate():
                        await senddm(self.bot.get_user(oppo), f"Game ended due to stalemate")
                        await ctx.send(f"Game ended due to stalemate")
                    elif board.is_insufficient_material():
                        await senddm(self.bot.get_user(oppo), f"Game ended due to insufficient material")
                        await ctx.send(f"Game ended due to insufficient material")
                    elif board.is_fivefold_repetition():
                        await senddm(self.bot.get_user(oppo), f"Game ended due to repetition")
                        await ctx.send(f"Game ended due to repetition")
                    await self.chess_show(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
                    del data[oppo]
                    del data[ctx.author.id]

                with open("boards.dat", "wb") as f:
                    pickle.dump(data, f)
            else:
                await ctx.send("Illegal move")
        except Exception as f:
            print(f)
            await ctx.send("Invalid move")

    @Chess.command(name='new')
    @commands.bot_has_guild_permissions(add_reactions=True)
    async def chess_new(self, ctx, p2: discord.Member):
        """Starts a chess game against another player"""
        if p2 == ctx.author or p2.bot:
            await ctx.send("Can't play against yourself or against a bot")
            return
        with open("boards.dat", "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:
            await ctx.send("Quit your game before starting a new one")
            return
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        msg = await ctx.send(
            f"{p2.mention}, {ctx.author.name} challenged you to a chess match. React to message to accept/deny")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        try:
            def check(reaction, user):
                return user == p2 and reaction.message.id == msg.id and (reaction.emoji == "✅" or reaction.emoji == "❌")

            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            await ctx.send(f'Took to long for {p2.name} to respond.')
            return
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        if reaction.emoji == "✅":
            l = [ctx.author.id, p2.id]
            shuffle(l)
            board = chess.Board(l[0], l[1])
            if l[0] == ctx.author.id:
                await ctx.send(f"{ctx.author.mention} you are white")
            else:
                await ctx.send(f"{p2.mention} you are white")
            data[ctx.author.id] = board
            data[p2.id] = board

            with open("opposite.dat", "rb") as f:
                oppos = pickle.load(f)
            oppos[ctx.author.id] = p2.id
            oppos[p2.id] = ctx.author.id
            with open("opposite.dat", "wb") as f:
                pickle.dump(oppos, f)
            await self.chess_show(ctx.author, ctx.channel, board, ctx.message.id)
            with open("boards.dat", "wb") as f:
                pickle.dump(data, f)

        else:
            await ctx.send(f'{p2.name} declined')

    @commands.group()
    async def Gomoku(self, ctx):
        pass

    @Gomoku.command(name='place')
    async def g_move(self, ctx, position):
        text = position.lower()
        pos = 0

        if not len(text) in [2, 3]:
            await ctx.send("Argument must consist of one alphabet and one number")
            return
        with open("boards.dat", "rb") as f:
            data = pickle.load(f)
        if not type(data[ctx.author.id]) == g.Board:
            await ctx.send("You don't have a gomoku game in progress.")
            return
        board = data[ctx.author.id]
        if not text[0] in list(alphabet)[:board.size]:
            await ctx.send("Invalid input")
            return
        else:
            pos += list(alphabet)[:board.size].index(text[0])
        try:
            if len(text) == 2:
                pos += (int(text[1]) - 1) * board.size
                if int(text[1]) == 0:
                    await ctx.send("Invalid input")
            else:
                pos += (int(text[1:]) - 1) * board.size
                if int(text[1]) == 0:
                    await ctx.send("Invalid input")
        except ValueError:
            await ctx.send("No number passed in")
            return

        if not ctx.author.id in data:
            await ctx.send("You're not in a game")
            return
        if ctx.author.id == board.p1:
            oppo = board.p2
            if not board.turn:
                await ctx.send("Its not your turn yet")
                return
        if ctx.author.id == board.p2:
            oppo = board.p1
            if board.turn:
                await ctx.send("Its not your turn yet")
                return
        oppo = self.bot.get_user(oppo)
        move = board.place(pos)



        if not move:
            await ctx.send("Illegal move")
            return
        elif move == True:
            await ctx.send("Placed at " + text)
            await senddm(oppo, f"{ctx.author.name} placed a piece at " + text)
        elif move == "Tie":
            await ctx.send(f"Game ended, tie")
            await senddm(oppo, f"Game ended, tie")
        else:
            await ctx.send(f"You Won")
            await senddm(oppo, f"Game ended, your opponent won")
            await self.gshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
            with open("opposite.dat", "rb") as f:
                oppos = pickle.load(f)
            opponent = oppos[ctx.author.id]
            del data[ctx.author.id]

            del data[opponent]
            del oppos[opponent]
            del oppos[ctx.author.id]

            with open("opposite.dat", "wb") as f:
                pickle.dump(oppos, f)
        with open("boards.dat", "wb") as f:
            pickle.dump(data, f)

    async def gshow(self, p: discord.Member, ch: discord.TextChannel, board, id):
        w, h = (board.size * 50 + 50, board.size * 50 + 50)
        img = Image.new("RGB", (w, h))
        img1 = ImageDraw.Draw(img)
        alp = list(alphabet)[:board.size]
        img1.rectangle([50, 0, board.size * 50 + 51, board.size * 50 + 1], (200, 180, 80))
        for i in range(board.size):
            if i != board.size:
                img1.text((i * 50 + 70, board.size * 50 + 20), alp[i], font=ImageFont.truetype('Arial.ttf', 20))
                img1.text((20, i * 50 + 20), str(board.size - i), font=ImageFont.truetype('Arial.ttf', 20))

            img1.line([(75, i * 50 + 25), (board.size * 50 + 25, i * 50 + 25)], fill=None, width=0)
            img1.line([(i * 50 + 75, 25), (i * 50 + 75, board.size * 50 - 25)], fill=None, width=0)
        for i in range(board.size ** 2):
            r = board.size - 1 - i // board.size
            c = i % board.size
            if board.squares[i].piece != None:

                if board.squares[i].piece:
                    t = (0, 0, 0)
                else:
                    t = (255, 255, 255)
                img1.ellipse([c * 50 + 55, r * 50 + 5, c * 50 + 95, r * 50 + 45], t)
        img.save(f"{str(id)}.png")
        await ch.send(file=discord.File(f"{str(id)}.png"))
        os.remove(f"{str(id)}.png")

    @Gomoku.command(name='new')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(add_reactions=True)
    async def gnew(self, ctx, size: int, p2: discord.Member):
        """
        Starts a gomoku game against another player"""

        if p2 == ctx.author or p2.bot:
            await ctx.send("Can't play against yourself or against a bot")
            return
        if not size in [9, 13, 19]:
            await ctx.send("Size has to be 9, 13, or 19")
            return
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:
            await ctx.send("Quit your game before starting a new one")
            return
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        msg = await ctx.send(
            f"{p2.mention}, {ctx.author.name} challenged you to a reversi match. React to message to accept/deny")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        try:
            def check(reaction, user):
                return user == p2 and reaction.message.id == msg.id and (reaction.emoji == "✅" or reaction.emoji == "❌")

            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            await ctx.send(f'Took to long for {p2.name} to respond.')
            return
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        if reaction.emoji == "✅":
            l = [ctx.author.id, p2.id]
            shuffle(l)
            board = g.Board(size, l[0], l[1])
            if l[0] == ctx.author.id:
                await ctx.send(f"{ctx.author.mention} you are black")
            else:
                await ctx.send(f"{p2.mention} you are black")
            data[ctx.author.id] = board
            data[p2.id] = board

            with open("opposite.dat", "rb") as f:
                oppos = pickle.load(f)
            oppos[ctx.author.id] = p2.id
            oppos[p2.id] = ctx.author.id
            with open("opposite.dat", "wb") as f:
                pickle.dump(oppos, f)
            await self.gshow(ctx.author, ctx.channel, board, ctx.message.id)
            with open('boards.dat', "wb") as f:
                pickle.dump(data, f)

        else:
            await ctx.send(f'{p2.name} declined')

    @Gomoku.command(name='show')
    async def show_gomoku(self, ctx):
        """Shows the board"""
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:
            if not type(data[ctx.author.id]) == g.Board:
                await ctx.send("You don't have a gomoku game in progress.")
                return
            if data[ctx.author.id].turn:
                await ctx.send("Black to move...")
            else:
                await ctx.send("White to move...")
            await self.gshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
        else:
            await ctx.send("You don't have a game in progress.")

    @commands.group()
    async def Reversi(self, ctx):
        pass

    @commands.command()
    async def show(self, ctx):
        """Shows the board"""
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:

            if data[ctx.author.id].turn:
                await ctx.send("Black to move...")
            else:
                await ctx.send("White to move...")
            if type(data[ctx.author.id]) == r.Board:
                await self.rshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
            elif type(data[ctx.author.id]) == chess.Board:
                await self.chess_show(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
            elif type(data[ctx.author.id]) == c4.Board:
                await self.cshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
            elif type(data[ctx.author.id]) == g.Board:
                await self.gshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
        else:
            await ctx.send("You don't have a game in progress.")

    @commands.command()
    async def end(self, ctx):
        with open("boards.dat", "rb") as f:
            data = pickle.load(f)
        with open("opposite.dat", "rb") as f:
            oppo = pickle.load(f)
        if ctx.author.id in data:
            del data[ctx.author.id]
            if ctx.author.id in oppo:
                del data[oppo[ctx.author.id]]
                del oppo[oppo[ctx.author.id]]
                del oppo[ctx.author.id]

            await ctx.send("Ended game")
            with open("boards.dat", "wb") as f:
                pickle.dump(data, f)
        else:
            await ctx.send("You don't have a game in progress.")
    @Reversi.command(name='new')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(add_reactions=True)
    async def reversi_new(self, ctx, p2: discord.Member):
        """
        Starts a reversi game against another player"""
        if p2 == ctx.author or p2.bot:
            await ctx.send("Can't play against yourself or against a bot")
            return
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:
            await ctx.send("Quit your game before starting a new one")
            return
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        msg = await ctx.send(
            f"{p2.mention}, {ctx.author.name} challenged you to a reversi match. React to message to accept/deny")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        try:
            def check(reaction, user):
                return user == p2 and reaction.message.id == msg.id and (reaction.emoji == "✅" or reaction.emoji == "❌")

            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            await ctx.send(f'Took to long for {p2.name} to respond.')
            return
        if reaction.emoji == "✅":
            l = [ctx.author.id, p2.id]
            shuffle(l)
            board = r.Board(l[0], l[1])
            if l[0] == ctx.author.id:
                await ctx.send(f"{ctx.author.mention} you are black")
            else:
                await ctx.send(f"{p2.mention} you are black")
            data[ctx.author.id] = board
            data[p2.id] = board

            with open("opposite.dat", "rb") as f:
                oppos = pickle.load(f)
            oppos[ctx.author.id] = p2.id
            oppos[p2.id] = ctx.author.id
            with open("opposite.dat", "wb") as f:
                pickle.dump(oppos, f)
            await self.rshow(ctx.author, ctx.channel, board, ctx.message.id)
            with open('boards.dat', "wb") as f:
                pickle.dump(data, f)

        else:
            await ctx.send(f'{p2.name} declined')

    @Reversi.command(name='show')
    async def show_rev(self, ctx):
        """Shows the board"""
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:
            if not type(data[ctx.author.id]) == r.Board:
                await ctx.send("You don't have a reversi game in progress.")
                return
            if data[ctx.author.id].turn:
                await ctx.send("Black to move...")
            else:
                await ctx.send("White to move...")
            await self.rshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
        else:
            await ctx.send("You don't have a game in progress.")

    @Reversi.command(name='place')
    async def rplace(self, ctx, position):
        """Places a piece at a given position"""
        text = position.lower()
        pos = 0
        if len(text) != 2:
            await ctx.send("Argument must consist of one alphabet and one digit")
            return
        if not text[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            await ctx.send("The alphabet must be between a and h")
            return
        else:
            pos += ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(text[0])
        try:
            pos += (int(text[1]) - 1) * 8
            if int(text[1]) == 0 or int(text[1]) == 9:
                await ctx.send("Digit must not be 0 or 9")
        except ValueError:
            await ctx.send("No digit passed in")
            return

        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if not ctx.author.id in data:
            await ctx.send("You're not in a game")
            return
        if not type(data[ctx.author.id]) == r.Board:
            await ctx.send("You don't have a reversi game in progress.")
            return
        board = data[ctx.author.id]
        if ctx.author.id == board.p1:
            oppo = board.p2
            if not board.turn:
                await ctx.send("Its not your turn yet")
                return
        if ctx.author.id == board.p2:
            oppo = board.p1
            if board.turn:
                await ctx.send("Its not your turn yet")
                return
        oppo = self.bot.get_user(oppo)
        move = board.place(pos)

        if not move:
            await ctx.send("Illegal move")
            return
        elif move == True:
            await ctx.send("Placed at " + text)
            await senddm(oppo, f"{ctx.author.name} put a piece at {text}")
        elif move == "pass":
            await ctx.send("Placed at " + text + ", your opponent got pass")
            await senddm(oppo, f"{ctx.author.name} put a piece at {text}, you got pass")
        else:
            if move[0] > move[1]:
                await ctx.send(f"Black wins {move[0]} to {move[1]}")
                await senddm(oppo, f"Black wins {move[0]} to {move[1]}")
            elif move[0] < move[1]:
                await ctx.send(f"White wins {move[1]} to {move[0]}")
                await senddm(oppo, f"White wins {move[1]} to {move[0]}")
            else:
                await ctx.send(f"Its a tie")
                await senddm(oppo, f"Its a tie")
            await self.rshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
            with open("opposite.dat", "rb") as f:
                oppos = pickle.load(f)
            opponent = oppos[ctx.author.id]
            del data[ctx.author.id]

            del data[opponent]
            del oppos[opponent]
            del oppos[ctx.author.id]

            with open("opposite.dat", "wb") as f:
                pickle.dump(oppos, f)
        with open('boards.dat', "wb") as f:
            pickle.dump(data, f)

    async def rshow(self, p: discord.Member, ch: discord.TextChannel, board, id):

        w, h = (790, 790)
        img = Image.new("RGB", (w, h))
        img1 = ImageDraw.Draw(img)
        alp = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        img1.rectangle([60, 10, 780, 730], (0, 115, 0))
        for i in range(9):
            if i != 8:
                img1.text((i * 90 + 95, 735), alp[i], font=ImageFont.truetype('Arial.ttf', 20))
                img1.text((20, i * 90 + 50), str(9 - (i + 1)), font=ImageFont.truetype('Arial.ttf', 20))

            img1.line([(60, i * 90 + 10), (780, i * 90 + 10)], fill=None, width=0)
            img1.line([(i * 90 + 60, 10), (i * 90 + 60, 730)], fill=None, width=0)
        if board.turn:
            legal = board.p1legal()
        else:
            legal = board.p2legal()
        for i in range(64):
            c = 7 - i // 8
            r = i % 8
            if board.squares[i].piece:

                if board.squares[i].piece.color:
                    t = (0, 0, 0)
                else:
                    t = (255, 255, 255)
                img1.ellipse([r * 90 + 70, c * 90 + 20, r * 90 + 140, c * 90 + 90], t)
            if board.squares[i] in legal:
                img1.ellipse([r * 90 + 100, c * 90 + 50, r * 90 + 110, c * 90 + 60], (255, 0, 0))
        img.save(f"{str(id)}.png")
        await ch.send(file=discord.File(f"{str(id)}.png"))
        os.remove(f"{str(id)}.png")

    @commands.group()
    async def C4(self, ctx):
        pass

    @C4.command(name='new')
    @commands.bot_has_guild_permissions(add_reactions=True)
    async def c4_new(self, ctx, p2: discord.Member):
        """Starts a connect 4 game against another player"""
        if p2 == ctx.author or p2.bot:
            await ctx.send("Can't play against yourself or against a bot")
            return
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:
            await ctx.send("Quit your game before starting a new one")
            return
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        msg = await ctx.send(
            f"{p2.mention}, {ctx.author.name} challenged you to a connect4 match. React to message to accept/deny")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        try:
            def check(reaction, user):
                return user == p2 and reaction.message.id == msg.id and (reaction.emoji == "✅" or reaction.emoji == "❌")

            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

        except asyncio.TimeoutError:
            await ctx.send(f'Took to long for {p2.name} to respond.')
            return
        if p2.id in data:
            await ctx.send("Your opponent is in a game right now, please tell them to end their game")
            return
        if reaction.emoji == "✅":
            l = [ctx.author.id, p2.id]
            shuffle(l)
            board = c4.Board(l[0], l[1])
            if l[0] == ctx.author.id:
                await ctx.send(f"{ctx.author.mention} you are Red")
            else:
                await ctx.send(f"{p2.mention} you are Red")
            data[ctx.author.id] = board
            data[p2.id] = board

            with open("opposite.dat", "rb") as f:
                oppos = pickle.load(f)
            oppos[ctx.author.id] = p2.id
            oppos[p2.id] = ctx.author.id
            with open("opposite.dat", "wb") as f:
                pickle.dump(oppos, f)
            await self.cshow(ctx.author, ctx.channel, board, ctx.message.id)
            with open('boards.dat', "wb") as f:
                pickle.dump(data, f)

        else:
            await ctx.send(f'{p2.name} declined')

    @C4.command(name='place')
    async def c4_place(self, ctx, column: int):
        """Drops a piece at a column **;drop 4**"""
        if not 1 <= column <= 7:
            await ctx.send("Column has to be between 1 and 7")
            return
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if not ctx.author.id in data:
            await ctx.send("You're not in a game")
            return
        if not type(data[ctx.author.id]) == c4.Board:
            await ctx.send("You don't have a connect4 game in progress.")
            return
        board = data[ctx.author.id]
        if ctx.author.id == board.p1:
            oppo = board.p2
            if not board.turn:
                await ctx.send("Its not your turn yet")
                return
        if ctx.author.id == board.p2:
            oppo = board.p1
            if board.turn:
                await ctx.send("Its not your turn yet")
                return
        oppo = self.bot.get_user(oppo)

        x = board.place(column - 1)
        if x != False:
            await ctx.send(f"Placed a piece at column {column}")
            await senddm(oppo, f"{ctx.author.name} placed a piece at column {column}")
            if x != "legal":

                if x == 3:
                    await ctx.send("Tied")
                    await senddm(oppo, "Game ended, tied")
                else:
                    await ctx.send("You won")
                    await senddm(oppo, f"Game ended, {ctx.author.name} won")
                await self.cshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
                del data[oppo]
                del data[ctx.author.id]
            with open('boards.dat', "wb") as f:
                pickle.dump(data, f)

        else:
            await ctx.send("Invalid move")

    @C4.command(name='show')
    async def showconnect4(self, ctx):
        """Shows board image"""
        with open('boards.dat', "rb") as f:
            data = pickle.load(f)
        if ctx.author.id in data:
            if not type(data[ctx.author.id]) == c4.Board:
                await ctx.send("You don't have a connect4 game in progress.")
                return
            if data[ctx.author.id].turn:
                await ctx.send("Red to move...")
            else:
                await ctx.send("Yellow to move...")
            await self.cshow(ctx.author, ctx.channel, data[ctx.author.id], ctx.message.id)
        else:
            await ctx.send("You don't have a game in progress.")

    async def cshow(self, p: discord.Member, ch: discord.TextChannel, board, id):
        w, h = (700, 650)
        img = Image.new("RGB", (w, h))
        img1 = ImageDraw.Draw(img)
        img1.rectangle([0, 0, 701, 651], (0, 50, 255))
        for i in range(7):
            img1.text((i * 100 + 45, 620), str(i + 1), font=ImageFont.truetype('Arial.ttf', 20))

        for i in range(42):
            r = 5 - i // 7
            c = i % 7
            if board.squares[i].piece == None:
                img1.ellipse([c * 100 + 20, r * 100 + 20, c * 100 + 80, r * 100 + 80], (0, 0, 0))
            elif board.squares[i].piece == True:
                img1.ellipse([c * 100 + 20, r * 100 + 20, c * 100 + 80, r * 100 + 80], (255, 0, 0), (0, 0, 0), 2)
            else:
                img1.ellipse([c * 100 + 20, r * 100 + 20, c * 100 + 80, r * 100 + 80], (255, 255, 0), (0, 0, 0), 2)

        img.save(f"{str(id)}.png")
        await ch.send(file=discord.File(f"{str(id)}.png"))
        os.remove(f"{str(id)}.png")
def setup(bot):
    bot.add_cog(BoardGames(bot))
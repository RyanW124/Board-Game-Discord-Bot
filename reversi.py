class Board:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.pieces = 4
        self.turn = True
        self.squares = []
        self.empty = []
        for i in range(64):
            if i in [27, 36]:
                b = Piece(True)
                a = Square(i, b)
                self.squares.append(a)
                b.square = a
            elif i in [28, 35]:
                b = Piece(False)
                a = Square(i, b)
                self.squares.append(a)
                b.square = a
            else:
                x = Square(i)
                self.squares.append(x)
                self.empty.append(x)
        for i in self.squares:
            i.init_board(self)

    def p1legal(self):
        leg = []
        for i in self.empty:
            popo = 0
            for j in i:
                popo += 1
                b = False
                if not j:
                    continue
                if not j[0].piece:
                    continue
                if j[0].piece.color:
                    continue

                for s in j:
                    if s.piece:
                        if s.piece.color:
                            leg.append(i)
                            b = True
                            break
                    else:
                        break
                if b:
                    break

        return leg

    def p2legal(self):
        num = 58
        leg = []
        for i in self.empty:
            k = 1
            for j in i:

                b = False
                k += 1
                if not j:
                    continue
                if not j[0].piece:
                    continue
                if not j[0].piece.color:
                    continue
                listj = []
                for pp in j:
                    listj.append(pp.piece)

                for s in j:
                    if s.piece:
                        if not s.piece.color:
                            leg.append(i)
                            b = True
                            break
                    else:
                        break
                if b:
                    break

        return leg

    def place(self, pos):
        sq = self.squares[pos]
        if self.turn:
            legal = self.p1legal()
        else:
            legal = self.p2legal()
        if not sq in legal:
            return False
        for j in sq:

            index = 0
            if len(j) == 0:
                continue
            while j[index].piece and index < len(j):
                full = True
                for i in j:
                    if not i.piece:
                        break
                    if i.piece.color == self.turn:
                        full = False
                if full:
                    break
                if j[index].piece.color != self.turn:
                    j[index].piece.color = not j[index].piece.color

                else:
                    break
                index += 1

        sq.piece = Piece(self.turn)
        self.empty.remove(sq)
        if self.turn:
            legal = self.p1legal()
            oppolegal = self.p2legal()
        else:
            legal = self.p2legal()
            oppolegal = self.p1legal()
        if len(oppolegal) == 0:
            if len(legal) == 0:
                x = 0
                for i in self:
                    if i.piece:
                        if i.piece.color:
                            x += 1

                return x, 64 - len(self.empty) - x

            return "pass"

        sq.piece = Piece(self.turn)
        self.turn = not self.turn
        return True

    def __iter__(self):
        for i in self.squares:
            yield i


class Piece:
    def __init__(self, color):
        self.color = color
        self.square = None


class Square:
    def __init__(self, pos, piece=None):
        self.piece = piece
        self.pos = pos
        self.bottom = []
        self.top = []
        self.left = []
        self.right = []
        self.topleft = []
        self.topright = []
        self.bottomleft = []
        self.bottomright = []

    def init_board(self, board):
        self.board = board
        for i in self.board:
            if i.pos % 8 == self.pos % 8:
                if i.pos // 8 < self.pos // 8:
                    self.bottom.append(i)
                elif i.pos // 8 > self.pos // 8:
                    self.top.append(i)
            elif i.pos // 8 == self.pos // 8:

                if i.pos % 8 < self.pos % 8:
                    self.left.append(i)
                elif i.pos > self.pos:
                    self.right.append(i)
            elif self.pos % 8 - i.pos % 8 == self.pos // 8 - i.pos // 8:
                if i.pos > self.pos:
                    self.topright.append(i)
                elif i.pos < self.pos:
                    self.bottomleft.append(i)
            elif self.pos % 8 - i.pos % 8 == i.pos // 8 - self.pos // 8:
                if i.pos < self.pos:
                    self.bottomright.append(i)
                elif i.pos > self.pos:
                    self.topleft.append(i)
        self.bottomright = list(reversed(self.bottomright))
        self.bottomleft = list(reversed(self.bottomleft))
        self.left = list(reversed(self.left))
        self.bottom = list(reversed(self.bottom))
        self.dire = [self.left, self.bottomleft, self.bottom, self.bottomright, self.right, self.topright, self.top,
                     self.topleft]

    def __iter__(self):

        for k in self.dire:
            yield k

    def __str__(self):
        return f'Square at {self.pos}'


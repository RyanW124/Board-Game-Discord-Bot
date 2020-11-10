class Board:
    def __init__(self, size, p1, p2):
        self.squares = []
        self.filled = []
        self.turn = True
        self.empty = size ** 2
        self.size = size
        self.p1 = p1
        self.p2 = p2
        for i in range(size ** 2):
            self.squares.append(Dot(i))

    def place(self, pos):
        if not 0 <= pos <= (self.size ** 2) - 1:
            return False
        if self.squares[pos].piece == None:
            self.squares[pos].piece = self.turn
            self.filled.append(self.squares[pos])
            self.empty -= 1
            x = self.check()

            if x == False:
                self.turn = not self.turn
                if self.empty == 0:
                    return "Tie"
                return True

            else:
                return "Win"
        return False

    def check(self):
        for sq in self.filled:
            try:
                for i in range(1, 5):
                    if self.squares[sq.pos + i].piece != sq.piece:
                        break
                else:
                    return sq.piece

            except:
                pass
            try:
                for i in range(1, 5):

                    if self.squares[sq.pos + i * (self.size - 1)].piece != sq.piece:
                        break
                else:
                    return sq.piece
            except:
                pass
            try:
                for i in range(1, 5):
                    if self.squares[sq.pos + i * (self.size)].piece != sq.piece:
                        break
                else:
                    return sq.piece
            except:
                pass
            try:
                for i in range(1, 5):
                    if self.squares[sq.pos + i * (self.size + 1)].piece != sq.piece:
                        break
                else:
                    return sq.piece
            except:
                pass
        return False


class Dot:
    def __init__(self, pos):
        self.pos = pos
        self.piece = None
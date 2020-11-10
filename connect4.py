class Board:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.num = 0
        self.squares = []
        self.turn = True
        self.columns = [[], [], [], [], [], [], []]
        for i in range(42):
            sq = Square(i)
            self.squares.append(sq)
            self.columns[i % 7].append(sq)

    def place(self, col):
        for i in self.columns[col]:
            if i.piece == None:
                self.num += 1
                i.piece = self.turn
                self.turn = not self.turn
                x = self.check()
                if x == True:
                    return 1
                elif x == False:
                    return 2
                elif self.num == 42:
                    return 3
                return "legal"
                break
        else:
            return False

    def check(self):
        for sq in self.squares:
            if sq.piece == None:
                continue
            try:
                for i in range(1, 4):
                    if self.squares[sq.pos + i].piece != sq.piece:
                        break
                else:
                    return sq.piece

            except:
                pass
            try:
                for i in range(1, 4):

                    if self.squares[sq.pos + i * 6].piece != sq.piece:
                        break
                else:
                    return sq.piece
            except:
                pass
            try:
                for i in range(1, 4):
                    if self.squares[sq.pos + i * 7].piece != sq.piece:
                        break
                else:
                    return sq.piece
            except:
                pass
            try:
                for i in range(1, 4):
                    if self.squares[sq.pos + i * 8].piece != sq.piece:
                        break
                else:
                    return sq.piece
            except:
                pass

        return None

    def __str__(self):
        text = ""
        for r in range(6):
            text += "+"
            for c in range(7):
                text += "---+"
            text += "\n"
            for c in range(7):
                cell = self.columns[c][5 - r].piece
                if cell == None:
                    sym = " "
                elif cell == True:
                    sym = "T"
                else:
                    sym = "F"
                text += f"| {sym} "
            text += "|\n"
        text += "+"
        for c in range(7):
            text += "---+"
        return text


class Square:
    def __init__(self, pos):
        self.pos = pos
        self.piece = None
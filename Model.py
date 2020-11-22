from discord.ext.commands import Bot as b
class Server:
    def __init__(self, id):
        self.id = id
        self.members = []
        self.autokick = None
        self.mute = None
        self.ticket_category = None
        self.ticket_msg = None
        self.ticket_staffs = []
        self.ticket_react = None
        self.tickets = []

    def new_ticket(self, id, cid):

        ticket = Ticket(id, cid)
        self.tickets.append(ticket)

        return ticket
    def new_member(self, id):
        member = Member(id)
        self.members.append(member)
        return member

    def get_member(self, id):
        for i in self.members:
            if i.id == id:
                return i
        return None

    @classmethod
    def search(cls, id, array):
        for i in array:
            if i.id == id:
                return i
        return None


class Member:
    def __init__(self, id):
        self.id = id
        self.warns = 0


class Advertisement:
    def __init__(self, id, description, invite, color):
        self.id = id
        self.description = description
        self.invite = invite
        self.color = color

class Mute:
    def __init__(self, id, time, mute, guild):
        import datetime
        self.id = id
        self.mute = mute
        self.guild = guild
        if time:
            self.time = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
        else:
            self.time = None

class Ticket:
    def __init__(self, id, ch_id):
        self.id = id
        self.ch_id = ch_id

class Autorole:
    def __init__(self, id, ch_id, roles):
        self.id = id
        self.ch_id = ch_id
        self.roles = roles


class Users:

    def __init__(self, id):
        self.id = id
        self.reset()

    def reset(self):
        self.coins = 500
        self.inventory = {}

    @classmethod
    def search(cls, id, array):
        for i in array:
            if i.id == id:
                return i
        return None

class Poll:
    def __init__(self, id, ch_id, question, answers, multi=1):
        self.id: int = id
        self.ch_id: int = ch_id
        self.question: str = question
        self.answers: dict = answers
        self.multi: int = multi


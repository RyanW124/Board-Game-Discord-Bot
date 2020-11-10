class Server:
    def __init__(self, id):
        self.id = id
        self.members = []
        self.autokick = None
        self.mute = None

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

    def embed(self, name, url):
        embed = discord.Embed()
        embed.title = name
        embed.description = self.description
        embed.color = self.color
        embed.add_field(name='Invite: ', value=self.invite, inline=False)
        embed.set_thumbnail(url=url)
        return embed

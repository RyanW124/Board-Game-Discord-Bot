from random import randint

class Item:
    def __init__(self, owner, price, description, name, count=1):
        self.owner = owner
        self.owner.inventory[name] = self
        self.name = name
        self.item_count = count
        self.price = price
        self.owner.coins -= count * price
        self.description = description
        self.selling_price = price//3

    def sell(self, count=1):
        self.owner.coins += count * self.selling_price
        self.item_count -= count

    def gift(self, reciever, count=1):
        self.item_count -= count
        reciever.inventory[self.name].item_count += count


class Candy(Item):
    price = 50
    description = 'Something'
    name = 'Candy'

    def __init__(self, owner, count=1):
        super().__init__(owner, self.price, self.description, self.name, count)

    def sell(self, count=1):
        super().sell(count)
        self.owner.coins += randint(10, 20)

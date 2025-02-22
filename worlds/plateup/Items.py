from BaseClasses import Item, ItemClassification

class PlateUpItem(Item):
    game = "plateup"
    
    def __init__(self, name, classification, code, player):
        super().__init__(name, classification, code, player)
        self.code = code

    def __repr__(self):
        return "<PlateUpItem {} (ID: {})>".format(self.name, self.code)


ITEMS = {
    "Hob": (1001, ItemClassification.progression),
    "Sink": (1002, ItemClassification.progression),
    "Counter": (1003, ItemClassification.progression),
    "Dining Table": (1004, ItemClassification.progression),
}

from BaseClasses import Item, ItemClassification

class PlateUpItem(Item):
    game = "plateup"
    
    def __init__(self, name, classification, code, player):
        super().__init__(name, classification, code, player)
        self.code = code

    def __repr__(self):
        return "<{}>".format(self.name)


ITEMS = {
    #region Appliances
    "Random Appliance": (1001, ItemClassification.useful),
    "Random Filler Appliance": (1002, ItemClassification.filler),
    #endregion
    #region Speed
    "Speed Upgrade Player": (10, ItemClassification.progression),
    "Speed Upgrade Appliance": (11, ItemClassification.progression),
    "Speed Upgrade Cook": (12, ItemClassification.progression),
    "Speed Upgrade Chop": (13, ItemClassification.progression),
    "Speed Upgrade Clean": (14, ItemClassification.progression),
    #endregion

    #region progression
    "Day Lease": (15, ItemClassification.progression),
    "Money Cap Increase": (16, ItemClassification.useful),



    #endregion
    #region traps
    "EVERYTHING IS ON FIRE": (20000, ItemClassification.trap),
    "Super Slow": (20001, ItemClassification.trap),
    "Random Customer Card": (20002, ItemClassification.trap),
    "Patience Decrease": (20003, ItemClassification.trap),
    "More Customers": (20004, ItemClassification.trap),
    "Minimum Group Size Increase": (20005, ItemClassification.trap),
    "Maximum Group Size Increase": (20006, ItemClassification.trap),
    "Random Dish Extra": (20007, ItemClassification.trap),
    "Random Side Dish": (20008, ItemClassification.trap),
    "Tip Jar Drain": (20009, ItemClassification.trap),
    "Good Advertisement": (20010, ItemClassification.trap),
    "Card Swap": (20011, ItemClassification.trap),
    #endregion
    #region filler
    "Patience Increase": (40001, ItemClassification.filler),
    "Less Customers": (40002, ItemClassification.filler),
    "Minimum Group Size Decrease": (40003, ItemClassification.filler),
    "Maximum Group Size Decrease": (40004, ItemClassification.filler),
    "Mess Reduction": (40005, ItemClassification.filler),
    "Coin": (40006, ItemClassification.filler),
    "Random Decoration Unlock": (40007, ItemClassification.filler),
    #endregion
    #region new progression
    "Global Patience Increase": (50001, ItemClassification.progression),
    "Remove Card": (50002, ItemClassification.progression),
    #endregion
}

# Add unlock items for each dish from a single source of truth
try:
    from .Locations import dish_dictionary
    for dish_id, dish_name in dish_dictionary.items():
        ITEMS[f"{dish_name} Unlock"] = (30000 + dish_id, ItemClassification.progression)
except Exception:
    for dish_id, dish_name in {
        101: "Salad",
        102: "Steak",
        103: "Burger",
        104: "Coffee",
        105: "Pizza",
        106: "Dumplings",
        107: "Turkey",
        108: "Pie",
        109: "Cakes",
        110: "Spaghetti",
        111: "Fish",
        112: "Tacos",
        113: "Hot Dogs",
        114: "Breakfast",
        115: "Stir Fry",
        116: "Sandwiches",
        117: "Sundaes",
    }.items():
        ITEMS[f"{dish_name} Unlock"] = (30000 + dish_id, ItemClassification.progression)
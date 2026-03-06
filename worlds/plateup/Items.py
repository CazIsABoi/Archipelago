from BaseClasses import Item, ItemClassification

class PlateUpItem(Item):
    game = "plateup"
    
    def __init__(self, name, classification, code, player):
        super().__init__(name, classification, code, player)
        self.code = code

    def __repr__(self):
        return "<{}>".format(self.name)


appliance_unlock_dictionary = {
    1: "Hob",
    2: "Hob (Safe)",
    3: "Hob (Danger)",
    4: "Oven",
    5: "Microwave",
    6: "Sink",
    7: "Power Sink",
    8: "Soaking Sink",
    9: "Dishwasher",
    10: "Large Sink",
    11: "Counter",
    12: "Workstation",
    13: "Freezer",
    14: "Prep Station",
    15: "Frozen Prep Station",
    16: "Research Desk",
    17: "Copy Desk",
    18: "Discount Desk",
    19: "Ordering Desk",
    20: "Grabber",
    21: "Smart Grabber",
    22: "Rotatable Grabber",
    23: "Combiner",
    24: "Portioner",
    25: "Mixer",
    26: "Mixer (Pusher)",
    27: "Heated Mixer",
    28: "Rapid Mixer",
    29: "Auto Plater",
    30: "Pot Stack",
    31: "Serving Board Stack",
    32: "Ice Dispenser",
    33: "Milk Dispenser",
    34: "Mop Bucket",
    35: "Lasting Mop",
    36: "Fast Mop",
    37: "Robot Mop",
    38: "Floor Buffer",
    39: "Robot Buffer",
    40: "Breadsticks",
    41: "Candles",
    42: "Napkins",
    43: "Sharp Cutlery",
    44: "Specials Menu",
    45: "Leftovers Bag",
    46: "Supply Cabinet",
    47: "Host Stand",
    48: "Flower Pot",
    49: "Coffee Table",
    50: "Food Display",
    51: "Fire Extinguisher Holder",
    52: "Plate Stack",
    53: "Starting Plate Stack",
    54: "Wok Stack",
    55: "Lasagne Tray",
    56: "Taco Tray",
    57: "Mixing Bowls",
    58: "Big Cake Tin",
    59: "Brownie Tray",
    60: "Cookie Tray",
    61: "Cupcake Tray",
    62: "Doughnut Tray",
}

ITEMS = {
    #region Appliances
    "Random Appliance": (1001, ItemClassification.filler),
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
    "Money Cap Increase": (16, ItemClassification.progression),
    "Remove Card": (21, ItemClassification.progression),
    #endregion

    #region useful
    "Shop Size Increase": (22, ItemClassification.useful),
    #endregion

    #region money
    "5 Coins": (17, ItemClassification.filler),
    "10 Coins": (18, ItemClassification.filler),
    "20 Coins": (19, ItemClassification.filler),
    #endregion
    #region decorations
    "Random Decoration Unlock": (100, ItemClassification.filler),
    #endregion
    #region traps
    "EVERYTHING IS ON FIRE": (20000, ItemClassification.trap),
    "Super Slow": (20001, ItemClassification.trap),
    "Random Customer Card": (20002, ItemClassification.trap),
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

# Appliances that are fundamental to progression
APPLIANCE_PROGRESSION = {"Hob", "Counter"}

# Appliances that have little impact on progression
APPLIANCE_FILLER = {
    "Ice Dispenser", "Milk Dispenser",
    "Mop Bucket", "Lasting Mop", "Fast Mop", "Robot Mop",
    "Floor Buffer", "Robot Buffer",
    "Breadsticks", "Candles", "Napkins", "Sharp Cutlery",
    "Specials Menu", "Leftovers Bag", "Supply Cabinet", "Host Stand",
    "Flower Pot", "Coffee Table", "Food Display", "Fire Extinguisher Holder",
    "Plate Stack", "Starting Plate Stack", "Wok Stack",
    "Lasagne Tray", "Taco Tray", "Mixing Bowls",
    "Big Cake Tin", "Brownie Tray", "Cookie Tray", "Cupcake Tray", "Doughnut Tray",
    "Pot Stack", "Serving Board Stack",
}

# Add unlock items for each appliance
for appliance_id, appliance_name in appliance_unlock_dictionary.items():
    if appliance_name in APPLIANCE_PROGRESSION:
        classification = ItemClassification.progression
    elif appliance_name in APPLIANCE_FILLER:
        classification = ItemClassification.filler
    else:
        classification = ItemClassification.useful
    ITEMS[f"Unlock {appliance_name}"] = (2000 + appliance_id, classification)
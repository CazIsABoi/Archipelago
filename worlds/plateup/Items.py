from BaseClasses import Item, ItemClassification

class PlateUpItem(Item):
    game = "PlateUp"
    
    def __init__(self, name, classification, code, player):
        super().__init__(name, classification, code, player)
        self.code = code

    def __repr__(self):
        return "<{}>".format(self.name)


appliance_unlock_dictionary = {
    # Cooking
    1: "Hob",
    2: "Safe Hob",
    3: "Danger Hob",
    5: "Oven",
    6: "Microwave",
    7: "Gas Limiter",
    8: "Gas Override",
    # Sinks
    9: "Sink",
    10: "Power Sink",
    11: "Soaking Sink",
    13: "Dishwasher",
    14: "Wash Basin",
    # Prep counters
    15: "Counter",
    16: "Workstation",
    17: "Freezer",
    18: "Prep Station",
    19: "Frozen Prep Station",
    # Tables
    20: "Dining Table",
    21: "Bar Table",
    22: "Basic Cloth Table",
    23: "Cheap Metal Table",
    24: "Fancy Cloth Table",
    25: "Coffee Table",
    # Bins & floor
    27: "Bin",
    28: "Compactor Bin",
    29: "Composter Bin",
    30: "Expanded Bin",
    31: "Floor Protector",
    # Tool providers
    32: "Rolling Pin",
    33: "Sharp Knife",
    34: "Scrubbing Brush",
    # Extras & decorations
    35: "Breadsticks",
    36: "Candles",
    37: "Napkins",
    38: "Sharp Cutlery",
    39: "Specials Menu",
    40: "Leftovers Bag",
    41: "Supply Cabinet",
    42: "Host Stand",
    43: "Flower Pot",
    # Cleaning
    44: "Mop Bucket",
    45: "Lasting Mop Bucket",
    46: "Fast Mop Bucket",
    47: "Robot Mop",
    48: "Floor Buffer",
    49: "Robot Buffer",
    50: "Dish Rack",
    # Automation
    51: "Belt",
    52: "Grabber",
    53: "Smart Grabber",
    54: "Rotatable Grabber",
    55: "Combiner",
    56: "Portioner",
    57: "Mixer",
    58: "Conveyor Mixer",
    59: "Heated Mixer",
    60: "Rapid Mixer",
    # Desks
    61: "Blueprint Cabinet",
    62: "Research Desk",
    63: "Ordering Desk",
    64: "Discount Desk",
    65: "Clipboard Stand",
    66: "Copy Desk",
    # Shoes
    67: "Trainers",
    68: "Wellies",
    69: "Work Boots",
    # Misc
    70: "Booking Desk",
    71: "Food Display",
    72: "Dumbwaiter",
    73: "Teleporter",
    74: "Fire Extinguisher",
    75: "Ordering Terminal",
    76: "Specials Terminal",
    # Plate providers
    78: "Plate Stack",
    79: "Auto Plater",
    80: "Pot Stack",
    81: "Serving Board Stack",
    # Dispensers & specialty
    82: "Coffee Machine",
    83: "Ice Dispenser",
    84: "Milk Dispenser",
    85: "Wok Stack",
    86: "Lasagne Tray",
    87: "Taco Tray",
    88: "Mixing Bowls",
    89: "Big Cake Tin",
    90: "Brownie Tray",
    91: "Cookie Tray",
    92: "Cupcake Tray",
    93: "Doughnut Tray",
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
    "Reduce Group Size": (23, ItemClassification.progression),
    "Global Patience Increase": (28, ItemClassification.progression),
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
    #region gameplay filler
    "Patience Increase": (24, ItemClassification.filler),
    "Less Customers": (25, ItemClassification.filler),
    "Minimum Group Size Decrease": (26, ItemClassification.filler),
    "Maximum Group Size Decrease": (27, ItemClassification.filler),
    "Mess Reduction": (29, ItemClassification.filler),
    #endregion
    #region traps
    "EVERYTHING IS ON FIRE": (20000, ItemClassification.trap),
    "Super Slow": (20001, ItemClassification.trap),
    "Random Customer Card": (20002, ItemClassification.trap),
    "Patience Decrease": (20003, ItemClassification.trap),
    "More Customers": (20004, ItemClassification.trap),
    "Minimum Group Size Increase": (20005, ItemClassification.trap),
    "Maximum Group Size Increase": (20006, ItemClassification.trap),
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
APPLIANCE_PROGRESSION = {"Hob", "Counter", "Dining Table", "Sink", "Plate Stack", "Blueprint Cabinet", "Research Desk"}

# Appliances that have little impact on progression
APPLIANCE_FILLER = {
    # Bins & floor protection
    "Bin", "Compactor Bin", "Composter Bin", "Expanded Bin", "Floor Protector",
    # Cleaning
    "Mop Bucket", "Lasting Mop Bucket", "Fast Mop Bucket", "Robot Mop",
    "Floor Buffer", "Robot Buffer", "Dish Rack",
    # Decorative extras
    "Breadsticks", "Candles", "Napkins", "Sharp Cutlery",
    "Specials Menu", "Leftovers Bag", "Supply Cabinet", "Host Stand",
    "Flower Pot", "Coffee Table",
    # Dispensers
    "Ice Dispenser", "Milk Dispenser",
    # Table variants (less essential than Dining Table)
    "Bar Table", "Basic Cloth Table", "Cheap Metal Table", "Fancy Cloth Table",
    # Trays & specialty stacks
    "Pot Stack", "Serving Board Stack",
    "Wok Stack", "Lasagne Tray", "Taco Tray", "Mixing Bowls",
    "Big Cake Tin", "Brownie Tray", "Cookie Tray", "Cupcake Tray", "Doughnut Tray",
    # Tool providers
    "Rolling Pin", "Scrubbing Brush",
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
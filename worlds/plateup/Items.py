from typing import Dict, List
from BaseClasses import Item, ItemClassification

class PlateUpItem(Item):
    game = "PlateUp"
    
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
    # Overtime Day Lease: used in place of Day Lease for goals 0/1 (franchise/day-count)
    # when day_lease_mode = dish_specific. Dishes get their own named leases; the Overtime
    # lease gates higher day tiers in the non-dish progression ladder.
    "Overtime Day Lease": (32000, ItemClassification.progression),
    "Money Cap Increase": (16, ItemClassification.progression),



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

# ─── Dish-Specific Day Lease Items ────────────────────────────────────────────
# Used when day_lease_mode = dish_specific. Each dish gets its own lease item
# (e.g. "Fish Day Lease") that gates only that dish's day-location chain.
# IDs: 31000 + dish_id  (31101 – 31118).
try:
    from .Locations import dish_dictionary as _lease_dish_dict
    for _lease_id, _lease_name in _lease_dish_dict.items():
        ITEMS[f"{_lease_name} Day Lease"] = (31000 + _lease_id, ItemClassification.progression)
except Exception:
    for _lease_id, _lease_name in {
        101: "Salad", 102: "Steak", 103: "Burger", 104: "Coffee", 105: "Pizza",
        106: "Dumplings", 107: "Turkey", 108: "Pie", 109: "Cakes", 110: "Spaghetti",
        111: "Fish", 112: "Tacos", 113: "Hot Dogs", 114: "Breakfast", 115: "Stir Fry",
        116: "Sandwiches", 117: "Sundaes", 118: "Fajita",
    }.items():
        ITEMS[f"{_lease_name} Day Lease"] = (31000 + _lease_id, ItemClassification.progression)

# ─── Appliance Unlock Pool ────────────────────────────────────────────────────
# Priority appliances are always chosen first when building the randomised pool.
# Names MUST match the keys used in the mod's ProgressionMapping dictionaries exactly.

APPLIANCE_UNLOCK_PRIORITY: List[str] = [
    "Hob", "Counter", "Sink", "Plate Stack", "Research Desk", "Conveyor Belt", "Grabber",
]

APPLIANCE_UNLOCK_POOL: List[str] = [
    # ── Priority (always chosen first) ──────────────────────────────────────
    "Hob", "Counter", "Sink", "Plate Stack", "Research Desk", "Conveyor Belt", "Grabber",
    # ── Useful appliances (usefulApplianceDictionary, minus priority) ────────
    "Hob (Safe)", "Hob (Danger)", "Oven", "Microwave", "Gas Limiter", "Gas Safety Override",
    "Power Sink", "Soaking Sink", "Dishwasher", "Large Sink",
    "Workstation", "Freezer", "Prep Station", "Frozen Prep Station",
    "Dining Table", "Bar Table", "Basic Cloth Table", "Metal Table", "Fancy Cloth Table",
    "Rolling Pin", "Sharp Knife", "Scrubbing Brush", "Trainers",
    "Copy Desk", "Discount Desk", "Ordering Desk", "Booking Desk",
    "Dumbwaiter", "Teleporter", "Ordering Terminal", "Ordering Terminal (Specials)",
    "Smart Grabber", "Rotatable Grabber",
    "Combiner", "Portioner", "Mixer", "Mixer (Pusher)", "Heated Mixer", "Rapid Mixer",
    "Auto Plater", "Dish Rack",
    "Pot Stack", "Serving Board Stack", "Wok Stack",
    "Lasagne Tray", "Taco Tray", "Mixing Bowls",
    "Big Cake Tin", "Brownie Tray", "Cookie Tray", "Cupcake Tray", "Doughnut Tray",
    # ── Filler appliances (fillerApplianceDictionary) ────────────────────────
    "Bin", "Compactor Bin", "Composter Bin", "Expanded Bin",
    "Floor Protector", "Wellies", "Work Boots", "Clipboard Stand",
    "Ice Dispenser", "Milk Dispenser", "Coffee Machine",
    "Mop Bucket", "Lasting Mop", "Fast Mop", "Robot Mop", "Floor Buffer", "Robot Buffer",
    "Breadsticks", "Candles", "Napkins", "Sharp Cutlery", "Specials Menu",
    "Leftovers Bag", "Supply Cabinet", "Blueprint Cabinet", "Host Stand",
    "Flower Pot", "Coffee Table", "Food Display", "Fire Extinguisher Holder",
]

# IDs for appliance unlock items start at 60001 (avoids all existing ranges).
APPLIANCE_UNLOCK_ITEMS: Dict[str, int] = {
    name: 60000 + i for i, name in enumerate(APPLIANCE_UNLOCK_POOL, start=1)
}

# Register every named appliance unlock in the shared ITEMS dict.
for _app_name, _app_id in APPLIANCE_UNLOCK_ITEMS.items():
    ITEMS[f"Unlock {_app_name}"] = (_app_id, ItemClassification.useful)
import typing
from BaseClasses import MultiWorld, Location
from Options import Accessibility
from .Locations import DISH_LOCATIONS, dish_dictionary
import random

if typing.TYPE_CHECKING:
    import BaseClasses

    CollectionRule = typing.Callable[[BaseClasses.CollectionState], bool]
    ItemRule = typing.Callable[[BaseClasses.Item], bool]
else:
    CollectionRule = typing.Callable[[object], bool]
    ItemRule = typing.Callable[[object], bool]

def set_rule(spot: typing.Union["BaseClasses.Location", "BaseClasses.Entrance"], rule: CollectionRule):
    """Sets an access rule on a location or entrance."""
    spot.access_rule = rule

def add_rule(spot: typing.Union["BaseClasses.Location", "BaseClasses.Entrance"], rule: CollectionRule, combine="and"):
    """Adds an access rule while preserving existing ones."""
    old_rule = spot.access_rule
    if old_rule is Location.access_rule:
        spot.access_rule = rule if combine == "and" else old_rule
    else:
        if combine == "and":
            spot.access_rule = lambda state: rule(state) and old_rule(state)
        else:
            spot.access_rule = lambda state: rule(state) or old_rule(state)

def restrict_locations_by_progression(multiworld: MultiWorld, player: int):
    """Enforces a sequential progression system for PlateUp."""
    
    plateup_world = multiworld.worlds[player]
    franchise_order = plateup_world.valid_dish_locations 

    for i in range(len(franchise_order) - 1):
        current_location = franchise_order[i]
        next_location = franchise_order[i + 1]

    if next_location in plateup_world.location_name_to_id:
        try:
            loc = multiworld.get_location(next_location, player)
            loc.access_rule = lambda state, cur=current_location: state.can_reach(cur, "Location", player)
        except KeyError:
            print(f"⚠ Skipping rule for {next_location}: Not found in MultiWorld.")
    else:
        print(f"⚠ {next_location} not found in location_name_to_id, skipping.")


def filter_selected_dishes(multiworld: MultiWorld, player: int):
    """Filters out dish locations based on selected dishes in `Options.py`."""
    dish_count = multiworld.dish[player].value  # Number of dishes selected
    all_dish_names = list(dish_dictionary.values())
    selected_dishes = random.sample(all_dish_names, min(dish_count, len(all_dish_names)))
    multiworld.selected_dishes[player] = selected_dishes

    print(f"Selected Dishes for Player {player}: {selected_dishes}")

    valid_dish_locations = []
    for dish in selected_dishes:
        for day in range(1, 16):
            location_name = f"{dish} - Day {day}"
            if location_name in DISH_LOCATIONS:
                valid_dish_locations.append(location_name)

    # Store the valid locations to be used by Fill.py
    multiworld.worlds[player].valid_dish_locations = valid_dish_locations
    print(f"Filtered Dish Locations for Player {player}: {valid_dish_locations}")

def apply_rules(multiworld: MultiWorld, player: int):
    """Apply all game rules for PlateUp."""
    restrict_locations_by_progression(multiworld, player)

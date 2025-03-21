# Rules.py
import typing
import random
from BaseClasses import MultiWorld, Location
from Options import Accessibility
from .Locations import (
    DAY_LOCATION_DICT,
    FRANCHISE_LOCATION_DICT,
    EXCLUDED_LOCATIONS,
    DISH_LOCATIONS,
    dish_dictionary
)

if typing.TYPE_CHECKING:
    from .__init__ import PlateUpWorld

def set_rule(spot: typing.Union["BaseClasses.Location", "BaseClasses.Entrance"], rule):
    spot.access_rule = rule

def add_rule(spot: typing.Union["BaseClasses.Location", "BaseClasses.Entrance"], rule, combine="and"):
    old_rule = spot.access_rule
    if old_rule is Location.access_rule:
        spot.access_rule = rule if combine == "and" else old_rule
    else:
        if combine == "and":
            spot.access_rule = lambda state: rule(state) and old_rule(state)
        else:
            spot.access_rule = lambda state: rule(state) or old_rule(state)

def restrict_locations_by_progression(multiworld: MultiWorld, player: int):
    """
    (Optional) If you want some dish-based progression chaining, etc.
    """

    plateup_world = multiworld.worlds[player]
    if not hasattr(plateup_world, "valid_dish_locations"):
        print(f"⚠ `valid_dish_locations` missing for Player {player}, skipping dish-based progression.")
        return

    dish_order = plateup_world.valid_dish_locations
    for i in range(len(dish_order) - 1):
        current_loc_name = dish_order[i]
        next_loc_name = dish_order[i + 1]
        if next_loc_name in plateup_world.location_name_to_id:
            try:
                loc = multiworld.get_location(next_loc_name, player)
                loc.access_rule = lambda state, cur=current_loc_name: state.can_reach(cur, "Location", player)
            except KeyError:
                pass

def filter_selected_dishes(multiworld: MultiWorld, player: int):
    """
    If user picks "dish=3", we randomly pick 3 dishes out of the set,
    store them in multiworld.selected_dishes, etc.
    """
    if not hasattr(multiworld, "selected_dishes"):
        multiworld.selected_dishes = {}

    if hasattr(multiworld.worlds[player], "valid_dish_locations") and multiworld.worlds[player].valid_dish_locations:
        print(f"✅ Dish filtering already done for Player {player}, skipping.")
        return

    print(f"⚠ `valid_dish_locations` missing for Player {player}, running `filter_selected_dishes()` now...")

    plateup_world = multiworld.worlds[player]
    if plateup_world.game != "plateup":
        print(f"⚠ Skipping dish filtering: Player {player} is not PlateUp.")
        return

    dish_count = multiworld.dish[player].value
    all_dishes = list(dish_dictionary.values())
    selected = random.sample(all_dishes, min(dish_count, len(all_dishes)))
    multiworld.selected_dishes[player] = selected

    valid_locs = []
    for dish in selected:
        for day in range(1, 16):
            loc_name = f"{dish} - Day {day}"
            if loc_name in DISH_LOCATIONS:
                valid_locs.append(loc_name)

    plateup_world.valid_dish_locations = valid_locs
    print(f"✅ Filtered Dish Locations for Player {player}: {valid_locs}")

def apply_rules(multiworld: MultiWorld, player: int):
    """
    Chain days or franchise checks if needed.
    """
    plateup_world = multiworld.worlds[player]
    goal_type = plateup_world.options.goal.value  # 0 => franchise, 1 => day

    # Day-chaining
    if goal_type == 1:
        for i in range(2, 101):
            current_day = f"Complete Day {i}"
            prev_day = f"Complete Day {i-1}"
            try:
                loc_current = multiworld.get_location(current_day, player)
                loc_current.access_rule = (
                    lambda state, p=prev_day: state.can_reach(p, "Location", player)
                )
            except KeyError:
                pass

    # Franchise-chaining
    else:
        # chain “Franchise 2 times” => “Franchise 1 times”, up to user’s chosen franchise_count
        for i in range(2, 11):
            current_name = f"Franchise {i} times"
            prev_name = f"Franchise {i-1} times"
            try:
                loc_current = multiworld.get_location(current_name, player)
                loc_current.access_rule = (
                    lambda state, p=prev_name: state.can_reach(p, "Location", player)
                )
            except KeyError:
                pass


    print(f"[Player {player}] Finished apply_rules for goal={goal_type}")

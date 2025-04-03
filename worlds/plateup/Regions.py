import random
import math
from BaseClasses import Region
from .Locations import (
    PlateUpLocation,
    EXCLUDED_LOCATIONS,
    FRANCHISE_LOCATION_DICT,
    DAY_LOCATION_DICT,
    DISH_LOCATIONS,
    dish_dictionary
)
from .Options import Goal


def create_plateup_regions(multiworld, player):
    from .Locations import PlateUpLocation
    from .Options import Goal

    menu_region = Region("Menu", player, multiworld)
    progression_region = Region("Progression", player, multiworld)
    dish_region = Region("Dish Checks", player, multiworld)

    multiworld.regions += [menu_region, progression_region, dish_region]
    menu_region.connect(progression_region)
    progression_region.connect(dish_region)

    user_goal = multiworld.goal[player].value
    progression_locs = []

    if user_goal == 0:
        # Franchise goal
        for loc_id in DAY_LOCATION_DICT.values():
            EXCLUDED_LOCATIONS.add(loc_id)

        required_franchises = multiworld.franchise_count[player].value
        max_franchise_id = (required_franchises + 1) * 100000

        for name, loc_id in FRANCHISE_LOCATION_DICT.items():
            if loc_id < max_franchise_id or name == f"Franchise {required_franchises} times":
                loc = PlateUpLocation(player, name, loc_id, parent=progression_region)
                progression_region.locations.append(loc)
                progression_locs.append(name)
            else:
                EXCLUDED_LOCATIONS.add(loc_id)

    elif user_goal == 1:
        # Day goal
        for loc_id in FRANCHISE_LOCATION_DICT.values():
            EXCLUDED_LOCATIONS.add(loc_id)

        required_days = multiworld.day_count[player].value
        max_stars = math.ceil(required_days / 3)

        for name, loc_id in DAY_LOCATION_DICT.items():
            if name.startswith("Complete Day "):
                day = int(name.removeprefix("Complete Day ").strip())
                if day > required_days:
                    EXCLUDED_LOCATIONS.add(loc_id)
                    continue
            elif name.startswith("Complete Star "):
                star = int(name.removeprefix("Complete Star ").strip())
                if star > max_stars:
                    EXCLUDED_LOCATIONS.add(loc_id)
                    continue
            loc = PlateUpLocation(player, name, loc_id, parent=progression_region)
            progression_region.locations.append(loc)
            progression_locs.append(name)

    multiworld.worlds[player].progression_locations = progression_locs
    print(f"[Player {player}] Final progression-locs: {progression_locs}")
    progression_locs = []

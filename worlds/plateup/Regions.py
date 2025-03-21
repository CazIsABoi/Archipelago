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
    menu_region = Region("Menu", player, multiworld)
    progression_region = Region("Progression", player, multiworld)
    dish_region = Region("Dish Checks", player, multiworld)

    if menu_region not in multiworld.regions:
        multiworld.regions.append(menu_region)
    if progression_region not in multiworld.regions:
        multiworld.regions.append(progression_region)
    if dish_region not in multiworld.regions:
        multiworld.regions.append(dish_region)

    menu_region.connect(progression_region)
    progression_region.connect(dish_region)

    user_goal = multiworld.goal[player].value  # 0 => Franchise, 1 => Day
    progression_locs = []

    if user_goal == 0:
        # ============ FRANCHISE MODE ============
        # Exclude all day checks
        for loc_id in DAY_LOCATION_DICT.values():
            EXCLUDED_LOCATIONS.add(loc_id)

        required_franchises = multiworld.franchise_count[player].value
        # If N=3 => exclude everything with ID >= 400000
        max_franchise_id = (required_franchises + 1) * 100000

        for name, loc_id in FRANCHISE_LOCATION_DICT.items():
            if loc_id < max_franchise_id:
                # It's within the player's selected franchise limit
                loc_obj = PlateUpLocation(player, name, loc_id, parent=progression_region)
                progression_region.locations.append(loc_obj)
                progression_locs.append(name)
            else:
                # ID >= max_franchise_id => exclude
                EXCLUDED_LOCATIONS.add(loc_id)

    else:
        # ============ DAY MODE ============
        # Exclude all franchise checks
        for loc_id in FRANCHISE_LOCATION_DICT.values():
            EXCLUDED_LOCATIONS.add(loc_id)

        required_days = multiworld.day_count[player].value
        max_stars = math.ceil(required_days / 3)

        for name, loc_id in DAY_LOCATION_DICT.items():
            if name.startswith("Complete Day "):
                day_str = name.removeprefix("Complete Day ").strip()
                if day_str.isdigit():
                    day_num = int(day_str)
                    if day_num > required_days:
                        EXCLUDED_LOCATIONS.add(loc_id)
                        continue
            elif name.startswith("Complete Star "):
                star_str = name.removeprefix("Complete Star ").strip()
                if star_str.isdigit():
                    star_num = int(star_str)
                    if star_num > max_stars:
                        EXCLUDED_LOCATIONS.add(loc_id)
                        continue
                else:
                    EXCLUDED_LOCATIONS.add(loc_id)
                    continue

            loc_obj = PlateUpLocation(player, name, loc_id, parent=progression_region)
            progression_region.locations.append(loc_obj)
            progression_locs.append(name)

    multiworld.worlds[player].progression_locations = progression_locs
    print(f"[Player {player}] Final progression-locs: {progression_locs}")

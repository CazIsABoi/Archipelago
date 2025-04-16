# Regions.py
import math
from BaseClasses import Region, LocationProgressType  # <-- IMPORT LocationProgressType
from .Locations import (
    PlateUpLocation,
    EXCLUDED_LOCATIONS,
    FRANCHISE_LOCATION_DICT,
    DAY_LOCATION_DICT,
    DISH_LOCATIONS
)

def create_plateup_regions(multiworld, player):
    plateup_world = multiworld.worlds[player]

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
                # Mark location as excluded if it's in EXCLUDED_LOCATIONS
                if loc_id in EXCLUDED_LOCATIONS:
                    loc.progress_type = LocationProgressType.EXCLUDED
                progression_region.locations.append(loc)
                progression_locs.append(name)
            else:
                plateup_world.excluded_locations.add(loc_id)

    elif user_goal == 1:
        # Day goal
        # Exclude all franchise locations
        for loc_id in FRANCHISE_LOCATION_DICT.values():
            plateup_world.excluded_locations.add(loc_id)

        required_days = multiworld.day_count[player].value
        max_stars = math.ceil(required_days / 3)

        # Only add "Complete Day" locations that are within the required days
        for name, loc_id in DAY_LOCATION_DICT.items():
            if name.startswith("Complete Day "):
                day = int(name.removeprefix("Complete Day ").strip())
                if day <= required_days:
                    loc = PlateUpLocation(player, name, loc_id, parent=progression_region)
                    # Mark location as excluded if it's in EXCLUDED_LOCATIONS
                    if loc_id in EXCLUDED_LOCATIONS:
                        loc.progress_type = LocationProgressType.EXCLUDED
                    progression_locs.append(name)
                    progression_region.locations.append(loc)
                else:
                    plateup_world.excluded_locations.add(loc_id)

        # Only add "Complete Star" locations that are within the allowed stars
        for name, loc_id in DAY_LOCATION_DICT.items():
            if name.startswith("Complete Star "):
                star = int(name.removeprefix("Complete Star ").strip())
                if star <= max_stars:
                    loc = PlateUpLocation(player, name, loc_id, parent=progression_region)
                    # Mark location as excluded if it's in EXCLUDED_LOCATIONS
                    if loc_id in EXCLUDED_LOCATIONS:
                        loc.progress_type = LocationProgressType.EXCLUDED
                    progression_locs.append(name)
                    progression_region.locations.append(loc)
                else:
                    plateup_world.excluded_locations.add(loc_id)

    multiworld.worlds[player].progression_locations = progression_locs
    print(f"[Player {player}] Final progression-locs: {progression_locs}")

import random
from BaseClasses import Region
from .Locations import PlateUpLocation, LOCATIONS, DISH_LOCATIONS, dish_dictionary

def create_plateup_regions(multiworld, player):
    menu_region = Region("Menu", player, multiworld)
    progression_region = Region("Progression", player, multiworld)
    dish_region = Region("Dish Checks", player, multiworld)

    multiworld.regions.extend([menu_region, progression_region, dish_region])

    # Set region connections
    menu_region.connect(progression_region)
    progression_region.connect(dish_region)

    # Ensure dish selection
    if not hasattr(multiworld, "selected_dishes"):
        multiworld.selected_dishes = {}

    # Select dishes
    dish_count = multiworld.dish[player].value
    all_dishes = list(dish_dictionary.keys())
    selected_dishes = random.sample(all_dishes, min(dish_count, len(all_dishes)))
    multiworld.selected_dishes[player] = [dish_dictionary[d] for d in selected_dishes]

    print(f"Selected Dishes: {multiworld.selected_dishes[player]}")

    # 🔥 Register dish locations (Even Unused Ones)
    for loc_name, loc_id in DISH_LOCATIONS.items():
        loc = PlateUpLocation(player, loc_name, loc_id, parent=dish_region)
        dish_region.locations.append(loc)

    # 🔥 Now filter for selected dishes (Remove unselected dish checks)
    dish_region.locations = [loc for loc in dish_region.locations if any(dish in loc.name for dish in multiworld.selected_dishes[player])]

    # Assign progression locations
    for loc_name, loc_id in LOCATIONS.items():
        loc = PlateUpLocation(player, loc_name, loc_id, parent=progression_region)
        progression_region.locations.append(loc)

    multiworld.regions.extend([progression_region, dish_region])

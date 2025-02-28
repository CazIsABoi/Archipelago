import random
from BaseClasses import Region
from .Locations import PlateUpLocation, LOCATIONS, dish_dictionary, add_filtered_dish_locations

def create_plateup_regions(multiworld, player):
    menu_region = Region("Menu", player, multiworld)
    progression_region = Region("Progression", player, multiworld)
    dish_region = Region("Dish Checks", player, multiworld)

    multiworld.regions.extend([menu_region, progression_region, dish_region])

    # Set region connections (ensuring accessibility)
    menu_region.connect(progression_region)
    progression_region.connect(dish_region)

    # Ensure selected_dishes is initialized
    if not hasattr(multiworld, "selected_dishes"):
        multiworld.selected_dishes = {}

    # Select random dishes
    dish_count = multiworld.dish[player].value
    all_dishes = list(dish_dictionary.keys())

    if dish_count > len(all_dishes):
        dish_count = len(all_dishes)

    selected_dishes = random.sample(all_dishes, dish_count)
    selected_dish_names = {dish_dictionary[dish_id] for dish_id in selected_dishes}

    print(f"Selected Dishes: {selected_dish_names}")

    # Store selected dishes properly
    multiworld.selected_dishes[player] = [dish_dictionary[dish_id] for dish_id in selected_dishes]

    # Add only filtered dish locations
    add_filtered_dish_locations(selected_dishes)

    # Add locations to regions
    for loc_name, loc_id in LOCATIONS.items():
        if "Day" not in loc_name:  # Progression locations
            loc = PlateUpLocation(player, loc_name, loc_id, parent=progression_region)
            progression_region.locations.append(loc)
        else:  # Dish locations
            loc = PlateUpLocation(player, loc_name, loc_id, parent=dish_region)
            dish_region.locations.append(loc)

    multiworld.regions.extend([progression_region, dish_region])


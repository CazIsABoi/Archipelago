import random
from .Locations import PlateUpLocation, LOCATIONS, DISH_LOCATIONS, dish_dictionary
from BaseClasses import Region

def create_plateup_regions(multiworld, player):
    # Create regions
    menu_region = Region("Menu", player, multiworld)
    progression_region = Region("Progression", player, multiworld)
    dish_region = Region("Dish Checks", player, multiworld)

    # Add regions to the multiworld
    multiworld.regions.extend([menu_region, progression_region, dish_region])

    # Set region connections
    menu_region.connect(progression_region)
    progression_region.connect(dish_region)

    # Ensure dish selection exists
    if not hasattr(multiworld, "selected_dishes"):
        multiworld.selected_dishes = {}

    # Select dishes (ensuring they are stored as **names**)
    dish_count = multiworld.dish[player].value
    all_dish_names = list(dish_dictionary.values())  # Fetch **dish names**
    selected_dishes = random.sample(all_dish_names, min(dish_count, len(all_dish_names)))
    multiworld.selected_dishes[player] = selected_dishes  # Store dish names

    print(f"Selected Dishes: {multiworld.selected_dishes[player]}")

    # Identify unselected **dish names**
    unselected_dishes = set(all_dish_names) - set(selected_dishes)

    # Define excluded dish checks based on **dish names**
    excluded_dish_checks = {
        loc_name for loc_name in DISH_LOCATIONS
        if any(dish_name in loc_name for dish_name in unselected_dishes)
    }

    print(f"Excluded Dish Locations: {excluded_dish_checks}")  # Debugging

    # Register dish locations, excluding unselected dish checks
    for loc_name, loc_id in DISH_LOCATIONS.items():
        if loc_name not in excluded_dish_checks:
            loc = PlateUpLocation(player, loc_name, loc_id, parent=dish_region)
            dish_region.locations.append(loc)

    # Goal-based location exclusion
    excluded_locations = {
        0: [  # Franchise Once
            "Complete First Day After Franchised", "Complete Second Day After Franchised",
            "Complete Third Day After Franchised", "First Star Franchised",
            "Complete Fourth Day After Franchised", "Complete Fifth Day After Franchised",
            "Complete Day 6 After Franchised", "Second Star Franchised",
            "Complete Day 7 After Franchised", "Complete Day 8 After Franchised",
            "Complete Day 9 After Franchised", "Third Star Franchised",
            "Complete Day 10 After Franchised", "Complete Day 11 After Franchised",
            "Complete Day 12 After Franchised", "Fourth Star Franchised",
            "Complete Day 13 After Franchised", "Complete Day 14 After Franchised",
            "Complete Day 15 After Franchised", "Fifth Star Franchised",
            "Complete Day 16 After Franchised", "Complete Day 17 After Franchised",
            "Complete Day 18 After Franchised", "Complete Day 19 After Franchised",
            "Complete Day 20 After Franchised", "Franchise Thrice",
            "Complete First Day After Franchised Twice", "Complete Second Day After Franchised Twice",
            "Complete Third Day After Franchised Twice", "First Star Franchised Twice",
            "Complete Fourth Day After Franchised Twice", "Complete Fifth Day After Franchised Twice",
            "Complete Day 6 After Franchised Twice", "Second Star Franchised Twice",
            "Complete Day 7 After Franchised Twice", "Complete Day 8 After Franchised Twice",
            "Complete Day 9 After Franchised Twice", "Third Star Franchised Twice",
            "Complete Day 10 After Franchised Twice", "Complete Day 11 After Franchised Twice",
            "Complete Day 12 After Franchised Twice", "Fourth Star Franchised Twice",
            "Complete Day 13 After Franchised Twice", "Complete Day 14 After Franchised Twice",
            "Complete Day 15 After Franchised Twice", "Fifth Star Franchised Twice",
            "Complete Day 16 After Franchised Twice", "Complete Day 17 After Franchised Twice",
            "Complete Day 18 After Franchised Twice", "Complete Day 19 After Franchised Twice",
            "Complete Day 20 After Franchised Twice", "Franchise Thrice"
        ],
        1: [  # Franchise Twice
            "Complete First Day After Franchised Twice", "Complete Second Day After Franchised Twice",
            "Complete Third Day After Franchised Twice", "First Star Franchised Twice",
            "Complete Fourth Day After Franchised Twice", "Complete Fifth Day After Franchised Twice",
            "Complete Day 6 After Franchised Twice", "Second Star Franchised Twice",
            "Complete Day 7 After Franchised Twice", "Complete Day 8 After Franchised Twice",
            "Complete Day 9 After Franchised Twice", "Third Star Franchised Twice",
            "Complete Day 10 After Franchised Twice", "Complete Day 11 After Franchised Twice",
            "Complete Day 12 After Franchised Twice", "Fourth Star Franchised Twice",
            "Complete Day 13 After Franchised Twice", "Complete Day 14 After Franchised Twice",
            "Complete Day 15 After Franchised Twice", "Fifth Star Franchised Twice",
            "Complete Day 16 After Franchised Twice", "Complete Day 17 After Franchised Twice",
            "Complete Day 18 After Franchised Twice", "Complete Day 19 After Franchised Twice",
            "Complete Day 20 After Franchised Twice", "Franchise Thrice"
        ],
        2: []  # Franchise Thrice (Exclude nothing)
    }

    goal_value = multiworld.goal[player].value  # Ensure goal_value is set before use

    print(f"DEBUG: Goal Value: {goal_value}")

    excluded_progression_checks = set(excluded_locations.get(goal_value, []))
    print(f"DEBUG: Excluded Progression Locations: {excluded_progression_checks}")

    goal_value = multiworld.goal[player].value
    excluded_progression_checks = set(excluded_locations.get(goal_value, []))

    valid_progression_locations = []

    for loc_name, loc_id in LOCATIONS.items():
        if loc_name not in excluded_progression_checks:
            loc = PlateUpLocation(player, loc_name, loc_id, parent=progression_region)
            progression_region.locations.append(loc)
            valid_progression_locations.append(loc_name)

    multiworld.worlds[player].progression_locations = valid_progression_locations
    print(f"✅ Stored Progression Locations in MultiWorld: {multiworld.worlds[player].progression_locations}")



    print(f"Registered Dish Locations: {[loc.name for loc in dish_region.locations]}")  # Debugging
    print(f"Registered Progression Locations: {[loc.name for loc in progression_region.locations]}")  # Debugging

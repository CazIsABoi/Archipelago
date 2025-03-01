import re
import json
import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification, LocationProgressType
from .Items import ITEMS, PlateUpItem
from .Locations import LOCATIONS, DISH_LOCATIONS, PlateUpLocation, dish_dictionary
from .Options import plateup_options
from .Rules import apply_rules

class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = plateup_options

    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {**LOCATIONS, **DISH_LOCATIONS}

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.progression):
        return PlateUpItem(name, classification, self.item_name_to_id[name], self.player)

    def create_items(self):
        multiworld = self.multiworld
        player = self.player

        # Define excluded progression locations for different goals
        excluded_locations = {
            0: [  # Franchise Once
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

        # Fetch selected goal
        goal_value = multiworld.goal[player].value

        # Retrieve excluded progression checks
        excluded_progression_checks = set(excluded_locations.get(goal_value, []))

        # Retrieve registered dish and progression locations from Regions.py
        dish_region = multiworld.get_region("Dish Checks", player)
        progression_region = multiworld.get_region("Progression", player)

        # Fetch selected dishes
        selected_dishes = set(multiworld.selected_dishes[player])

        # Extract filtered locations that were registered
        available_dish_locations = {
            loc.name: loc for loc in dish_region.locations
            if any(dish in loc.name for dish in selected_dishes)
        }

        available_progression_locations = {
            loc.name: loc for loc in progression_region.locations
        }

        print(f"Filtered Available Dish Locations: {list(available_dish_locations.keys())}")
        print(f"Filtered Available Progression Locations: {list(available_progression_locations.keys())}")

        # Fetch MultiWorld items first
        multiworld_items = list(multiworld.get_items())

        # Generate PlateUp items (excluding Speed Upgrade Player)
        plateup_items = [
            self.create_item(name, classification)
            for name, (item_id, classification) in ITEMS.items()
            if classification != ItemClassification.filler and name != "Speed Upgrade Player"
        ]

        # Ensure exactly 5 copies of "Speed Upgrade Player" are added
        speed_upgrade_item = self.create_item("Speed Upgrade Player", ItemClassification.progression)
        plateup_items.extend([speed_upgrade_item] * 5)

        # Ensure enough items exist to fill all valid locations
        min_items_required = len(available_dish_locations) + len(available_progression_locations)

        while len(multiworld_items) + len(plateup_items) < min_items_required:
            next_item = random.choice(list(ITEMS.keys()))
            if next_item != "Speed Upgrade Player":
                plateup_items.append(self.create_item(next_item, ItemClassification.progression))

        # Combine MultiWorld Items + PlateUp Items
        self.itempool = multiworld_items + plateup_items

        # Shuffle item pool to randomize placement
        random.shuffle(self.itempool)

        # Assign Items to Locations (Only for filtered dish & progression checks)
        all_valid_locations = list(available_progression_locations.values()) + list(available_dish_locations.values())

        for loc, item in zip(all_valid_locations, self.itempool):
            if not loc.item:
                loc.place_locked_item(item)

        print(f"Filled {len(all_valid_locations)} locations with {len(self.itempool)} items.")


    @classmethod
    def get_filler_item_name(cls):
        return "Hob"

    def create_regions(self):
        from .Regions import create_plateup_regions
        create_plateup_regions(self.multiworld, self.player)

        # 🔥 Ensure dish locations are properly registered in the MultiWorld system
        dish_region = self.multiworld.get_region("Dish Checks", self.player)

        for loc_name, loc_id in DISH_LOCATIONS.items():
            if not any(loc.name == loc_name for loc in dish_region.locations):
                loc = PlateUpLocation(self.player, loc_name, loc_id, parent=dish_region)
                dish_region.locations.append(loc)  # ✅ Register dish location

        print(f"Registered {len(dish_region.locations)} dish locations in 'Dish Checks'.")

    def set_rules(self):
        """Set progression rules for PlateUp."""
        multiworld = self.multiworld
        player = self.player

        apply_rules(multiworld, player)  # Call the function from Rules.py



    def fill_slot_data(self):
        goal_value = self.multiworld.goal[self.player].value
        selected_dishes = list(self.multiworld.selected_dishes.get(self.player, []))

        return {
            "goal": goal_value,
            "selected_dishes": json.dumps(selected_dishes)  # Store as a JSON string
        }




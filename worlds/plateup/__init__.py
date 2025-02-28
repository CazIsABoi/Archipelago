import re
import json
import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification, LocationProgressType
from .Items import ITEMS, PlateUpItem
from .Locations import LOCATIONS, DISH_LOCATIONS, PlateUpLocation
from .Options import plateup_options

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

        # 🔥 Fetch Available Locations
        available_progression_locations = {
            loc.name: loc for loc in multiworld.get_reachable_locations(multiworld.state, player)
            if "Progression" in loc.parent_region.name
        }
        available_dish_locations = {
            loc.name: loc for loc in multiworld.get_reachable_locations(multiworld.state, player)
            if "Dish Checks" in loc.parent_region.name
        }

        # 🔥 Ensure only selected dishes are included
        selected_dishes = multiworld.selected_dishes[player]
        filtered_dish_locations = {
            loc_name: loc for loc_name, loc in available_dish_locations.items()
            if any(dish in loc_name for dish in selected_dishes)
        }

        print(f"Progression Locations: {list(available_progression_locations.keys())}")
        print(f"Filtered Dish Locations: {list(filtered_dish_locations.keys())}")

        if not available_progression_locations:
            raise ValueError("No available progression locations found. Check region setup!")

        if not filtered_dish_locations:
            raise ValueError("No valid dish locations found. Check region setup!")

        # 🔥 Fetch All MultiWorld Items First
        multiworld_items = list(multiworld.get_items())

        # 🔥 Generate PlateUp Items (Excluding Speed Upgrade Player)
        plateup_items = [
            self.create_item(name, classification)
            for name, (item_id, classification) in ITEMS.items()
            if classification != ItemClassification.filler and name != "Speed Upgrade Player"
        ]

        # 🔥 Ensure Franchise Progression Locations Have Items
        franchise_locations = [
            "Franchise Once", "Franchise Twice", "Franchise Thrice",
            "Complete First Day After Franchised", "Complete Second Day After Franchised",
            "Complete Third Day After Franchised", "First Star Franchised", "Complete Fourth Day After Franchised",
            "Complete Fifth Day After Franchised", "Complete Day 6 After Franchised", "Second Star Franchised",
            "Complete Day 7 After Franchised", "Complete Day 8 After Franchised", "Complete Day 9 After Franchised",
            "Third Star Franchised", "Complete Day 10 After Franchised", "Complete Day 11 After Franchised",
            "Complete Day 12 After Franchised", "Fourth Star Franchised", "Complete Day 13 After Franchised",
            "Complete Day 14 After Franchised", "Complete Day 15 After Franchised", "Fifth Star Franchised",
            "Complete Day 16 After Franchised", "Complete Day 17 After Franchised", "Complete Day 18 After Franchised",
            "Complete Day 19 After Franchised", "Complete Day 20 After Franchised"
        ]

        for loc_name in franchise_locations:
            if loc_name not in available_progression_locations:
                continue
            loc = available_progression_locations[loc_name]
            item = self.create_item(random.choice(list(ITEMS.keys())), ItemClassification.progression)
            loc.place_locked_item(item)

        # 🔥 Ensure Enough Items Exist
        min_items_required = len(available_progression_locations) + len(filtered_dish_locations)

        while len(multiworld_items) + len(plateup_items) < min_items_required:
            next_item = random.choice(list(ITEMS.keys()))  # Randomly select from PlateUp items
            if next_item != "Speed Upgrade Player":
                plateup_items.append(self.create_item(next_item, ItemClassification.progression))

        # 🔥 Combine MultiWorld Items + PlateUp Items
        self.itempool = multiworld_items + plateup_items

        # 🔥 Shuffle Item Pool to Randomize Placement
        random.shuffle(self.itempool)

        # 🔥 Assign Items to Locations (Only to Valid Dish Checks)
        all_locations = list(available_progression_locations.values()) + list(filtered_dish_locations.values())

        for loc, item in zip(all_locations, self.itempool):
            if not loc.item:
                loc.place_locked_item(item)

        print(f"Filled {len(all_locations)} locations with {len(self.itempool)} items.")









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
        multiworld = self.multiworld
        player = self.player

        # 🔥 Set Completion Goal Based on Player's Selected Goal
        goal_mapping = {
            0: "Franchise Once",
            1: "Franchise Twice",
            2: "Franchise Thrice",
        }
        
        required_location = goal_mapping.get(multiworld.goal[player].value, "Franchise Once")

        multiworld.completion_condition[player] = lambda state: state.can_reach(required_location, "Location", player)

        # 🔥 Ensure Franchise Progression is Reachable
        franchise_order = [
            "Franchise Once", "Complete First Day After Franchised", "Complete Second Day After Franchised",
            "Complete Third Day After Franchised", "First Star Franchised", "Complete Fourth Day After Franchised",
            "Complete Fifth Day After Franchised", "Complete Day 6 After Franchised", "Second Star Franchised",
            "Complete Day 7 After Franchised", "Complete Day 8 After Franchised", "Complete Day 9 After Franchised",
            "Third Star Franchised", "Complete Day 10 After Franchised", "Complete Day 11 After Franchised",
            "Complete Day 12 After Franchised", "Fourth Star Franchised", "Complete Day 13 After Franchised",
            "Complete Day 14 After Franchised", "Complete Day 15 After Franchised", "Fifth Star Franchised",
            "Complete Day 16 After Franchised", "Complete Day 17 After Franchised", "Complete Day 18 After Franchised",
            "Complete Day 19 After Franchised", "Complete Day 20 After Franchised", "Franchise Twice",
            "Complete First Day After Franchised Twice", "Complete Second Day After Franchised Twice",
            "Complete Third Day After Franchised Twice", "First Star Franchised Twice", "Complete Fourth Day After Franchised Twice",
            "Complete Fifth Day After Franchised Twice", "Complete Day 6 After Franchised Twice", "Second Star Franchised Twice",
            "Complete Day 7 After Franchised Twice", "Complete Day 8 After Franchised Twice", "Complete Day 9 After Franchised Twice",
            "Third Star Franchised Twice", "Complete Day 10 After Franchised Twice", "Complete Day 11 After Franchised Twice",
            "Complete Day 12 After Franchised Twice", "Fourth Star Franchised Twice", "Complete Day 13 After Franchised Twice",
            "Complete Day 14 After Franchised Twice", "Complete Day 15 After Franchised Twice", "Fifth Star Franchised Twice",
            "Complete Day 16 After Franchised Twice", "Complete Day 17 After Franchised Twice", "Complete Day 18 After Franchised Twice",
            "Complete Day 19 After Franchised Twice", "Complete Day 20 After Franchised Twice", "Franchise Thrice"
        ]

        for i in range(len(franchise_order) - 1):
            current_location = franchise_order[i]
            next_location = franchise_order[i + 1]
            
            multiworld.get_location(next_location, player).access_rule = lambda state, cur=current_location: state.can_reach(cur, "Location", player)

        print(f"Final Completion Goal: {required_location}")








    def fill_slot_data(self):
        goal_value = self.multiworld.goal[self.player].value
        selected_dishes = list(self.multiworld.selected_dishes.get(self.player, []))

        return {
            "goal": goal_value,
            "selected_dishes": json.dumps(selected_dishes)  # Store as a JSON string
        }




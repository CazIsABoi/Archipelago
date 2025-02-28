import re
import json
import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification, LocationProgressType
from .Items import ITEMS, PlateUpItem
from .Locations import LOCATIONS, PlateUpLocation
from .Options import plateup_options

class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = plateup_options

    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = LOCATIONS

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.progression):
        return PlateUpItem(name, classification, self.item_name_to_id[name], self.player)

    def create_items(self):
        try:
            available_progression_locations = {
                loc.name: loc for loc in self.multiworld.get_reachable_locations(self.multiworld.state, self.player)
                if "Progression" in loc.parent_region.name
            }
            available_dish_locations = {
                loc.name: loc for loc in self.multiworld.get_reachable_locations(self.multiworld.state, self.player)
                if "Dish Checks" in loc.parent_region.name
            }
        except AttributeError as e:
            print(f"Error fetching reachable locations: {e}")
            available_progression_locations = {}
            available_dish_locations = {}

        print(f"Progression Locations: {list(available_progression_locations.keys())}")
        print(f"Dish Locations: {list(available_dish_locations.keys())}")

        if not available_progression_locations:
            raise ValueError("No available progression locations found. Check region setup!")
        
        if not available_dish_locations:
            raise ValueError("No available dish locations found. Check region setup!")

        # Generate item pool while excluding "Speed Upgrade Player"
        self.itempool = [
            self.create_item(name, classification)
            for name, (item_id, classification) in ITEMS.items()
            if name != "Speed Upgrade Player"
        ]

        # Add exactly 5 "Speed Upgrade Player" items
        speed_upgrades = [self.create_item("Speed Upgrade Player", ItemClassification.useful) for _ in range(5)]

        # Ensure at least one Speed Upgrade Player is placed before Day 15 and one before Franchised Day 15
        important_locations = [name for name in available_progression_locations if "Day 15" not in name]
        franchised_locations = [name for name in available_progression_locations if "After Franchised" in name and "Day 15" not in name]

        if important_locations:
            chosen_location = random.choice(important_locations)
            available_progression_locations[chosen_location].place_locked_item(speed_upgrades.pop())

        if franchised_locations:
            chosen_location = random.choice(franchised_locations)
            available_progression_locations[chosen_location].place_locked_item(speed_upgrades.pop())

        # Add remaining Speed Upgrades randomly into the pool
        self.itempool.extend(speed_upgrades)
        random.shuffle(self.itempool)

        # Ensure enough items to fill locations
        all_locations = list(available_progression_locations.values()) + list(available_dish_locations.values())
        while len(self.itempool) < len(all_locations):
            self.itempool.extend(self.itempool)  # Duplicate the item pool if necessary
        self.itempool = self.itempool[:len(all_locations)]  # Trim to match location count

        # Assign items to locations
        for loc, item in zip(all_locations, self.itempool):
            if not loc.item:  # Avoid overwriting pre-placed Speed Upgrade Player
                loc.place_locked_item(item)

        print(f"Filled {len(all_locations)} locations with items.")

    @classmethod
    def get_filler_item_name(cls):
        return "Hob"

    def create_regions(self):
        from .Regions import create_plateup_regions
        create_plateup_regions(self.multiworld, self.player)

    def set_rules(self):
        goal = self.multiworld.goal[self.player].value
        if goal == "Franchise":
            location_id = 200000
        elif goal == "Franchise Twice":
            location_id = 300000
        else:
            location_id = 400000

        self.multiworld.completion_condition[self.player] = lambda state: any(
            (loc.address == location_id) for loc in state.locations_checked
        )

    def fill_slot_data(self):
        goal_value = self.multiworld.goal[self.player].value
        selected_dishes = list(self.multiworld.selected_dishes.get(self.player, []))

        return {
            "goal": goal_value,
            "selected_dishes": json.dumps(selected_dishes)  # Store as a JSON string
        }




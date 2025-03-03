import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification
from .Items import ITEMS, PlateUpItem
from .Locations import LOCATIONS, DISH_LOCATIONS
from .Options import plateup_options
from .Rules import apply_rules

class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = plateup_options

    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {**LOCATIONS, **DISH_LOCATIONS}

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.progression) -> PlateUpItem:
        """Create a PlateUp item with the given classification."""
        return PlateUpItem(name, classification, self.item_name_to_id[name], self.player)

    def create_items(self):
        """
        Populates the item pool with PlateUp items.
        Ensures items are generated and included in the MultiWorld fill process.
        """
        multiworld = self.multiworld
        player = self.player

        # Ensure locations are properly filtered and initialized
        if not hasattr(multiworld.worlds[player], "progression_locations"):
            multiworld.worlds[player].progression_locations = []

        if not hasattr(multiworld.worlds[player], "valid_dish_locations"):
            from .Rules import filter_selected_dishes
            filter_selected_dishes(multiworld, player)  # Run dish filtering

        # Fetch the actual locations **after filtering**
        valid_dish_locations = multiworld.worlds[player].valid_dish_locations
        progression_locations = multiworld.worlds[player].progression_locations

        # Total number of locations to be filled
        total_locations = len(valid_dish_locations) + len(progression_locations)

        # Initialize item pool
        item_pool = []

        # Add all PlateUp items **except** "Speed Upgrade Player"
        plateup_items = [self.create_item(item_name) for item_name in self.item_name_to_id if item_name != "Speed Upgrade Player"]
        item_pool.extend(plateup_items)

        # Add exactly 5 "Speed Upgrade Player" items
        item_pool += [self.create_item("Speed Upgrade Player") for _ in range(5)]

        # **Ensure the number of items matches the number of locations**
        existing_items = len(item_pool)
        items_needed = total_locations - existing_items  # Difference between locations and items

        # If there are more locations than items, cycle through the item table repeatedly until all locations are filled
        if items_needed > 0:
            item_list = [name for name in self.item_name_to_id if name != "Speed Upgrade Player"]
            item_index = 0
            while len(item_pool) < total_locations:
                item_pool.append(self.create_item(item_list[item_index % len(item_list)]))
                item_index += 1

        # Assign the filled item pool to the MultiWorld
        self.multiworld.itempool += item_pool

        # Debugging output
        print(f"PlateUp items added: {len(item_pool)} (Target: {total_locations})")
        print(f"Total locations to fill: {total_locations}")
        print(f"Valid Dish Locations Count: {len(valid_dish_locations)}")
        print(f"Progression Locations Count: {len(progression_locations)}")

    def create_regions(self):
        from .Regions import create_plateup_regions
        create_plateup_regions(self.multiworld, self.player)

    def set_rules(self):
        """Set progression rules for PlateUp."""
        apply_rules(self.multiworld, self.player)

    def fill_slot_data(self):
        goal_value = self.multiworld.goal[self.player].value
        selected_dishes = list(self.multiworld.selected_dishes.get(self.player, []))

        return {
            "goal": goal_value,
            "selected_dishes": selected_dishes
        }

    def get_filler_item_name(self):
        return "Hob"
import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification
from .Items import ITEMS, PlateUpItem, FILLER_ITEMS
from .Locations import LOCATIONS, DISH_LOCATIONS
from .Options import PlateUpOptions

from .Rules import apply_rules

class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = PlateUpOptions

    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {**LOCATIONS, **DISH_LOCATIONS}

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> PlateUpItem:
        """Create a PlateUp item, properly handling filler items."""
        
        # Check if item exists in regular ITEMS list
        if name in self.item_name_to_id:
            item_id = self.item_name_to_id[name]
        # Otherwise, check the FILLER_ITEMS list
        elif name in FILLER_ITEMS:
            item_id = FILLER_ITEMS[name][0]
        else:
            raise ValueError(f"Item '{name}' not found in ITEMS or FILLER_ITEMS!")

        return PlateUpItem(name, classification, item_id, self.player)



    def create_items(self):
        """
        Populates the item pool with PlateUp items.
        Ensures items are generated and included in the MultiWorld fill process.
        """
        multiworld = self.multiworld
        player = self.player

        print(f"DEBUG: Available Players in MultiWorld: {list(multiworld.worlds.keys())}")
        print(f"DEBUG: Trying to access Player {player}")
        if player not in multiworld.worlds:
            print(f"🚨 ERROR: Player {player} does not exist in MultiWorld!")


        # Ensure locations are properly filtered and initialized
        if not hasattr(multiworld.worlds[player], "progression_locations"):
            multiworld.worlds[player].progression_locations = []

        if not hasattr(multiworld.worlds[player], "valid_dish_locations"):
            from .Rules import filter_selected_dishes
            filter_selected_dishes(multiworld, player)  # Run dish filtering

        # Fetch the actual locations **after filtering**
        valid_dish_locations = multiworld.worlds[player].valid_dish_locations
        if hasattr(multiworld.worlds[player], "progression_locations"):
            progression_locations = multiworld.worlds[player].progression_locations
            print(f"Loaded Progression Locations for Player {player}: {progression_locations}")
        else:
            print(f"ERROR: Progression locations were not set in `Regions.py` for Player {player}! Using empty list.")
            progression_locations = []


        print(f"DEBUG: Checking dish locations BEFORE item generation...")
        print(f"valid_dish_locations Count: {len(valid_dish_locations)}")
        print(f"valid_dish_locations List: {valid_dish_locations}")
        print(f"progression_locations Count: {len(progression_locations)}")
        print(f"progression_locations List: {progression_locations}")

        # Total number of locations to be filled
        total_locations = len(valid_dish_locations) + len(progression_locations)

        # Initialize item pool
        item_pool = []

        # Add all PlateUp items **except** "Speed Upgrade Player"
        plateup_items = [
            self.create_item(item_name) for item_name in self.item_name_to_id
            if item_name != "Speed Upgrade Player"
        ][:total_locations]  # Ensure we don’t overfill before filler step
        item_pool.extend(plateup_items)

        # Add exactly 5 "Speed Upgrade Player" items
        item_pool += [self.create_item("Speed Upgrade Player") for _ in range(5)]

        # Debugging: Check if the total locations were detected correctly
        print(f"Total Locations Detected: {total_locations}")
        print(f"Initial Item Count: {len(item_pool)}")

        # **Ensure the number of items matches the number of locations**
        existing_items = len(item_pool)
        items_needed = total_locations - existing_items  # Difference between locations and items

        print(f"Items Needed: {items_needed}")

        # If there are more locations than items, cycle through the item table repeatedly
        if items_needed > 0:
            item_list = [name for name in self.item_name_to_id if name != "Speed Upgrade Player"]
            item_index = 0
            while len(item_pool) < total_locations and item_list:
                item_pool.append(self.create_item(item_list[item_index % len(item_list)]))
                item_index += 1

        # Debugging: Check if we're still missing items after cycling
        print(f"Item Count After Cycling: {len(item_pool)}")

        # If we still don't have enough items, enforce filler items
        filler_items_needed = total_locations - len(item_pool)
        if filler_items_needed > 0:
            print(f"🚨 Adding {filler_items_needed} filler items to reach {total_locations} total.")
            filler_list = list(FILLER_ITEMS.keys())

            for i in range(filler_items_needed):
                filler_name = filler_list[i % len(filler_list)]
                print(f"Adding filler item: {filler_name}")  # Debugging Output
                item_pool.append(self.create_item(filler_name, ItemClassification.filler))
        print(f"Filler Items Needed: {filler_items_needed}")

        if filler_items_needed > 0:
            print(f"Adding {filler_items_needed} filler items...")
            filler_list = list(FILLER_ITEMS.keys())

            for i in range(filler_items_needed):
                filler_name = filler_list[i % len(filler_list)]
                print(f"Adding filler item: {filler_name}")  # Debugging Output
                item_pool.append(self.create_item(filler_name, ItemClassification.filler))

        print(f"Final Item Count After Fillers: {len(item_pool)}")

        # Debugging: Check the final item count
        print(f"Final Item Count: {len(item_pool)}")
        print(f"Filler Items Used: {max(0, len(item_pool) - existing_items)}")

        # Assign the filled item pool to the MultiWorld
        self.multiworld.itempool += item_pool


    def create_regions(self):
        from .Regions import create_plateup_regions
        create_plateup_regions(self.multiworld, self.player)

    def set_rules(self):
        """Set progression rules for PlateUp."""
        apply_rules(self.multiworld, self.player)

    def fill_slot_data(self):
        goal_value = self.multiworld.goal[self.player].value
        selected_dishes = list(self.multiworld.selected_dishes.get(self.player, []))

        # Fetch DeathLink settings
        death_link_enabled = self.multiworld.death_link[self.player].value
        death_link_behavior = self.multiworld.death_link_behavior[self.player].value

        return {
            "goal": goal_value,
            "selected_dishes": selected_dishes,
            "death_link": death_link_enabled,  # Store if DeathLink is enabled (0 or 1)
            "death_link_behavior": death_link_behavior  # Store selected DeathLink behavior
        }

    def get_filler_item_name(self):
        return "Hob"
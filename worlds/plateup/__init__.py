import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification
from .Items import ITEMS, PlateUpItem, FILLER_ITEMS
from .Locations import LOCATIONS, DISH_LOCATIONS
from .Options import PlateUpOptions


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
        Populates the item pool with PlateUp items for each player independently.
        Ensures items are generated per-player and included in the MultiWorld fill process.
        """
        multiworld = self.multiworld
        player = self.player

        # Ensure locations are properly initialized (should already be set in create_plateup_regions)
        valid_dish_locations = getattr(multiworld.worlds[player], "valid_dish_locations", [])
        progression_locations = getattr(multiworld.worlds[player], "progression_locations", [])

        # Total number of locations to be filled per player
        total_locations = len(valid_dish_locations) + len(progression_locations)
        if total_locations == 0:
            print(f"⚠ Player {player} has no valid locations to place items!")
            return  # No locations, no items needed.

        # Initialize item pool per player
        item_pool = []

        # Add all PlateUp items **except** "Speed Upgrade Player"
        plateup_items = [
            self.create_item(item_name) for item_name in self.item_name_to_id
            if item_name != "Speed Upgrade Player"
        ][:total_locations]  # Prevent overfilling
        item_pool.extend(plateup_items)

        # Add exactly 5 "Speed Upgrade Player" items per player
        speed_upgrade_count = 5
        for _ in range(speed_upgrade_count):
            item = self.create_item("Speed Upgrade Player")
            item_pool.append(item)
            print(f"DEBUG: Added Speed Upgrade Player for Player {player}")

        # Debugging: Initial check on item counts
        print(f"Player {player} - Total Locations Detected: {total_locations}")
        print(f"Player {player} - Initial Item Count: {len(item_pool)}")

        # Ensure the number of items matches the number of locations
        existing_items = len(item_pool)
        items_needed = total_locations - existing_items

        # If there are more locations than items, cycle through available items
        if items_needed > 0:
            item_list = [name for name in self.item_name_to_id if name != "Speed Upgrade Player"]
            for _ in range(items_needed):
                item_pool.append(self.create_item(item_list[_ % len(item_list)]))  # Rotates through item list

        print(f"Player {player} - Item Count After Cycling: {len(item_pool)}")

        # If we still don't have enough items, enforce filler items
        filler_items_needed = total_locations - len(item_pool)
        if filler_items_needed > 0:
            print(f"Player {player} - Adding {filler_items_needed} filler items to reach {total_locations} total.")
            filler_list = list(FILLER_ITEMS.keys())
            for i in range(filler_items_needed):
                filler_name = filler_list[i % len(filler_list)]
                item_pool.append(self.create_item(filler_name, ItemClassification.filler))

        # Final debugging check
        print(f"Player {player} - Final Item Count: {len(item_pool)}")
        print(f"Player {player} - Filler Items Used: {max(0, len(item_pool) - existing_items)}")

        # Assign the filled item pool only for this player
        multiworld.itempool += item_pool

    def create_regions(self):
        from .Regions import create_plateup_regions
        create_plateup_regions(self.multiworld, self.player)

    def set_rules(self):
        """Applies access rules for PlateUp to ensure progression works correctly per player."""
        multiworld = self.multiworld
        player = self.player

        # Ensure valid_dish_locations is set before applying rules
        if not hasattr(multiworld.worlds[player], "valid_dish_locations"):
            from .Rules import filter_selected_dishes
            print(f"⚠ `valid_dish_locations` missing for Player {player}, running `filter_selected_dishes()` now...")
            filter_selected_dishes(multiworld, player)

        # Ensure progression locations are initialized
        if not hasattr(multiworld.worlds[player], "progression_locations"):
            multiworld.worlds[player].progression_locations = []

        from .Rules import apply_rules
        apply_rules(multiworld, player)

    def fill_slot_data(self):
        player = self.player  # Ensure we're using the correct player ID

        if player not in self.multiworld.selected_dishes:
            print(f"⚠ Warning: `selected_dishes` missing for Player {player}. Using empty list.")
            self.multiworld.selected_dishes[player] = []

        return {
            "goal": self.multiworld.goal[player].value,
            "selected_dishes": list(self.multiworld.selected_dishes[player]),
            "death_link": self.multiworld.death_link[player].value,
            "death_link_behavior": self.multiworld.death_link_behavior[player].value,
            "items_kept": self.multiworld.appliances_kept[player].value
        }

    def get_filler_item_name(self):
        return "Hob"
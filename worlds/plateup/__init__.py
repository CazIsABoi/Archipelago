import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification
from .Items import ITEMS, PlateUpItem, FILLER_ITEMS
from .Locations import DISH_LOCATIONS, FRANCHISE_LOCATION_DICT, DAY_LOCATION_DICT, EXCLUDED_LOCATIONS
from .Options import PlateUpOptions
from .Rules import filter_selected_dishes, apply_rules


class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = PlateUpOptions

    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {
        **FRANCHISE_LOCATION_DICT,
        **DAY_LOCATION_DICT,
        **DISH_LOCATIONS
    }

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> PlateUpItem:
        if name in self.item_name_to_id:
            item_id = self.item_name_to_id[name]
        elif name in FILLER_ITEMS:
            item_id = FILLER_ITEMS[name][0]
        else:
            raise ValueError(f"Item '{name}' not found in ITEMS or FILLER_ITEMS!")

        return PlateUpItem(name, classification, item_id, self.player)

    def create_items(self):
        multiworld = self.multiworld
        player = self.player

        valid_dish_locations = getattr(multiworld.worlds[player], "valid_dish_locations", [])
        progression_locations = getattr(multiworld.worlds[player], "progression_locations", [])
        total_locations = len(valid_dish_locations) + len(progression_locations)
        if total_locations == 0:
            print(f"Player {player} has no valid locations to place items!")
            return

        item_pool = []

        normal_item_names = [
            name for name in self.item_name_to_id
            if name != "Speed Upgrade Player"
        ]
        sliced_normal_items = normal_item_names[:total_locations]

        for item_name in sliced_normal_items:
            item_pool.append(self.create_item(item_name))

        speed_mode = multiworld.appliance_speed_mode[player].value
        for _ in range(5):
            item_pool.append(self.create_item("Speed Upgrade Player", classification=ItemClassification.progression))

        if speed_mode == 0:
            for _ in range(5):
                item_pool.append(self.create_item("Speed Upgrade Appliance", classification=ItemClassification.progression))
        else:
            for _ in range(5):
                item_pool.append(self.create_item("Speed Upgrade Cook", classification=ItemClassification.progression))
            for _ in range(5):
                item_pool.append(self.create_item("Speed Upgrade Clean", classification=ItemClassification.progression))
            for _ in range(5):
                item_pool.append(self.create_item("Speed Upgrade Chop", classification=ItemClassification.progression))

        for _ in range(3):
            item_pool.append(self.create_item("Random Customer Card", classification=ItemClassification.trap))

        existing_count = len(item_pool)
        items_needed = total_locations - existing_count
        if items_needed > 0:
            i = 0
            while len(item_pool) < total_locations:
                pick_name = normal_item_names[i % len(normal_item_names)]
                item_pool.append(self.create_item(pick_name))
                i += 1

        filler_items_needed = total_locations - len(item_pool)
        if filler_items_needed > 0:
            for _ in range(filler_items_needed):
                filler_name = self.get_filler_item_name()
                item_pool.append(self.create_item(filler_name, ItemClassification.filler))

        multiworld.itempool += item_pool

    def create_regions(self):
        from .Regions import create_plateup_regions
        create_plateup_regions(self.multiworld, self.player)

    def set_rules(self):
        multiworld = self.multiworld
        player = self.player

        if not hasattr(multiworld.worlds[player], "valid_dish_locations"):
            filter_selected_dishes(multiworld, player)
        if not hasattr(multiworld.worlds[player], "progression_locations"):
            multiworld.worlds[player].progression_locations = []

        user_goal = multiworld.goal[player].value
        if user_goal == 0:
            required = multiworld.franchise_count[player].value
            for i in range(required + 1, 11):
                name = f"Franchise {i} times"
                if name in FRANCHISE_LOCATION_DICT:
                    loc_id = FRANCHISE_LOCATION_DICT[name]
                    EXCLUDED_LOCATIONS.add(loc_id)

        apply_rules(multiworld, player)

    def fill_slot_data(self):
        player = self.player

        if player not in self.multiworld.selected_dishes:
            print(f"Warning: `selected_dishes` missing for Player {player}. Using empty list.")
            self.multiworld.selected_dishes[player] = []

        return {
            "goal": self.multiworld.goal[player].value,
            "franchise_count": self.multiworld.franchise_count[player].value if hasattr(self.multiworld, "franchise_count") else 1,
            "day_count": self.multiworld.day_count[player].value if hasattr(self.multiworld, "day_count") else 1,
            "selected_dishes": list(self.multiworld.selected_dishes[player]),
            "death_link": self.multiworld.death_link[player].value,
            "death_link_behavior": self.multiworld.death_link_behavior[player].value,
            "items_kept": self.multiworld.appliances_kept[player].value,
            "appliance_speed_mode": self.multiworld.appliance_speed_mode[player].value
        }

    def get_filler_item_name(self):
        return "Hob"

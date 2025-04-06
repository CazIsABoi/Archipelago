from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification, CollectionState
from .Items import ITEMS, PlateUpItem
from .Locations import DISH_LOCATIONS, FRANCHISE_LOCATION_DICT, DAY_LOCATION_DICT, EXCLUDED_LOCATIONS
from .Options import PlateUpOptions
from .Rules import filter_selected_dishes, apply_rules
from collections import Counter
import math


class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = PlateUpOptions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.excluded_locations = set()

    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {**FRANCHISE_LOCATION_DICT, **DAY_LOCATION_DICT, **DISH_LOCATIONS}

    def generate_location_table(self):
        goal = self.multiworld.goal[self.player].value
        if goal == 0:
            locs = {**FRANCHISE_LOCATION_DICT}
        else:
            locs = {**DAY_LOCATION_DICT}
        locs.update(DISH_LOCATIONS)
        return locs
    
    def validate_ids(self):
        item_ids = list(self.item_name_to_id.values())
        dupe_items = [item for item, count in Counter(item_ids).items() if count > 1]
        if dupe_items:
            raise Exception(f"Duplicate item IDs found: {dupe_items}")

        loc_ids = list(self.location_name_to_id.values())
        dupe_locs = [loc for loc, count in Counter(loc_ids).items() if count > 1]
        if dupe_locs:
            raise Exception(f"Duplicate location IDs found: {dupe_locs}")
    
    def create_regions(self):
        from .Regions import create_plateup_regions
        self._location_name_to_id = self.generate_location_table()
        self.validate_ids()
        create_plateup_regions(self.multiworld, self.player)

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> PlateUpItem:
        if name in self.item_name_to_id:
            item_id = self.item_name_to_id[name]
        else:
            raise ValueError(f"Item '{name}' not found in ITEMS")
        return PlateUpItem(name, classification, item_id, self.player)

    def create_items(self):
        multiworld = self.multiworld
        player = self.player

        # Use the planned location table count instead of the currently created locations
        total_locations = len(self.generate_location_table())
        item_pool = []

        # Add progression items
        item_pool.extend([
            self.create_item("Speed Upgrade Player", classification=ItemClassification.progression)
            for _ in range(5)
        ])

        speed_mode = multiworld.appliance_speed_mode[player].value
        if speed_mode == 0:
            item_pool.extend([
                self.create_item("Speed Upgrade Appliance", classification=ItemClassification.progression)
                for _ in range(5)
            ])
        else:
            item_pool.extend([
                self.create_item("Speed Upgrade Cook", classification=ItemClassification.progression),
                self.create_item("Speed Upgrade Clean", classification=ItemClassification.progression),
                self.create_item("Speed Upgrade Chop", classification=ItemClassification.progression)
            ] * 5)

        # Determine total required days based on the goal
        if multiworld.goal[player].value == 0:
            total_days = 15 * multiworld.franchise_count[player].value
        else:
            total_days = multiworld.day_count[player].value

        lease_count = math.ceil(total_days / 3)
        item_pool.extend([
            self.create_item("Day Lease", classification=ItemClassification.progression)
            for _ in range(lease_count)
        ])

        # Add traps
        item_pool.extend([
            self.create_item("Random Customer Card", classification=ItemClassification.trap)
            for _ in range(3)
        ])

        # Fill remaining space with filler items
        while len(item_pool) < total_locations:
            filler_name = self.get_filler_item_name()
            item_pool.append(self.create_item(filler_name))

        print(f"[Player {player}] Total item pool count: {len(item_pool)}")
        print(f"[Player {player}] Total locations: {total_locations}")
        self.multiworld.itempool += item_pool


    def set_rules(self):
        multiworld = self.multiworld
        player = self.player

        if not hasattr(multiworld.worlds[player], "valid_dish_locations"):
            filter_selected_dishes(multiworld, player)
        if not hasattr(multiworld.worlds[player], "progression_locations"):
            multiworld.worlds[player].progression_locations = []

        # Set up dish progression chaining
        from .Rules import restrict_locations_by_progression
        restrict_locations_by_progression(multiworld, player)

        # Add selected dish locations to the Dish Checks region
        plateup_world = multiworld.worlds[player]
        if hasattr(plateup_world, "valid_dish_locations"):
            from .Locations import DISH_LOCATIONS, PlateUpLocation
            dish_region = None
            for region in multiworld.regions:
                if region.name == "Dish Checks" and region.player == player:
                    dish_region = region
                    break
            if dish_region:
                for loc_name in plateup_world.valid_dish_locations:
                    # Only add if not already present
                    if not any(loc.name == loc_name for loc in dish_region.locations):
                        loc_id = DISH_LOCATIONS.get(loc_name)
                        if loc_id:
                            loc = PlateUpLocation(player, loc_name, loc_id, parent=dish_region)
                            dish_region.locations.append(loc)

        user_goal = multiworld.goal[player].value
        if user_goal == 0:
            required = multiworld.franchise_count[player].value
            for i in range(required + 1, 11):
                name = f"Franchise {i} times"
                if name in FRANCHISE_LOCATION_DICT:
                    loc_id = FRANCHISE_LOCATION_DICT[name]
                    EXCLUDED_LOCATIONS.add(loc_id)

        def plateup_completion(state: CollectionState):
            goal = self.multiworld.goal[self.player].value
            if goal == 0:
                count = self.multiworld.franchise_count[self.player].value
                loc_name = f"Franchise {count} times"
            else:
                count = self.multiworld.day_count[self.player].value
                loc_name = f"Complete Day {count}"
            return state.can_reach(loc_name, "Location", self.player)

        self.multiworld.completion_condition[self.player] = plateup_completion
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
        filler_candidates = [name for name, (code, classification) in ITEMS.items()
                             if classification == ItemClassification.filler]
        if not filler_candidates:
            raise Exception("No filler items available in ITEMS.")
        return self.multiworld.random.choice(filler_candidates)

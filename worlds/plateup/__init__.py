from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification, CollectionState
from .Items import ITEMS, PlateUpItem
from .Locations import DISH_LOCATIONS, FRANCHISE_LOCATION_DICT, DAY_LOCATION_DICT, EXCLUDED_LOCATIONS
from .Options import PlateUpOptions
from .Rules import (
    filter_selected_dishes,
    apply_rules,
    restrict_locations_by_progression
)
from collections import Counter
import math


class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = PlateUpOptions

    # Pre-calculate mappings for items and locations.
    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {**FRANCHISE_LOCATION_DICT, **DAY_LOCATION_DICT, **DISH_LOCATIONS}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.excluded_locations = set()

    def generate_location_table(self):
        """Return a planned location table based on the goal and options."""
        goal = self.multiworld.goal[self.player].value
        if goal == 0:
            # Franchise goal: include only franchise locations up to the required count.
            required = self.multiworld.franchise_count[self.player].value
            max_franchise_id = (required + 1) * 100000
            locs = {
                name: loc
                for name, loc in FRANCHISE_LOCATION_DICT.items()
                if loc < max_franchise_id or name == f"Franchise {required} times"
            }
            return locs
        else:
            required_days = self.multiworld.day_count[self.player].value
            max_stars = math.ceil(required_days / 3)
            locs = {}
            for name, loc in DAY_LOCATION_DICT.items():
                if name.startswith("Complete Day "):
                    day = int(name.removeprefix("Complete Day ").strip())
                    if day <= required_days:
                        locs[name] = loc
                elif name.startswith("Complete Star "):
                    star = int(name.removeprefix("Complete Star ").strip())
                    if star <= max_stars:
                        locs[name] = loc
            locs.update(DISH_LOCATIONS)
            return locs

    def validate_ids(self):
        """Ensure that item and location IDs are unique."""
        item_ids = list(self.item_name_to_id.values())
        dupe_items = [item for item, count in Counter(item_ids).items() if count > 1]
        if dupe_items:
            raise Exception(f"Duplicate item IDs found: {dupe_items}")

        loc_ids = list(self.location_name_to_id.values())
        dupe_locs = [loc for loc, count in Counter(loc_ids).items() if count > 1]
        if dupe_locs:
            raise Exception(f"Duplicate location IDs found: {dupe_locs}")

    def create_regions(self):
        """Create regions using the planned location table."""
        from .Regions import create_plateup_regions
        self._location_name_to_id = self.generate_location_table()
        self.validate_ids()
        create_plateup_regions(self.multiworld, self.player)

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> PlateUpItem:
        """Create a PlateUp item from the given name."""
        if name in self.item_name_to_id:
            item_id = self.item_name_to_id[name]
        else:
            raise ValueError(f"Item '{name}' not found in ITEMS")
        return PlateUpItem(name, classification, item_id, self.player)

    def create_items(self):
        """Create the initial item pool based on the planned location table."""
        multiworld = self.multiworld
        player = self.player

        total_locations = len(self.generate_location_table())
        item_pool = []

        # Add progression items.
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

        if multiworld.goal[player].value == 0:
            total_days = 15 * multiworld.franchise_count[player].value
        else:
            total_days = multiworld.day_count[player].value
        lease_count = math.ceil(total_days / 3)
        item_pool.extend([
            self.create_item("Day Lease", classification=ItemClassification.progression)
            for _ in range(lease_count)
        ])

        item_pool.extend([
            self.create_item("Random Customer Card", classification=ItemClassification.trap)
            for _ in range(3)
        ])

        while len(item_pool) < total_locations:
            filler_name = self.get_filler_item_name()
            item_pool.append(self.create_item(filler_name))

        print(f"[Player {player}] Total item pool count: {len(item_pool)}")
        print(f"[Player {player}] Total locations: {total_locations}")
        self.multiworld.itempool += item_pool

    def set_rules(self):
        """Set progression rules and top-up the item pool based on final locations."""
        multiworld = self.multiworld
        player = self.player

        if not hasattr(multiworld.worlds[player], "valid_dish_locations"):
            filter_selected_dishes(multiworld, player)
        if not hasattr(multiworld.worlds[player], "progression_locations"):
            multiworld.worlds[player].progression_locations = []

        restrict_locations_by_progression(multiworld, player)

        from .Locations import DISH_LOCATIONS, PlateUpLocation
        plateup_world = multiworld.worlds[player]
        dish_region = next(
            (r for r in multiworld.regions if r.name == "Dish Checks" and r.player == player),
            None
        )
        if dish_region:
            for loc_name in plateup_world.valid_dish_locations:
                if not any(loc.name == loc_name for loc in dish_region.locations):
                    loc_id = DISH_LOCATIONS.get(loc_name)
                    if loc_id:
                        loc = PlateUpLocation(player, loc_name, loc_id, parent=dish_region)
                        dish_region.locations.append(loc)

        if multiworld.goal[player].value == 0:
            required = multiworld.franchise_count[player].value
            for i in range(required + 1, 11):
                name = f"Franchise {i} times"
                if name in FRANCHISE_LOCATION_DICT:
                    EXCLUDED_LOCATIONS.add(FRANCHISE_LOCATION_DICT[name])

        def plateup_completion(state: CollectionState):
            if multiworld.goal[player].value == 0:
                count = multiworld.franchise_count[player].value
                loc_name = f"Franchise {count} times"
            else:
                count = multiworld.day_count[player].value
                loc_name = f"Complete Day {count}"
            return state.can_reach(loc_name, "Location", player)

        multiworld.completion_condition[player] = plateup_completion
        apply_rules(multiworld, player)

        final_locations = [loc for loc in multiworld.get_locations() if loc.player == player]
        current_items = [item for item in multiworld.itempool if item.player == player]
        missing = len(final_locations) - len(current_items)
        if missing > 0:
            print(f"[Player {player}] Item pool is short by {missing} items. Adding filler items.")
            for _ in range(missing):
                filler_name = self.get_filler_item_name()
                multiworld.itempool.append(self.create_item(filler_name))

    def fill_slot_data(self):
        """Return slot data for this player."""
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
        """Randomly select a filler item from the available candidates."""
        filler_candidates = [
            name for name, (code, classification) in ITEMS.items()
            if classification == ItemClassification.filler
        ]
        if not filler_candidates:
            raise Exception("No filler items available in ITEMS.")
        return self.multiworld.random.choice(filler_candidates)

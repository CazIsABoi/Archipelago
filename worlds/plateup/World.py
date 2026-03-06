import logging
import math
from collections import Counter

from BaseClasses import ItemClassification, CollectionState, LocationProgressType
from worlds.AutoWorld import World
from . import Web_World
from .Items import ITEMS, PlateUpItem, appliance_unlock_dictionary, APPLIANCE_PROGRESSION
from .Locations import (
    DISH_LOCATIONS,
    FRANCHISE_LOCATION_DICT,
    DAY_LOCATION_DICT,
    EXCLUDED_LOCATIONS,
    SETTING_LOCATIONS,
    BASE_SETTING_NAME,
    OPTIONAL_SETTING_DISPLAY,
)
from .Options import PlateUpOptions, Goal, SettingCheckMode
from .Rules import (
    filter_selected_dishes,
    filter_selected_settings,
    apply_rules,
    restrict_locations_by_progression
)


class PlateUpWorld(World):
    game = "plateup"
    web = Web_World.PlateUpWebWorld()
    options_dataclass = PlateUpOptions
    options: PlateUpOptions

    # Pre-calculate mappings for items and locations.
    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {
        **FRANCHISE_LOCATION_DICT,
        **DAY_LOCATION_DICT,
        **DISH_LOCATIONS,
        **SETTING_LOCATIONS,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.excluded_locations = set()
        # Initialize attributes to avoid hasattr checks
        self.selected_dishes = []
        self.starting_dish = None
        self.valid_dish_locations = []
        self.selected_settings = []
        self.valid_setting_locations = []

    def generate_early(self):
        """Validate option combinations before generation begins."""
        if self.options.goal.value == Goal.option_reach_day_x_with_dishes:
            dish_count = self.options.dish.value
            dish_goal = self.options.dish_goal_count.value
            if dish_count == 0:
                raise Exception(
                    f"[{self.multiworld.player_name[self.player]}] "
                    "'dish' must be at least 1 when using goal 'reach_day_x_with_dishes'."
                )
            if dish_goal > dish_count:
                raise Exception(
                    f"[{self.multiworld.player_name[self.player]}] "
                    f"'dish_goal_count' ({dish_goal}) cannot exceed 'dish' ({dish_count}). "
                    "Lower dish_goal_count or raise the dish count."
                )

    def generate_location_table(self):
        """Plan locations based on goal/options and selected dishes."""
        self.set_selected_settings()
        goal = self.options.goal.value
        dish_count = self.options.dish.value
        if goal == 0:
            # Franchise goal: include per-run day/star locations up to required,
            # plus milestone locations up to required.
            required = self.options.franchise_count.value
            locs = {}

            def run_index_from_name(n: str):
                if not n.startswith("Franchise - "):
                    return None
                # Run 0 has no " After Franchised" suffix.
                if " After Franchised" not in n:
                    return 0
                # Extract suffix part
                suffix_part = n.split(" After Franchised", 1)[1]
                if suffix_part == "":
                    return 1  # exactly " After Franchised" => run 1
                suffix_part = suffix_part.strip()
                if suffix_part.isdigit():
                    return int(suffix_part)
                return None

            for name, loc in FRANCHISE_LOCATION_DICT.items():
                if name.startswith("Franchise ") and name.endswith(" times"):
                    # Milestone: include only up to required
                    try:
                        count = int(name.removeprefix("Franchise ").removesuffix(" times"))
                        if count <= required:
                            locs[name] = loc
                    except ValueError:
                        pass
                else:
                    run_idx = run_index_from_name(name)
                    if run_idx is not None and (run_idx + 1) <= required:
                        # Exclude post-day-15 checks (Day 16–20) from progression locations.
                        if "Complete Day " in name:
                            try:
                                day_str = name.split("Complete Day ", 1)[1].split(" ")[0].strip()
                                # day_str should be a number for days >=6; if it isn't, keep it
                                if day_str.isdigit() and int(day_str) > 15:
                                    continue
                            except Exception:
                                pass
                        locs[name] = loc
            # Include selected dish day locations as non-progression checks
            if dish_count > 0:
                if not self.selected_dishes or len(self.selected_dishes) != dish_count:
                    self.set_selected_dishes()
                for dish in self.selected_dishes:
                    for day in range(1, 15 + 1):
                        loc_name = f"{dish} - Day {day}"
                        loc_id = DISH_LOCATIONS.get(loc_name)
                        if loc_id:
                            locs[loc_name] = loc_id
        elif goal == 1:
            required_days = self.options.day_count.value
            # Must match Regions star creation logic (floor)
            max_stars = required_days // 3
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
            # Add dish locations when enabled; only those in selected_dishes
            if dish_count > 0:
                if not self.selected_dishes or len(self.selected_dishes) != dish_count:
                    self.set_selected_dishes()
                for dish in self.selected_dishes:
                    for day in range(1, 15 + 1):
                        loc_name = f"{dish} - Day {day}"
                        loc_id = DISH_LOCATIONS.get(loc_name)
                        if loc_id:
                            locs[loc_name] = loc_id
        else:  # goal == 2: reach Day X with Z dishes
            required_days = self.options.day_target.value
            max_stars = required_days // 3
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
            # Dish checks go up to day_target (not capped at 15) so there is
            # content to check off on every run until the goal day is reached.
            if dish_count > 0:
                if not self.selected_dishes or len(self.selected_dishes) != dish_count:
                    self.set_selected_dishes()
                for dish in self.selected_dishes:
                    for day in range(1, required_days + 1):
                        loc_name = f"{dish} - Day {day}"
                        loc_id = DISH_LOCATIONS.get(loc_name)
                        if loc_id:
                            locs[loc_name] = loc_id
        if self.options.setting_checks.value:
            if not self.selected_settings:
                self.set_selected_settings()
            for setting in self.selected_settings:
                for day in range(1, 16):
                    loc_name = f"{setting} - Day {day}"
                    loc_id = SETTING_LOCATIONS.get(loc_name)
                    if loc_id:
                        locs[loc_name] = loc_id
        return locs

    def validate_ids(self):
        """Ensure item and location IDs are unique."""
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
        # Ensure selected dishes are initialized
        self.set_selected_dishes()
        self.set_selected_settings()
        self._location_name_to_id = self.generate_location_table()
        self.validate_ids()
        create_plateup_regions(self)

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> PlateUpItem:
        """Create a PlateUp item from the given name."""
        if name == "Random Appliance":
            return PlateUpItem(name, classification, 1001, self.player)
        if name == "Random Filler Appliance":
            return PlateUpItem(name, classification, 1002, self.player)

        if name in self.item_name_to_id:
            item_id = self.item_name_to_id[name]
        else:
            # Rebuild mapping from current ITEMS in case the class-level cache is stale
            from .Items import ITEMS as CURRENT_ITEMS
            self.item_name_to_id = {n: data[0] for n, data in CURRENT_ITEMS.items()}
            if name in self.item_name_to_id:
                item_id = self.item_name_to_id[name]
            else:
                raise ValueError(f"Item '{name}' not found in ITEMS")
        return PlateUpItem(name, classification, item_id, self.player)

    def create_items(self):
        self.set_selected_dishes()
        """Create the item pool for all planned locations."""
        # Base planned locations used by region creation
        planned_locations = self.generate_location_table()
        base_locations = len(planned_locations)
        # Dish locations are included in the base table
        total_locations = base_locations
        item_pool = []

        # Always remove one dish to be the starting dish (if any)
        self.starting_dish = self.selected_dishes[0] if self.selected_dishes else None
        unlock_dishes = self.selected_dishes[1:] if len(self.selected_dishes) > 1 else []

        # Add unlock items for the rest of the selected dishes (or all if none selected)
        for dish in unlock_dishes:
            unlock_name = f"{dish} Unlock"
            # Ensure mapping is current
            try:
                from .Items import ITEMS as CURRENT_ITEMS
                self.item_name_to_id = {n: data[0] for n, data in CURRENT_ITEMS.items()}
            except Exception:
                pass
            if unlock_name in self.item_name_to_id:
                item_pool.append(self.create_item(unlock_name, classification=ItemClassification.progression))
            else:
                logging.error(f"[Player {self.multiworld.player_name[self.player]}] Unlock item missing: {unlock_name}. ITEMS should include unlocks generated from Locations.dish_dictionary.")

        # Add progression items.
        # Add Player speed upgrades based on configured count
        player_speed_count = int(self.options.player_speed_upgrade_count.value)
        if player_speed_count > 0:
            item_pool.extend([
                self.create_item("Speed Upgrade Player", classification=ItemClassification.progression)
                for _ in range(player_speed_count)
            ])

        speed_mode = self.options.appliance_speed_mode.value
        appliance_speed_count = int(self.options.appliance_speed_upgrade_count.value)
        if appliance_speed_count > 0:
            if speed_mode == 0:
                item_pool.extend([
                    self.create_item("Speed Upgrade Appliance", classification=ItemClassification.progression)
                    for _ in range(appliance_speed_count)
                ])
            else:
                for _ in range(appliance_speed_count):
                    item_pool.extend([
                        self.create_item("Speed Upgrade Cook", classification=ItemClassification.progression),
                        self.create_item("Speed Upgrade Clean", classification=ItemClassification.progression),
                        self.create_item("Speed Upgrade Chop", classification=ItemClassification.progression)
                    ])

        # Determine total days to drive item counts
        if self.options.goal.value == Goal.option_franchise_x_times:
            total_days = 15 * int(self.options.franchise_count.value)
        elif self.options.goal.value == Goal.option_reach_day_x_with_dishes:
            total_days = int(self.options.day_target.value)
        else:
            total_days = int(self.options.day_count.value)

        # Place Money Cap Increase at ~1 per 10 days
        money_cap_items = max(1, total_days // 10)
        logging.debug(f"[Player {self.multiworld.player_name[self.player]}] Auto Money Cap items by cadence: total_days={total_days}, placing={money_cap_items}")
        if money_cap_items > 0:
            item_pool.extend([
                self.create_item("Money Cap Increase", classification=ItemClassification.progression)
                for _ in range(money_cap_items)
            ])

        # Number of Day Lease items required depends on configurable interval
        interval = max(1, int(self.options.day_lease_interval.value))
        lease_count = math.ceil(total_days / interval)
        item_pool.extend([
            self.create_item("Day Lease", classification=ItemClassification.progression)
            for _ in range(lease_count)
        ])

        # Add Remove Card items if starting cards are enabled
        if self.options.starting_cards.value != 0:
            remove_card_count = int(self.options.starting_cards_amount.value)
            item_pool.extend([
                self.create_item("Remove Card", classification=ItemClassification.progression)
                for _ in range(remove_card_count)
            ])

        # Add a small number of Shop Size Increase items (1 per 20 days, min 1)
        shop_size_count = max(1, total_days // 10)
        item_pool.extend([
            self.create_item("Shop Size Increase", classification=ItemClassification.useful)
            for _ in range(shop_size_count)
        ])

        if self.options.trap_cards.value:
            # Add traps at ~10% of total locations, minimum 3
            remaining_capacity = max(0, total_locations - len(item_pool))
            desired_traps = max(3, total_days // 10)  # scale with run length
            trap_to_add = min(desired_traps, remaining_capacity)
            item_pool.extend([
                self.create_item("Random Customer Card", classification=ItemClassification.trap)
                for _ in range(trap_to_add)
            ])

        # Top up remaining capacity with a mix of normal and filler appliances,
        # ensuring there are enough filler-classified items to cover excluded locations.
        remaining = max(0, total_locations - len(item_pool))
        try:
            excluded_needed = sum(
                1
                for loc in self.multiworld.get_locations()
                if loc.player == self.player and loc.progress_type == LocationProgressType.EXCLUDED
            )
        except Exception:
            excluded_needed = sum(1 for loc_id in planned_locations.values() if loc_id in EXCLUDED_LOCATIONS)

        def count_filler(items: list[PlateUpItem]) -> int:
            return sum(1 for item in items if item.classification == ItemClassification.filler)

        filler_needed = max(0, excluded_needed - count_filler(item_pool))
        filler_from_remaining = min(filler_needed, remaining)
        if filler_from_remaining:
            item_pool.extend([
                self.create_item("Random Filler Appliance", classification=ItemClassification.filler)
                for _ in range(filler_from_remaining)
            ])
            remaining -= filler_from_remaining
            filler_needed -= filler_from_remaining

        # Fill remaining slots with specific appliance unlocks first, then generic random ones
        unlock_queue = [
            f"Unlock {name}"
            for name in appliance_unlock_dictionary.values()
            if f"Unlock {name}" in self.item_name_to_id
        ] if self.options.appliance_unlocks.value else []
        filler_queue = ["5 Coins", "Random Filler Appliance", "10 Coins", "Random Filler Appliance", "20 Coins", "Random Filler Appliance"]
        if self.options.decoration_unlocks.value:
            filler_queue = ["5 Coins", "Random Decoration Unlock", "10 Coins", "Random Filler Appliance", "20 Coins", "Random Decoration Unlock"]
        unlock_index = 0
        for i in range(remaining):
            if i % 2 == 0:
                if unlock_index < len(unlock_queue):
                    unlock_name = unlock_queue[unlock_index]
                    unlock_classification = ITEMS[unlock_name][1]
                    item_pool.append(self.create_item(unlock_name, classification=unlock_classification))
                    unlock_index += 1
                else:
                    item_pool.append(self.create_item("Random Appliance", classification=ItemClassification.useful))
            else:
                coin_name = filler_queue[(i // 2) % len(filler_queue)]
                item_pool.append(self.create_item(coin_name, classification=ItemClassification.filler))

        if filler_needed > 0:
            for idx, item in enumerate(item_pool):
                if filler_needed <= 0:
                    break
                if item.name == "Random Appliance":
                    item_pool[idx] = self.create_item("Random Filler Appliance", classification=ItemClassification.filler)
                    filler_needed -= 1
            if filler_needed > 0:
                logging.warning(
                    f"[Player {self.multiworld.player_name[self.player]}] Unable to satisfy filler quota. "
                    f"Missing {filler_needed} filler items for excluded locations."
                )

        logging.debug(f"[Player {self.multiworld.player_name[self.player]}] Total item pool count: {len(item_pool)}")
        logging.debug(f"[Player {self.multiworld.player_name[self.player]}] Total locations: {total_locations}")
        self.multiworld.itempool.extend(item_pool)

    def set_rules(self):
        """Set progression rules and top-up the item pool based on final locations."""

        self.set_selected_settings()

        # Filter dishes only when enabled
        if self.options.dish.value > 0:
            filter_selected_dishes(self)
        else:
            self.selected_dishes = []
            self.valid_dish_locations = []

        filter_selected_settings(self)

        restrict_locations_by_progression(self)

        if self.options.goal.value == Goal.option_franchise_x_times:
            def plateup_completion(state: CollectionState):
                count = self.options.franchise_count.value
                loc_name = f"Franchise {count} times"
                return state.can_reach(loc_name, "Location", self.player)
        elif self.options.goal.value == Goal.option_reach_day_x_with_dishes:
            target_day = self.options.day_target.value
            dish_count_opt = self.options.dish.value
            dish_goal = self.options.dish_goal_count.value
            day_loc = f"Complete Day {target_day}"
            if dish_goal <= 1 or dish_count_opt == 0:
                # Just need to reach the target day
                def plateup_completion(state: CollectionState, dl=day_loc):
                    return state.can_reach(dl, "Location", self.player)
            else:
                # Need to reach target day AND have dish_goal dishes active
                # (1 starting dish free; need dish_goal-1 unlocks from the item pool)
                needed_unlocks = dish_goal - 1
                all_unlock_names = [f"{dish} Unlock" for dish in getattr(self, "selected_dishes", [])[1:]]
                unlock_names = [n for n in all_unlock_names if n in self.item_name_to_id]
                def plateup_completion(state: CollectionState, dl=day_loc, un=unlock_names, nu=needed_unlocks):
                    return (
                        state.can_reach(dl, "Location", self.player)
                        and state.has_from_list(un, self.player, nu)
                    )
        else:  # complete_x_days
            def plateup_completion(state: CollectionState):
                count = self.options.day_count.value
                loc_name = f"Complete Day {count}"
                return state.can_reach(loc_name, "Location", self.player)

        self.multiworld.completion_condition[self.player] = plateup_completion
        apply_rules(self)

        final_locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        current_items = [item for item in self.multiworld.itempool if item.player == self.player]
        missing = len(final_locations) - len(current_items)
        if missing > 0:
            logging.debug(f"[Player {self.multiworld.player_name[self.player]}] Item pool is short by {missing} items. Adding appliance placeholders.")
            for i in range(missing):
                if i % 2 == 0:
                    self.multiworld.itempool.append(self.create_item("Random Appliance", classification=ItemClassification.useful))
                else:
                    self.multiworld.itempool.append(self.create_item("Random Filler Appliance", classification=ItemClassification.filler))

    def fill_slot_data(self):
        """Return slot data for this player."""
        options_dict = self.options.as_dict(
            "goal",
            "franchise_count",
            "day_count",
            "day_target",
            "dish_goal_count",
            "death_link",
            "death_link_behavior",
            "appliance_speed_mode",
            "day_lease_interval",
            "starting_money_cap",
            "appliance_unlocks",
            "decoration_unlocks",
            "trap_cards",
            "setting_checks",
            "setting_check_mode",
            "setting_extra_checks",
            "starting_cards",
            "starting_cards_amount",
        )
        options_dict["items_kept"] = self.options.appliances_kept.value
        if self.options.dish.value == 0:
            options_dict["selected_dishes"] = []
            options_dict["starting_dish"] = None
        else:
            options_dict["starting_dish"] = getattr(self, "starting_dish", None)
            options_dict["selected_dishes"] = getattr(self, "selected_dishes", [])
            # Diagnostics: count of planned dish day locations included
            planned = getattr(self, "_location_name_to_id", {})
            count = 0
            for dish in options_dict["selected_dishes"]:
                for day in range(1, 16):
                    name = f"{dish} - Day {day}"
                    if name in planned:
                        count += 1
            options_dict["dish_locations_present"] = count
        if self.options.setting_checks.value:
            self.set_selected_settings()
            options_dict["selected_settings"] = getattr(self, "selected_settings", [])
            planned = getattr(self, "_location_name_to_id", {})
            count = 0
            for setting in options_dict["selected_settings"]:
                for day in range(1, 16):
                    name = f"{setting} - Day {day}"
                    if name in planned:
                        count += 1
            options_dict["setting_locations_present"] = count
        else:
            options_dict["selected_settings"] = []
            options_dict["setting_locations_present"] = 0
        # Diagnostics
        options_dict["dish_unlocks"] = 0 if self.options.dish.value == 0 else 1
        return options_dict

    def get_filler_item_name(self):
        """Randomly select a filler item from the available candidates."""
        # Use the explicit filler placeholder to avoid ambiguity.
        return "Random Filler Appliance"

    def set_selected_settings(self):
        if not getattr(self.options, "setting_checks", None) or not self.options.setting_checks.value:
            self.selected_settings = []
            self.valid_setting_locations = []
            return

        mode = getattr(self.options, "setting_check_mode", None)
        mode_value = getattr(mode, "value", SettingCheckMode.option_base_only)
        include_base = mode_value != SettingCheckMode.option_extras_only
        include_extras = mode_value != SettingCheckMode.option_base_only

        selected: list[str] = []
        if include_base:
            selected.append(BASE_SETTING_NAME)

        if include_extras:
            extra_settings = list(getattr(self.options.setting_extra_checks, "value", []))
            for slug in extra_settings:
                display = OPTIONAL_SETTING_DISPLAY.get(slug, slug)
                if display not in selected:
                    selected.append(display)

        self.selected_settings = selected

    # Dishes weighted toward easier starts (3× more likely to be the starting dish)
    _EASY_START_DISHES = {"Salad", "Pizza", "Coffee", "Breakfast"}

    def set_selected_dishes(self):
        dish_count = self.options.dish.value
        try:
            from .Locations import dish_dictionary
            all_dishes = list(dish_dictionary.values())
        except Exception:
            all_dishes = [
                "Salad", "Steak", "Burger", "Coffee", "Pizza", "Dumplings", "Turkey",
                "Pie", "Cakes", "Spaghetti", "Fish", "Tacos", "Hot Dogs", "Breakfast", "Stir Fry",
                "Sandwiches", "Sundaes"
            ]
        if dish_count <= 0:
            self.selected_dishes = []
            return
        # Sanitize any pre-set selection (e.g., plando)
        if self.selected_dishes:
            sanitized = [d for d in self.selected_dishes if d in all_dishes]
            if len(sanitized) >= dish_count:
                self.selected_dishes = sanitized[:dish_count]
                return
        # Pick starting dish with weighted probability (easy dishes are 3× more likely)
        weights = [3 if d in self._EASY_START_DISHES else 1 for d in all_dishes]
        starting_dish = self.random.choices(all_dishes, weights=weights, k=1)[0]
        if dish_count == 1:
            self.selected_dishes = [starting_dish]
            return
        # Fill remaining slots with a random sample from the non-starting dishes
        remaining = [d for d in all_dishes if d != starting_dish]
        rest = self.random.sample(remaining, k=min(dish_count - 1, len(remaining)))
        self.selected_dishes = [starting_dish] + rest
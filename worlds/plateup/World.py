import logging
import math
from collections import Counter

from BaseClasses import ItemClassification, CollectionState
from worlds.AutoWorld import World
from . import Web_World
from .Items import ITEMS, PlateUpItem, APPLIANCE_UNLOCK_POOL, APPLIANCE_UNLOCK_PRIORITY, APPLIANCE_UNLOCK_ITEMS
from .Locations import (
    DISH_LOCATIONS, FRANCHISE_LOCATION_DICT, DAY_LOCATION_DICT, EXCLUDED_LOCATIONS,
    SETTING_LOCATIONS, EXTRA_SETTING_LOCATIONS, BLUEPRINT_LOCATIONS, REROLL_LOCATIONS,
    _setting_slug_to_display,
)
from .Options import PlateUpOptions, Goal, SettingCheckMode
from .Rules import (
    filter_selected_dishes,
    apply_rules,
    restrict_locations_by_progression
)


def _get_dishes_with_leases(world: "PlateUpWorld") -> list[str]:
    """Compute which dishes get day lease items based on goal and scope settings.
    
    Shared helper to avoid duplication between World.py and Regions.py.
    Returns empty list if dish-specific mode is not active.
    """
    _is_dish_specific = (
        world.options.day_lease_mode.value == 1
        and world.options.dish.value > 0
        and world.selected_dishes
    )
    
    if not _is_dish_specific:
        return []
    
    _is_goal2 = world.options.goal.value == Goal.option_reach_day_x_with_dishes
    scope = world.options.dish_lease_scope.value
    
    if scope == 1 and _is_goal2:
        # goal_count_only: only first N dishes get leases
        dish_goal = min(world.options.dish_goal_count.value, len(world.selected_dishes))
        return list(world.selected_dishes[:dish_goal])
    else:
        # all_dishes: all selected dishes get leases
        return list(world.selected_dishes)


class PlateUpWorld(World):
    game = "PlateUp"
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
        **EXTRA_SETTING_LOCATIONS,
        **BLUEPRINT_LOCATIONS,
        **REROLL_LOCATIONS,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.excluded_locations = set()
        # Initialize attributes to avoid hasattr checks
        self.selected_dishes = []
        self.starting_dish = None
        self.valid_dish_locations = []
        self.dishes_with_leases = []

    def generate_location_table(self):
        """Plan locations based on goal/options and selected dishes."""
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
            # Include the "Lose a Run" location (always present for franchise goal)
            lose_id = FRANCHISE_LOCATION_DICT.get("Lose a Run")
            if lose_id is not None:
                locs["Lose a Run"] = lose_id
        elif goal == 1:
            required_days = self.options.day_count.value
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
            if dish_count > 0:
                if not self.selected_dishes or len(self.selected_dishes) != dish_count:
                    self.set_selected_dishes()
                for dish in self.selected_dishes:
                    for day in range(1, 16):
                        loc_name = f"{dish} - Day {day}"
                        loc_id = DISH_LOCATIONS.get(loc_name)
                        if loc_id:
                            locs[loc_name] = loc_id
            # Include the "Lose a Run" location (always present for day goal)
            lose_id = DAY_LOCATION_DICT.get("Lose a Run")
            if lose_id is not None:
                locs["Lose a Run"] = lose_id
        else:  # goal == 2: reach_day_x_with_dishes
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
            if dish_count > 0:
                if not self.selected_dishes or len(self.selected_dishes) != dish_count:
                    self.set_selected_dishes()
                for dish in self.selected_dishes:
                    for day in range(1, 16):
                        loc_name = f"{dish} - Day {day}"
                        loc_id = DISH_LOCATIONS.get(loc_name)
                        if loc_id:
                            locs[loc_name] = loc_id

        # Blueprint check locations (all goals)
        bp_count = int(self.options.blueprint_check_count.value)
        if bp_count > 0:
            if self.options.money_cap_enabled.value:
                max_cap = (int(self.options.starting_money_cap.value)
                           + int(self.options.money_cap_increase_amount.value)
                           * int(self.options.money_cap_increase_count.value))
                base_price = int(self.options.blueprint_base_price.value)
                price_inc = int(self.options.blueprint_price_increase.value)
                within_cap = sum(
                    1 for i in range(1, bp_count + 1)
                    if base_price + (i - 1) * price_inc <= max_cap
                )
                allowed = min(bp_count, math.ceil(within_cap * 1.3))
            else:
                allowed = bp_count
            for i in range(1, allowed + 1):
                bpname = f"Blueprint Check {i}"
                if bpname in BLUEPRINT_LOCATIONS:
                    locs[bpname] = BLUEPRINT_LOCATIONS[bpname]

        # Reroll cost check locations (all goals)
        reroll_count = int(self.options.reroll_check_count.value)
        if reroll_count > 0:
            for i in range(1, reroll_count + 1):
                rname = f"Reroll Cost Check {i}"
                if rname in REROLL_LOCATIONS:
                    locs[rname] = REROLL_LOCATIONS[rname]

        # Setting check locations (all goals)
        if self.options.setting_checks.value:
            mode = self.options.setting_check_mode.value
            extra_slugs = list(self.options.setting_extra_checks.value)
            if mode in (0, 1):  # base_only or base_and_extras
                locs.update(SETTING_LOCATIONS)
            if mode in (1, 2):  # base_and_extras or extras_only
                for slug in extra_slugs:
                    display = _setting_slug_to_display.get(slug)
                    if display:
                        for d in range(1, 16):
                            sname = f"{display} - Day {d}"
                            if sname in EXTRA_SETTING_LOCATIONS:
                                locs[sname] = EXTRA_SETTING_LOCATIONS[sname]

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
        
        # BUG FIX #2: Validate dish_lease_scope setting
        # dish_lease_scope only applies to goal type 2 (reach_day_x_with_dishes)
        if (self.options.dish_lease_scope.value == 1 and  # goal_count_only
            self.options.goal.value != Goal.option_reach_day_x_with_dishes):
            logging.warning(
                f"[PlateUp] Player {self.player_name}: dish_lease_scope is set to 'goal_count_only' "
                f"but goal is not 'reach_day_x_with_dishes'. This setting only applies to goal type 2. "
                f"It will be ignored and all selected dishes will receive lease items."
            )
        
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
        """Create the item pool for all planned locations."""
        self.set_selected_dishes()
        location_table = self.generate_location_table()
        self._location_name_to_id = location_table
        total_locations = len(location_table)
        item_pool = []

        # --- Dish unlocks ---
        free_starters = min(self.options.free_starter_dishes.value, len(self.selected_dishes))
        self.starting_dishes = self.selected_dishes[:free_starters]
        self.starting_dish = self.starting_dishes[0] if self.starting_dishes else None
        for dish in self.selected_dishes[free_starters:]:
            unlock_name = f"{dish} Unlock"
            if unlock_name in self.item_name_to_id:
                item_pool.append(self.create_item(unlock_name, classification=ItemClassification.progression))

        # --- Speed upgrades (progression, no access logic) ---
        player_speed_count = int(self.options.player_speed_upgrade_count.value)
        if player_speed_count > 0:
            item_pool.extend([
                self.create_item("Speed Upgrade Player", classification=ItemClassification.progression)
                for _ in range(player_speed_count)
            ])
        appliance_speed_count = int(self.options.appliance_speed_upgrade_count.value)
        if appliance_speed_count > 0:
            if self.options.appliance_speed_mode.value == 0:
                item_pool.extend([
                    self.create_item("Speed Upgrade Appliance", classification=ItemClassification.progression)
                    for _ in range(appliance_speed_count)
                ])
            else:
                for _ in range(appliance_speed_count):
                    item_pool.extend([
                        self.create_item("Speed Upgrade Cook", classification=ItemClassification.progression),
                        self.create_item("Speed Upgrade Clean", classification=ItemClassification.progression),
                        self.create_item("Speed Upgrade Chop", classification=ItemClassification.progression),
                    ])

        # --- Determine total days for item scale ---
        goal = self.options.goal.value
        if goal == Goal.option_franchise_x_times:
            total_days = 15 * int(self.options.franchise_count.value)
        elif goal == Goal.option_reach_day_x_with_dishes:
            total_days = int(self.options.day_target.value)
        else:
            total_days = int(self.options.day_count.value)

        # --- Money Cap Increase ---
        if self.options.money_cap_enabled.value:
            cap_count = int(self.options.money_cap_increase_count.value)
            item_pool.extend([
                self.create_item("Money Cap Increase", classification=ItemClassification.progression)
                for _ in range(cap_count)
            ])

        # --- Day Lease items ---
        if self.options.day_leases_enabled.value:
            interval = max(1, int(self.options.day_lease_interval.value))
            _is_dish_specific = (
                self.options.day_lease_mode.value == 1
                and self.options.dish.value > 0
                and self.selected_dishes
            )
            _is_goal2 = self.options.goal.value == Goal.option_reach_day_x_with_dishes
            goal = self.options.goal.value

            # Use shared helper to determine which dishes get lease items
            self.dishes_with_leases = _get_dishes_with_leases(self)

            if _is_dish_specific and _is_goal2:
                # Goal 2 + dish_specific: dish leases are sufficient; no entrance lease gating.
                pass
            elif _is_dish_specific and goal == Goal.option_franchise_x_times:
                # Franchise runs reset after Day 15 and are gated by the active
                # dish's leases. They do not consume global overtime capacity.
                pass
            elif _is_dish_specific:
                # Day-count goal + dish_specific: Overtime Day Lease covers only days above day 15.
                # Each dish's lease chain reaches day 15, so overtime = days beyond that coverage.
                overtime_days = max(0, total_days - 15 * len(self.dishes_with_leases))
                overtime_lease_count = math.ceil(overtime_days / interval) if overtime_days > 0 else 0
                item_pool.extend([
                    self.create_item("Overtime Day Lease", ItemClassification.progression)
                    for _ in range(overtime_lease_count)
                ])
            else:
                # Global mode (any goal): regular Day Lease gates all days.
                lease_count = math.ceil(total_days / interval)
                item_pool.extend([
                    self.create_item("Day Lease", ItemClassification.progression)
                    for _ in range(lease_count)
                ])

            # Per-dish lease items gate {Dish} - Day X locations (dish checks cap at day 15).
            # BUG FIX #1: Only create per-dish leases when dish day locations actually exist.
            # Goals 0 (franchise) and 1 (complete_x_days) can have dish day locations when dish > 0.
            # Goal 2 (reach_day_x_with_dishes) always has dish day locations.
            if _is_dish_specific and self.options.dish.value > 0:
                dish_lease_count = math.ceil(15 / interval)
                for dish in self.dishes_with_leases:
                    item_pool.extend([
                        self.create_item(f"{dish} Day Lease", ItemClassification.progression)
                        for _ in range(dish_lease_count)
                    ])

        # --- Global Patience Increase items ---
        if self.options.global_patience_enabled.value:
            patience_count = int(self.options.global_patience_upgrade_count.value)
            item_pool.extend([
                self.create_item("Global Patience Increase", classification=ItemClassification.progression)
                for _ in range(patience_count)
            ])

        # --- Starting card Remove Card items ---
        starting_cards = self.options.starting_cards.value
        if starting_cards > 0:
            card_count = int(self.options.starting_cards_amount.value)
            item_pool.extend([
                self.create_item("Remove Card", classification=ItemClassification.progression)
                for _ in range(card_count)
            ])
        for _ in range(len(list(self.options.extra_starting_cards.value))):
            item_pool.append(self.create_item("Remove Card", classification=ItemClassification.progression))

        # --- Overflow guard: raise early if mandatory items exceed locations ---
        if len(item_pool) > total_locations:
            raise Exception(
                f"{len(item_pool)} mandatory items cannot fit — only {total_locations} locations are available. "
                f"Reduce item counts or increase day_target/day_count."
            )

        # --- Trap items (trap_chance > 0) ---
        trap_chance = int(self.options.trap_chance.value)
        if trap_chance > 0:
            remaining_before_traps = max(0, total_locations - len(item_pool))
            trap_count = int(remaining_before_traps * trap_chance / 100)
            if trap_count > 0:
                _key_to_name = {
                    "everything_is_on_fire": "EVERYTHING IS ON FIRE",
                    "super_slow": "Super Slow",
                    "random_customer_card": "Random Customer Card",
                    "patience_decrease": "Patience Decrease",
                    "more_customers": "More Customers",
                    "min_group_size_increase": "Minimum Group Size Increase",
                    "max_group_size_increase": "Maximum Group Size Increase",
                    "random_dish_extra": "Random Dish Extra",
                    "random_side_dish": "Random Side Dish",
                    "tip_jar_drain": "Tip Jar Drain",
                    "good_advertisement": "Good Advertisement",
                    "card_swap": "Card Swap",
                }
                weights_dict = self.options.trap_weights.value
                pool = [(name, w) for k, w in weights_dict.items()
                        if (name := _key_to_name.get(k)) and w > 0]
                if pool:
                    names_list, ws_list = zip(*pool)
                    _card_trap_names = {"Random Customer Card", "Card Swap"}
                    _card_trap_cap = 20
                    _card_trap_count = 0
                    for chosen in self.multiworld.random.choices(list(names_list), weights=list(ws_list), k=trap_count):
                        if chosen in _card_trap_names:
                            if _card_trap_count < _card_trap_cap:
                                item_pool.append(self.create_item(chosen, classification=ItemClassification.trap))
                                _card_trap_count += 1
                        else:
                            item_pool.append(self.create_item(chosen, classification=ItemClassification.trap))
                    # Add one Remove Card per card trap placed, limited to available space
                    _remove_budget = max(0, total_locations - len(item_pool))
                    for _ in range(min(_card_trap_count, _remove_budget)):
                        item_pool.append(self.create_item("Remove Card", classification=ItemClassification.progression))

        # --- Filler percent items (each consumes from remaining budget) ---
        def _add_filler(item_name: str, count: int, cls=ItemClassification.filler):
            item_pool.extend([self.create_item(item_name, classification=cls) for _ in range(count)])

        remaining = max(0, total_locations - len(item_pool))

        pat_pct = int(self.options.patience_filler_percent.value)
        pat_count = int(remaining * pat_pct / 100)
        _add_filler("Patience Increase", pat_count)
        remaining -= pat_count

        cust_pct = int(self.options.customer_filler_percent.value)
        cust_count = int(remaining * cust_pct / 100)
        _add_filler("Less Customers", cust_count)
        remaining -= cust_count

        grp_pct = int(self.options.group_size_filler_percent.value)
        grp_count = int(remaining * grp_pct / 100)
        half_grp = grp_count // 2
        _add_filler("Minimum Group Size Decrease", half_grp)
        _add_filler("Maximum Group Size Decrease", half_grp)
        remaining -= half_grp * 2

        mess_pct = int(self.options.mess_reduction_percent.value)
        mess_count = int(remaining * mess_pct / 100)
        _add_filler("Mess Reduction", mess_count)
        remaining -= mess_count

        coin_pct = int(self.options.coin_filler_percent.value)
        coin_count = int(remaining * coin_pct / 100)
        _add_filler("Coin", coin_count)
        remaining -= coin_count

        # --- Top off with named appliance unlocks, then generic appliance / decoration filler ---
        remaining_final = max(0, total_locations - len(item_pool))
        use_decorations = self.options.decoration_unlocks.value

        # Named appliance unlock items occupy as many filler slots as the pool_size allows,
        # replacing an equivalent number of generic Random Appliance items.
        if self.options.appliance_unlocks.value:
            pool_size = min(
                int(self.options.appliance_unlock_pool_size.value),
                len(APPLIANCE_UNLOCK_POOL),
                remaining_final,
            )
            priority = [a for a in APPLIANCE_UNLOCK_PRIORITY if a in APPLIANCE_UNLOCK_POOL]
            non_priority = [a for a in APPLIANCE_UNLOCK_POOL if a not in priority]
            self.multiworld.random.shuffle(non_priority)
            selected_appliances = (priority + non_priority)[:pool_size]
            for app_name in selected_appliances:
                item_pool.append(self.create_item(f"Unlock {app_name}", ItemClassification.useful))
            self.unlocked_appliances_list = [a for a in APPLIANCE_UNLOCK_POOL if a not in selected_appliances]
        else:
            selected_appliances = []
            self.unlocked_appliances_list = list(APPLIANCE_UNLOCK_POOL)

        for i in range(max(0, total_locations - len(item_pool))):
            if use_decorations and i % 3 == 2:
                item_pool.append(self.create_item("Random Decoration Unlock", classification=ItemClassification.filler))
            elif i % 2 == 0:
                item_pool.append(self.create_item("Random Appliance", classification=ItemClassification.useful))
            else:
                item_pool.append(self.create_item("Random Filler Appliance", classification=ItemClassification.filler))

        logging.debug(f"[Player {self.multiworld.player_name[self.player]}] Total items: {len(item_pool)}, locations: {total_locations}")
        self.multiworld.itempool.extend(item_pool)

    def set_rules(self):
        """Set progression rules and top-up the item pool based on final locations."""

        # Filter dishes only when enabled
        if self.options.dish.value > 0:
            filter_selected_dishes(self)
        else:
            self.selected_dishes = []
            self.valid_dish_locations = []

        restrict_locations_by_progression(self)

        if self.options.goal.value == Goal.option_franchise_x_times:
            required = self.options.franchise_count.value
            for i in range(required + 1, 51):  # expanded upper bound
                name = f"Franchise {i} times"
                if name in FRANCHISE_LOCATION_DICT:
                    self.excluded_locations.add(FRANCHISE_LOCATION_DICT[name])

        def plateup_completion(state: CollectionState):
            if self.options.goal.value == Goal.option_franchise_x_times:
                count = self.options.franchise_count.value
                loc_name = f"Franchise {count} times"
                return state.can_reach(loc_name, "Location", self.player)
            elif self.options.goal.value == Goal.option_complete_x_days:
                count = self.options.day_count.value
                loc_name = f"Complete Day {count}"
                return state.can_reach(loc_name, "Location", self.player)
            else:  # reach_day_x_with_dishes
                day_target = self.options.day_target.value
                if not state.can_reach(f"Complete Day {day_target}", "Location", self.player):
                    return False
                dish_goal = min(self.options.dish_goal_count.value, self.options.dish.value)
                if dish_goal <= 0:
                    return True
                starter_dishes = getattr(self, 'starting_dishes', [])
                dishes_available = sum(
                    1 for dish in getattr(self, 'selected_dishes', [])
                    if dish in starter_dishes or state.has(f"{dish} Unlock", self.player)
                )
                return dishes_available >= dish_goal

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
            "player_speed_upgrade_count",
            "appliance_speed_upgrade_count",
            "day_leases_enabled",
            "day_lease_interval",
            "day_lease_mode",
            "dish_lease_scope",
            "day_leases_progressive",
            "money_cap_enabled",
            "starting_money_cap",
            "money_cap_increase_amount",
            "money_cap_activation",
            "appliance_unlocks",
            "appliance_unlock_grants_appliance",
            "unlocked_appliances_in_shop",
            "decoration_unlocks",
            "trap_weights",
            "trap_chance",
            "patience_filler_percent",
            "customer_filler_percent",
            "group_size_filler_percent",
            "mess_reduction_percent",
            "coin_filler_percent",
            "setting_checks",
            "setting_check_mode",
            "setting_extra_checks",
            "starting_cards",
            "starting_cards_amount",
            "starting_group_size",
            "global_patience_enabled",
            "global_patience_upgrade_count",
            "global_patience_starting_debuff",
            "achievement_check_mode",
            "money_cap_increase_count",
            "appliance_unlock_pool_size",
            "blueprint_base_price",
            "blueprint_price_increase",
            "blueprint_check_count",
            "random_research",
            "allow_save_file_editing",
        )
        options_dict["items_kept"] = 0 if self.options.allow_save_file_editing.value else self.options.appliances_kept.value
        options_dict["extra_starting_cards"] = list(self.options.extra_starting_cards.value)
        options_dict["free_starter_dishes"] = self.options.free_starter_dishes.value
        if self.options.dish.value == 0:
            options_dict["selected_dishes"] = []
            options_dict["starting_dishes"] = []
            options_dict["starting_dish"] = None
        else:
            options_dict["starting_dish"] = getattr(self, "starting_dish", None)
            options_dict["starting_dishes"] = getattr(self, "starting_dishes", [])
            options_dict["selected_dishes"] = getattr(self, "selected_dishes", [])
            planned = getattr(self, "_location_name_to_id", {})
            count = sum(
                1 for dish in options_dict["selected_dishes"]
                for day in range(1, 16)
                if f"{dish} - Day {day}" in planned
            )
            options_dict["dish_locations_present"] = count

        # Blueprint check IDs: mapping of location name -> ID, matching the original format.
        planned = getattr(self, "_location_name_to_id", {})
        blueprint_ids = {
            f"Blueprint Check {i}": planned[f"Blueprint Check {i}"]
            for i in range(1, int(self.options.blueprint_check_count.value) + 1)
            if f"Blueprint Check {i}" in planned
        }
        options_dict["blueprint_check_ids"] = blueprint_ids

        # unlocked_appliances: appliances not assigned a named unlock item (pre-unlocked on the mod side)
        options_dict["unlocked_appliances"] = getattr(self, "unlocked_appliances_list", list(APPLIANCE_UNLOCK_POOL))

        # Reroll check count
        options_dict["reroll_check_count"] = int(self.options.reroll_check_count.value)

        # Dish unlock flag
        options_dict["dish_unlocks"] = 0 if self.options.dish.value == 0 else 1

        # Setting check selected settings and location counts
        if self.options.setting_checks.value:
            self.set_selected_settings()
            options_dict["selected_settings"] = getattr(self, "selected_settings", [])
            planned = getattr(self, "_location_name_to_id", {})
            count = sum(
                1 for setting in options_dict["selected_settings"]
                for day in range(1, 16)
                if f"{setting} - Day {day}" in planned
            )
            options_dict["setting_locations_present"] = count
        else:
            options_dict["selected_settings"] = []
            options_dict["setting_locations_present"] = 0

        # Day lease counts for client
        if self.options.day_leases_enabled.value:
            _interval = max(1, int(self.options.day_lease_interval.value))
            _goal = self.options.goal.value
            if _goal == Goal.option_franchise_x_times:
                _total_days = 15 * int(self.options.franchise_count.value)
            elif _goal == Goal.option_reach_day_x_with_dishes:
                _total_days = int(self.options.day_target.value)
            else:
                _total_days = int(self.options.day_count.value)
            _is_dish_specific = (
                self.options.day_lease_mode.value == 1
                and self.options.dish.value > 0
                and bool(getattr(self, "selected_dishes", []))
            )
            _is_goal2 = _goal == Goal.option_reach_day_x_with_dishes
            if _is_dish_specific:
                options_dict["dish_lease_count"] = math.ceil(15 / _interval)
                _dishes_with_leases = getattr(self, "dishes_with_leases", [])
                if _goal == Goal.option_franchise_x_times:
                    options_dict["day_lease_count"] = 0
                elif not _is_goal2:
                    _overtime_days = max(0, _total_days - 15 * len(_dishes_with_leases))
                    options_dict["day_lease_count"] = math.ceil(_overtime_days / _interval) if _overtime_days > 0 else 0
                else:
                    options_dict["day_lease_count"] = 0
            else:
                options_dict["day_lease_count"] = math.ceil(_total_days / _interval)
                options_dict["dish_lease_count"] = 0
        else:
            options_dict["day_lease_count"] = 0
            options_dict["dish_lease_count"] = 0

        # Reroll max cost based on money cap settings
        if self.options.money_cap_enabled.value:
            if self.options.goal.value == Goal.option_franchise_x_times:
                _rtd = 15 * int(self.options.franchise_count.value)
            elif self.options.goal.value == Goal.option_reach_day_x_with_dishes:
                _rtd = int(self.options.day_target.value)
            else:
                _rtd = int(self.options.day_count.value)
            _sc = int(self.options.starting_money_cap.value)
            _ca = int(self.options.money_cap_increase_amount.value)
            _min_for_60 = max(0, math.ceil((60 - _sc) / _ca)) if _ca > 0 else 0
            _cap_items = max(_rtd // 15 + 1, _min_for_60)
            options_dict["reroll_max_cost"] = min(_sc + _ca * _cap_items, 300)
        else:
            options_dict["reroll_max_cost"] = 300

        return options_dict

    def get_filler_item_name(self):
        """Randomly select a filler item from the available candidates."""
        # Use the explicit filler placeholder to avoid ambiguity.
        return "Random Filler Appliance"

    def set_selected_settings(self):
        if not getattr(self.options, "setting_checks", None) or not self.options.setting_checks.value:
            self.selected_settings = []
            return
        mode = self.options.setting_check_mode.value
        extra_slugs = list(self.options.setting_extra_checks.value)
        selected = []
        if mode in (0, 1):  # base_only or base_and_extras
            selected.append("Base Setting")
        if mode in (1, 2):  # base_and_extras or extras_only
            for slug in extra_slugs:
                display = _setting_slug_to_display.get(slug)
                if display and display not in selected:
                    selected.append(display)
        self.selected_settings = selected

    def set_selected_dishes(self):
        dish_count = self.options.dish.value
        try:
            from .Locations import dish_dictionary
            all_dishes = list(dish_dictionary.values())
        except Exception:
            all_dishes = [
                "Salad", "Steak", "Burger", "Coffee", "Pizza", "Dumplings", "Turkey",
                "Pie", "Cakes", "Spaghetti", "Fish", "Tacos", "Hot Dogs", "Breakfast", "Stir Fry",
                "Sandwiches", "Sundaes", "Fajitas"
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
        # Deterministic per-seed random selection, without replacement
        self.selected_dishes = self.random.sample(all_dishes, k=min(dish_count, len(all_dishes)))

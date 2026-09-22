from typing import TYPE_CHECKING
import math
import sys

# Increase recursion limit to allow deep day chains (up to 1000). Default (~1000) is borderline once
# Archipelago stack usage adds frames. Set higher to prevent RecursionError.
sys.setrecursionlimit(5000)

from BaseClasses import Location, Entrance
from .Locations import (
    DISH_LOCATIONS,
    dish_dictionary
)

if TYPE_CHECKING:
    from . import PlateUpWorld

# All speed upgrade item names used across both upgrade modes.
_SPEED_UPGRADE_ITEMS = [
    "Speed Upgrade Player",
    "Speed Upgrade Appliance",
    "Speed Upgrade Cook",
    "Speed Upgrade Chop",
    "Speed Upgrade Clean",
]


def _build_strict_lease_rule(world: "PlateUpWorld", leases_required: int, lease_item: str):
    """Return a strict access rule requiring only the matching lease item count."""
    player = world.player

    def rule(state):
        return state.has(lease_item, player, leases_required)

    return rule


def _build_speed_fallback_rule(world: "PlateUpWorld"):
    """Return an access rule requiring at least one speed upgrade item.
    
    Used ONLY when day_leases_enabled=false as a fallback progression requirement.
    Speed upgrades make early game significantly easier but provide less value later.
    """
    player = world.player

    def rule(state):
        return any(state.has(spd, player) for spd in _SPEED_UPGRADE_ITEMS)

    return rule

def set_rule(spot: Location | Entrance, rule):
    spot.access_rule = rule


def add_rule(spot: Location | Entrance, rule, combine="and"):
    old_rule = spot.access_rule
    if old_rule is Location.access_rule:
        spot.access_rule = rule if combine == "and" else old_rule
    else:
        if combine == "and":
            spot.access_rule = lambda state: rule(state) and old_rule(state)
        else:
            spot.access_rule = lambda state: rule(state) or old_rule(state)


def _extract_dish_day_number(name: str) -> int | None:
    if " - Day " not in name:
        return None
    try:
        return int(name.rsplit(" - Day ", 1)[1])
    except ValueError:
        return None


def restrict_locations_by_progression(world: "PlateUpWorld"):
    # Chain dish day locations to require the previous day.
    # For non-starting dishes, Day 1 requires the corresponding Unlock item.
    dish_order = getattr(world, 'valid_dish_locations', [])
    # Support multiple starter dishes (free_starter_dishes > 1)
    starting_dishes = getattr(world, 'starting_dishes', [])
    if not starting_dishes:
        sd = getattr(world, 'starting_dish', None)
        starting_dishes = [sd] if sd else []

    interval = max(1, int(world.options.day_lease_interval.value))
    leases_enabled = bool(world.options.day_leases_enabled.value)
    lease_mode = world.options.day_lease_mode.value
    dishes_with_leases = set(getattr(world, 'dishes_with_leases', []))
    progressive = bool(world.options.day_leases_progressive.value)

    for i in range(len(dish_order) - 1):
        current_loc_name = dish_order[i]
        next_loc_name = dish_order[i + 1]
        if next_loc_name in world.location_name_to_id and current_loc_name in world.location_name_to_id:
            try:
                loc = world.get_location(next_loc_name)
                is_new_dish_start = next_loc_name.endswith(" - Day 1")

                if not is_new_dish_start:
                    # Next day within the same dish requires reaching the previous day.
                    # Day 1 of each dish starts its own chain — it must NOT require the
                    # previous dish's last day, or dishes stop being independent tracks
                    # (dish_order is one flat list spanning every selected dish back to back).
                    add_rule(loc, lambda state, cur=current_loc_name: state.can_reach(cur, "Location", world.player))
                else:
                    # If next is Day 1 of a non-starting dish, require Unlock
                    dish_name = next_loc_name.rsplit(" - Day ", 1)[0]
                    if dish_name not in starting_dishes:
                        unlock_item = f"{dish_name} Unlock"
                        add_rule(loc, lambda state, item=unlock_item: state.has(item, world.player))

                # Day Lease gating: strict when enabled, speed fallback when disabled
                day_number = _extract_dish_day_number(next_loc_name)
                if day_number:
                    if progressive:
                        leases_required = math.ceil(day_number / interval)
                    else:
                        leases_required = max(0, (day_number - 1) // interval)
                    
                    if leases_required > 0:
                        if leases_enabled:
                            # Strict lease gating when leases are enabled
                            if lease_mode == 1 and dishes_with_leases:  # dish_specific
                                dish_name = next_loc_name.rsplit(" - Day ", 1)[0]
                                if dish_name in dishes_with_leases:
                                    add_rule(
                                        loc,
                                        _build_strict_lease_rule(world, leases_required, f"{dish_name} Day Lease")
                                    )
                                # else: dish is out of scope — no lease gating
                            else:  # global
                                add_rule(
                                    loc,
                                    _build_strict_lease_rule(world, leases_required, "Day Lease")
                                )
                        else:
                            # Speed upgrade fallback when leases are disabled
                            add_rule(loc, _build_speed_fallback_rule(world))
            except KeyError:
                pass


def filter_selected_dishes(world: "PlateUpWorld"):
    dish_count = world.options.dish.value
    if dish_count == 0:
        world.selected_dishes = []
        world.valid_dish_locations = []
        return

    # Do NOT re-randomize here; use the selection established earlier
    # in world.set_selected_dishes/create_items so item pool unlocks match.
    selected = getattr(world, "selected_dishes", [])

    planned_table = getattr(world, "_location_name_to_id", {})
    valid_locs = []
    for dish in selected:
        for day in range(1, 15 + 1):
            loc_name = f"{dish} - Day {day}"
            # Only include if defined and present in the planned location table used by regions
            if loc_name in DISH_LOCATIONS and loc_name in planned_table:
                valid_locs.append(loc_name)

    world.valid_dish_locations = valid_locs

def apply_rules(world: "PlateUpWorld"):
    from .World import _get_total_days  # deferred import avoids a circular import with World.py

    goal_type = world.options.goal.value

    if goal_type in (1, 2):
        # Chain day completions: each day requires the previous.
        # Bounded by the goal's actual day count/target — every "Complete Day i" up to
        # that bound is guaranteed to exist (see generate_location_table), so no
        # try/except KeyError scaffolding is needed here.
        total_days = _get_total_days(world)
        for i in range(2, total_days + 1):
            current_day = f"Complete Day {i}"
            prev_day = f"Complete Day {i-1}"
            loc_current = world.get_location(current_day)
            loc_current.access_rule = (
                lambda state, p=prev_day: state.can_reach(p, "Location", world.player)
            )
        # Chain star completions (each star requires previous star).
        # Must match generate_location_table's max_stars formula exactly (required_days // 3)
        # or this will try to chain a "Complete Star" location that was never created.
        if goal_type == 1:
            max_stars = world.options.day_count.value // 3
        else:
            max_stars = world.options.day_target.value // 3
        for i in range(2, max_stars + 1):
            current_star = f"Complete Star {i}"
            prev_star = f"Complete Star {i-1}"
            loc_current = world.get_location(current_star)
            loc_current.access_rule = (
                lambda state, p=prev_star: state.can_reach(p, "Location", world.player)
            )
    else:
        # Bounded by the configured franchise_count — matches generate_location_table's
        # goal==0 branch exactly, so every location referenced below is guaranteed to exist.
        required_franchises = int(world.options.franchise_count.value)

        # Chain franchise goal completions
        for i in range(2, required_franchises + 1):
            suffix = "" if i - 1 == 1 else f" {i-1}"
            loc = world.get_location(f"Franchise {i} times")
            required_loc = f"Franchise - Complete Day 15 After Franchised{suffix}"
            loc.access_rule = lambda state, req=required_loc: state.can_reach(req, "Location", world.player)
        # Chain stars within each franchise run (each star after the first requires the previous in same run)
        star_labels = ["First Star", "Second Star", "Third Star", "Fourth Star", "Fifth Star"]
        for run in range(required_franchises):
            suffix = "" if run == 0 else (" After Franchised" if run == 1 else f" After Franchised {run}")
            # Build full names
            for idx in range(1, len(star_labels)):
                prev_name = f"Franchise - {star_labels[idx-1]}{suffix}"
                cur_name = f"Franchise - {star_labels[idx]}{suffix}"
                loc_current = world.get_location(cur_name)
                loc_current.access_rule = (
                    lambda state, p=prev_name: state.can_reach(p, "Location", world.player)
                )

        # Gate franchise day completion locations by the Day Lease item. This always uses
        # the flat Day Lease pool, matching Regions.py's entrance gating \u2014 dish-specific
        # leases are a separate currency that only gates each dish's own day chain.
        interval = max(1, int(world.options.day_lease_interval.value))
        leases_enabled = bool(world.options.day_leases_enabled.value)
        progressive = bool(world.options.day_leases_progressive.value)
        _franchise_lease_item = "Day Lease"

        def run_suffix(run: int) -> str:
            if run == 0:
                return ""
            if run == 1:
                return " After Franchised"
            return f" After Franchised {run}"

        def day_label(d: int) -> str:
            mapping = {1: "First Day", 2: "Second Day", 3: "Third Day", 4: "Fourth Day", 5: "Fifth Day"}
            return mapping.get(d, f"Day {d}")

        for run in range(required_franchises):
            suff = run_suffix(run)
            for d in range(1, 16):
                cur_name = f"Franchise - Complete {day_label(d)}{suff}"
                global_day = run * 15 + d
                if leases_enabled:
                    if progressive:
                        leases_required = math.ceil(global_day / interval)
                    else:
                        leases_required = (global_day - 1) // interval
                else:
                    leases_required = 0

                if d == 1:
                    prev_name = None if run == 0 else f"Franchise - Complete Day 15{run_suffix(run - 1)}"
                else:
                    prev_name = f"Franchise - Complete {day_label(d-1)}{suff}"

                try:
                    loc_cur = world.get_location(cur_name)
                    block_rule = _build_strict_lease_rule(world, leases_required, _franchise_lease_item) if leases_required > 0 else None
                    if prev_name is None:
                        if leases_required > 0:
                            loc_cur.access_rule = block_rule
                    else:
                        if leases_required > 0:
                            loc_cur.access_rule = (
                                lambda state, p=prev_name, br=block_rule: (
                                    state.can_reach(p, "Location", world.player)
                                    and br(state)
                                )
                            )
                        else:
                            loc_cur.access_rule = (
                                lambda state, p=prev_name: state.can_reach(p, "Location", world.player)
                            )
                except KeyError:
                    pass

    try:
        lose_loc = world.get_location("Lose a Run")
        if world.options.goal.value == 1:
            # Day goal: require completion of Day 1
            lose_loc.access_rule = lambda state: state.can_reach("Complete Day 1", "Location", world.player)
        else:
            # Franchise goal: require completion of the first franchise day
            lose_loc.access_rule = lambda state: state.can_reach("Franchise - Complete First Day", "Location", world.player)
    except KeyError:
        pass

    # Apply money cap rules to blueprint checks to prevent softlocks.
    # Each blueprint check has a progressive cost; expensive checks require Money Cap Increase items.
    if world.options.money_cap_enabled.value:
        bp_count = int(world.options.blueprint_check_count.value)
        if bp_count > 0:
            starting_cap = int(world.options.starting_money_cap.value)
            cap_increase_amount = int(world.options.money_cap_increase_amount.value)
            cap_increase_count = int(world.options.money_cap_increase_count.value)
            max_cap = starting_cap + cap_increase_amount * cap_increase_count
            base_price = int(world.options.blueprint_base_price.value)
            price_increase = int(world.options.blueprint_price_increase.value)
            activation_mode = world.options.money_cap_activation.value
            player = world.player
            
            # When activation is start_of_day, players can earn extra gold during service before cap applies.
            # This "earning headroom" allows purchasing checks slightly above the hard cap.
            # Use 60g for start_of_day mode (conservative estimate for in-day earning potential).
            earning_headroom = 60 if activation_mode == 1 else 0  # 1 = start_of_day

            for i in range(1, bp_count + 1):
                bp_name = f"Blueprint Check {i}"
                bp_cost = base_price + (i - 1) * price_increase
                
                # Calculate how many Money Cap Increase items are needed to afford this check.
                # Account for earning headroom when activation is start_of_day.
                effective_starting_cap = starting_cap + earning_headroom
                
                if bp_cost > effective_starting_cap:
                    if cap_increase_amount > 0:
                        # For "bonus checks" that cost more than the max achievable cap + headroom,
                        # require ALL cap increases. These can only be obtained by maximizing both
                        # cap increases and in-day earning.
                        effective_max_cap = max_cap + earning_headroom
                        if bp_cost > effective_max_cap:
                            increases_needed = cap_increase_count
                        else:
                            increases_needed = math.ceil((bp_cost - effective_starting_cap) / cap_increase_amount)
                        
                        try:
                            loc = world.get_location(bp_name)
                            # Require the player to have received the necessary Money Cap Increase items
                            loc.access_rule = (
                                lambda state, req=increases_needed: 
                                    state.has("Money Cap Increase", player, req)
                            )
                        except KeyError:
                            pass
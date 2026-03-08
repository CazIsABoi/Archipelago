from typing import TYPE_CHECKING
import math
import sys

# Increase recursion limit to allow deep day chains (up to 1000). Default (~1000) is borderline once
# Archipelago stack usage adds frames. Set higher to prevent RecursionError.
sys.setrecursionlimit(5000)

from BaseClasses import Location, Entrance
from .Locations import (
    DISH_LOCATIONS,
    SETTING_LOCATIONS,
    dish_dictionary,
    ACHIEVEMENT_LOCATIONS,
)

if TYPE_CHECKING:
    from . import PlateUpWorld

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
    starting_dishes = getattr(world, 'starting_dishes', None)
    if starting_dishes is None:
        sd = getattr(world, 'starting_dish', None)
        starting_dishes = [sd] if sd else []

    interval = max(1, int(world.options.day_lease_interval.value)) if world.options.day_leases_enabled.value else 9999
    try:
        goal_val = world.options.goal.value
        if goal_val == 2:
            required_days = max(1, int(world.options.day_target.value))
        else:
            required_days = max(1, int(world.options.day_count.value))
    except Exception:
        required_days = 1
    try:
        required_franchises = max(1, int(world.options.franchise_count.value))
    except Exception:
        required_franchises = 1
    total_progress_days = required_days if world.options.goal.value in (1, 2) else 15 * required_franchises
    total_progress_days = max(1, total_progress_days)
    try:
        speed_upgrade_count = max(0, int(world.options.player_speed_upgrade_count.value))
    except Exception:
        speed_upgrade_count = 0
    speed_slots = max(1, speed_upgrade_count)
    speed_interval = max(1, math.ceil(total_progress_days / speed_slots))
    group_size_opt = int(world.options.starting_group_size.value)
    group_item_count = max(0, group_size_opt - 1)
    group_interval = max(1, math.ceil(total_progress_days / group_item_count)) if group_item_count > 0 else 9999
    patience_item_count = int(world.options.global_patience_upgrade_count.value) if world.options.global_patience_enabled.value else 0
    patience_interval = max(1, math.ceil(total_progress_days / patience_item_count)) if patience_item_count > 0 else 9999

    for i in range(len(dish_order) - 1):
        current_loc_name = dish_order[i]
        next_loc_name = dish_order[i + 1]
        # Only set rules when both exist in this world's locations
        if next_loc_name in world.location_name_to_id and current_loc_name in world.location_name_to_id:
            try:
                loc = world.get_location(next_loc_name)
                # Next requires reaching the previous
                add_rule(loc, lambda state, cur=current_loc_name: state.can_reach(cur, "Location", world.player))

                # If next is Day 1 of a non-starting dish, require Unlock
                if next_loc_name.endswith(" - Day 1"):
                    dish_name = next_loc_name.rsplit(" - Day ", 1)[0]
                    if dish_name not in starting_dishes:
                        unlock_item = f"{dish_name} Unlock"
                        add_rule(loc, lambda state, item=unlock_item: state.has(item, world.player))

                day_number = _extract_dish_day_number(next_loc_name)
                if day_number:
                    leases_required = max(0, (day_number - 1) // interval)
                    speed_required = min(speed_upgrade_count, (day_number - 1) // speed_interval)
                    group_required = min(group_item_count, (day_number - 1) // group_interval) if group_item_count > 0 else 0
                    patience_required = min(patience_item_count, (day_number - 1) // patience_interval) if patience_item_count > 0 else 0
                    add_rule(
                        loc,
                        lambda state, req=leases_required, spd=speed_required, grp=group_required, pat=patience_required: (
                            state.has("Day Lease", world.player, req)
                            and state.has("Speed Upgrade Player", world.player, spd)
                            and state.has("Reduce Group Size", world.player, grp)
                            and state.has("Global Patience Increase", world.player, pat)
                        )
                    )
            except KeyError:
                pass

    setting_order = getattr(world, 'valid_setting_locations', [])
    for i in range(len(setting_order) - 1):
        current_loc_name = setting_order[i]
        next_loc_name = setting_order[i + 1]
        if next_loc_name in world.location_name_to_id and current_loc_name in world.location_name_to_id:
            try:
                loc = world.get_location(next_loc_name)
                add_rule(loc, lambda state, cur=current_loc_name: state.can_reach(cur, "Location", world.player))

                day_number = _extract_dish_day_number(next_loc_name)
                if day_number:
                    leases_required = max(0, (day_number - 1) // interval)
                    speed_required = min(speed_upgrade_count, (day_number - 1) // speed_interval)
                    group_required = min(group_item_count, (day_number - 1) // group_interval) if group_item_count > 0 else 0
                    patience_required = min(patience_item_count, (day_number - 1) // patience_interval) if patience_item_count > 0 else 0
                    add_rule(
                        loc,
                        lambda state, req=leases_required, spd=speed_required, grp=group_required, pat=patience_required: (
                            state.has("Day Lease", world.player, req)
                            and state.has("Speed Upgrade Player", world.player, spd)
                            and state.has("Reduce Group Size", world.player, grp)
                            and state.has("Global Patience Increase", world.player, pat)
                        )
                    )
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
    goal_val = getattr(world.options.goal, 'value', 0)
    dish_day_max = world.options.day_target.value if goal_val == 2 else 15
    valid_locs = []
    for dish in selected:
        for day in range(1, dish_day_max + 1):
            loc_name = f"{dish} - Day {day}"
            # Only include if defined and present in the planned location table used by regions
            if loc_name in DISH_LOCATIONS and loc_name in planned_table:
                valid_locs.append(loc_name)

    world.valid_dish_locations = valid_locs


def filter_selected_settings(world: "PlateUpWorld"):
    if not getattr(world.options, "setting_checks", None) or not world.options.setting_checks.value:
        world.selected_settings = []
        world.valid_setting_locations = []
        return

    selected = getattr(world, "selected_settings", [])
    planned_table = getattr(world, "_location_name_to_id", {})
    valid_locs: list[str] = []
    for setting in selected:
        for day in range(1, 16):
            loc_name = f"{setting} - Day {day}"
            if loc_name in SETTING_LOCATIONS and loc_name in planned_table:
                valid_locs.append(loc_name)

    world.valid_setting_locations = valid_locs

def apply_achievement_rules(world: "PlateUpWorld"):
    """Set access rules for achievement location checks."""
    if not getattr(world.options, 'achievement_checks', None) or not world.options.achievement_checks.value:
        return

    goal = world.options.goal.value

    # New Chef Plus — requires completing day 15
    try:
        loc = world.get_location("New Chef Plus")
        if goal == 0:  # franchise goal
            loc.access_rule = lambda state: state.can_reach(
                "Franchise - Complete Day 15", "Location", world.player
            )
        else:  # day-based goals
            loc.access_rule = lambda state: state.can_reach(
                "Complete Day 15", "Location", world.player
            )
    except KeyError:
        pass

    # Overtime achievements — only exist for day-based goals at sufficient length
    if goal != 0:
        _overtime_day_requirements = {
            "Overtime Day 5":  20,
            "Overtime Day 10": 25,
            "Overtime Day 15": 30,
        }
        for ach_name, required_day in _overtime_day_requirements.items():
            try:
                loc = world.get_location(ach_name)
                day_loc = f"Complete Day {required_day}"
                loc.access_rule = lambda state, dl=day_loc: state.can_reach(
                    dl, "Location", world.player
                )
            except KeyError:
                pass


def apply_rules(world: "PlateUpWorld"):
    goal_type = world.options.goal.value

    if goal_type in (1, 2):
        # Chain day completions for day-based goals
        if goal_type == 2:
            max_day = world.options.day_target.value
            max_stars = max_day // 3
        else:
            max_day = world.options.day_count.value
            max_stars = max_day // 3
        for i in range(2, max_day + 1):
            current_day = f"Complete Day {i}"
            prev_day = f"Complete Day {i-1}"
            try:
                loc_current = world.get_location(current_day)
                loc_current.access_rule = (
                    lambda state, p=prev_day: state.can_reach(p, "Location", world.player)
                )
            except KeyError:
                pass
        # Chain star completions (each star requires previous star)
        for i in range(2, max_stars + 1):
            current_star = f"Complete Star {i}"
            prev_star = f"Complete Star {i-1}"
            try:
                loc_current = world.get_location(current_star)
                loc_current.access_rule = (
                    lambda state, p=prev_star: state.can_reach(p, "Location", world.player)
                )
            except KeyError:
                pass
    else:
        # Chain franchise goal completions
        for i in range(2, 51):  # expanded to support up to 50 franchises
            suffix = "" if i - 1 == 1 else f" {i-1}"
            try:
                loc = world.get_location(f"Franchise {i} times")
                required_loc = f"Franchise - Complete Day 15 After Franchised{suffix}"
                loc.access_rule = lambda state, req=required_loc: state.can_reach(req, "Location", world.player)
            except KeyError:
                pass
        # Chain stars within each franchise run (each star after the first requires the previous in same run)
        star_labels = ["First Star", "Second Star", "Third Star", "Fourth Star", "Fifth Star"]
        for run in range(50):  # runs 0..49
            suffix = "" if run == 0 else (" After Franchised" if run == 1 else f" After Franchised {run}")
            # Build full names
            for idx in range(1, len(star_labels)):
                prev_name = f"Franchise - {star_labels[idx-1]}{suffix}"
                cur_name = f"Franchise - {star_labels[idx]}{suffix}"
                try:
                    loc_current = world.get_location(cur_name)
                    loc_current.access_rule = (
                        lambda state, p=prev_name: state.can_reach(p, "Location", world.player)
                    )
                except KeyError:
                    pass

        # Explicitly gate franchise day completion locations by Day Lease and Player Speed,
        # mirroring the region entrance rules so spheres reflect lease requirements.
        try:
            required_franchises = int(world.options.franchise_count.value)
        except Exception:
            required_franchises = 1
        # Lease cadence and speed-gating must match Regions.create_plateup_regions
        interval = max(1, int(world.options.day_lease_interval.value)) if world.options.day_leases_enabled.value else 9999
        # Compute speed interval across all franchise days
        total_days = 15 * required_franchises if required_franchises > 0 else 15
        speed_slots = max(1, int(world.options.player_speed_upgrade_count.value))
        # Ceiling so last chunk can be shorter
        import math as _math
        speed_interval = max(1, _math.ceil(total_days / speed_slots))
        group_size_opt = int(world.options.starting_group_size.value)
        group_item_count = max(0, group_size_opt - 1)
        group_interval = max(1, _math.ceil(total_days / group_item_count)) if group_item_count > 0 else 9999
        patience_item_count = int(world.options.global_patience_upgrade_count.value) if world.options.global_patience_enabled.value else 0
        patience_interval = max(1, _math.ceil(total_days / patience_item_count)) if patience_item_count > 0 else 9999

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
                # Leases required based on global day number (run*15 + d)
                global_day = run * 15 + d
                leases_required = (global_day - 1) // interval
                speed_required = min(int(world.options.player_speed_upgrade_count.value), (global_day - 1) // speed_interval)
                group_required = min(group_item_count, (global_day - 1) // group_interval) if group_item_count > 0 else 0
                patience_required = min(patience_item_count, (global_day - 1) // patience_interval) if patience_item_count > 0 else 0

                # Previous completion within the same run or prior run's Day 15 when d == 1 and run > 0
                if d == 1:
                    if run == 0:
                        prev_name = None
                    else:
                        prev_name = f"Franchise - Complete Day 15{run_suffix(run - 1)}"
                else:
                    prev_name = f"Franchise - Complete {day_label(d-1)}{suff}"

                try:
                    loc_cur = world.get_location(cur_name)
                    # Build rule requiring leases/speed (and previous completion if applicable)
                    if prev_name is None:
                        loc_cur.access_rule = (
                            lambda state, req=leases_required, spd=speed_required, grp=group_required, pat=patience_required: (
                                state.has("Day Lease", world.player, req)
                                and state.has("Speed Upgrade Player", world.player, spd)
                                and state.has("Reduce Group Size", world.player, grp)
                                and state.has("Global Patience Increase", world.player, pat)
                            )
                        )
                    else:
                        loc_cur.access_rule = (
                            lambda state, p=prev_name, req=leases_required, spd=speed_required, grp=group_required, pat=patience_required: (
                                state.can_reach(p, "Location", world.player)
                                and state.has("Day Lease", world.player, req)
                                and state.has("Speed Upgrade Player", world.player, spd)
                                and state.has("Reduce Group Size", world.player, grp)
                                and state.has("Global Patience Increase", world.player, pat)
                            )
                        )
                except KeyError:
                    # This day's franchise completion might not be present (e.g., beyond required runs)
                    pass

    try:
        lose_loc = world.get_location("Lose a Run")
        if world.options.goal.value in (1, 2):
            # Day-based goal: require completion of Day 1
            lose_loc.access_rule = lambda state: state.can_reach("Complete Day 1", "Location", world.player)
        else:
            # Franchise goal: require completion of the first franchise day
            lose_loc.access_rule = lambda state: state.can_reach("Franchise - Complete First Day", "Location", world.player)
    except KeyError:
        pass

    apply_achievement_rules(world)
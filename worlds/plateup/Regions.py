# Regions.py
import logging
import math
import re
from typing import TYPE_CHECKING

from BaseClasses import Region, LocationProgressType, Entrance, ItemClassification
from .Locations import (
    PlateUpLocation,
    EXCLUDED_LOCATIONS,
    FRANCHISE_LOCATION_DICT,
    DAY_LOCATION_DICT,
    DISH_LOCATIONS,
    SETTING_LOCATIONS,
    ACHIEVEMENT_LOCATIONS,
    REROLL_LOCATIONS,
    BLUEPRINT_LOCATIONS,
)

if TYPE_CHECKING:
    from . import PlateUpWorld

def create_plateup_regions(world: "PlateUpWorld"):

    menu_region = Region("Menu", world.player, world.multiworld)
    progression_region = Region("Progression", world.player, world.multiworld)
    dish_region = Region("Dish Checks", world.player, world.multiworld)
    setting_region = Region("Setting Checks", world.player, world.multiworld)
    achievement_region = Region("Achievement Checks", world.player, world.multiworld)
    reroll_region = Region("Reroll Checks", world.player, world.multiworld)
    blueprint_region = Region("Blueprint Checks", world.player, world.multiworld)

    world.multiworld.regions.extend([menu_region, progression_region, dish_region, setting_region, achievement_region, reroll_region, blueprint_region])
    menu_region.connect(progression_region)
    progression_region.connect(dish_region)
    menu_region.connect(setting_region)
    menu_region.connect(achievement_region)
    menu_region.connect(reroll_region)
    menu_region.connect(blueprint_region)

    user_goal = world.options.goal.value
    progression_locs = []

    if user_goal == 0:
        # Franchise goal: Build per-run, per-day regions with chained entrances and lease requirements.

        required_franchises = world.options.franchise_count.value
        interval = max(1, int(world.options.day_lease_interval.value)) if world.options.day_leases_enabled.value else 9999
        # Speed upgrades gating: split total franchise days into chunks based on configured player speed upgrades
        total_days = 15 * required_franchises
        speed_slots = max(1, int(world.options.player_speed_upgrade_count.value))
        speed_interval = max(1, math.ceil(total_days / speed_slots))

        group_size_opt = int(world.options.starting_group_size.value)
        group_item_count = max(0, group_size_opt - 1)
        # Push group reductions to the second half of the run so the larger group persists longer
        group_late_start = total_days // 2
        group_interval = max(1, math.ceil(max(1, total_days - group_late_start) / group_item_count)) if group_item_count > 0 else 9999

        patience_item_count = int(world.options.global_patience_upgrade_count.value) if world.options.global_patience_enabled.value else 0
        patience_interval = max(1, math.ceil(total_days / patience_item_count)) if patience_item_count > 0 else 9999
        money_cap_enabled = world.options.money_cap_enabled.value
        money_cap_item_count = int(world.options.money_cap_increase_count.value) if money_cap_enabled else 0
        table_in_logic = (
            world.options.appliance_unlocks.value and
            "Unlock Dining Table" in world.item_name_to_id
        )

        def run_suffix(run: int) -> str:
            if run == 0:
                return ""
            if run == 1:
                return " After Franchised"
            return f" After Franchised {run}"

        def day_label(d: int) -> str:
            names = {1: "First Day", 2: "Second Day", 3: "Third Day", 4: "Fourth Day", 5: "Fifth Day"}
            return names.get(d, f"Day {d}")

        star_labels = {1: "First Star", 2: "Second Star", 3: "Third Star", 4: "Fourth Star", 5: "Fifth Star"}

        # Create regions for each run/day (days 1..15 per run)
        run_day_regions = {}
        for run in range(required_franchises):
            for d in range(1, 16):
                r = Region(f"Franchise Run {run+1} - Day {d}", world.player, world.multiworld)
                run_day_regions[(run, d)] = r
        world.multiworld.regions.extend(run_day_regions.values())

        # Connect Progression -> Run1 Day1
        start_to_day1 = Entrance(world.player, "Start -> Franchise Run 1 - Day 1", parent=progression_region)
        progression_region.exits.append(start_to_day1)
        start_to_day1.connect(run_day_regions[(0, 1)])

        included_names = set()

        # Helper to compute leases requirement based on global day number (run*15 + d)
        def leases_required_for(run: int, d: int) -> int:
            global_day = run * 15 + d
            return (global_day - 1) // interval

        # Chain within runs and across runs
        for run in range(required_franchises):
            suff = run_suffix(run)
            # Within-run day chaining
            for d in range(2, 16):
                prev_r = run_day_regions[(run, d - 1)]
                cur_r = run_day_regions[(run, d)]
                e = Entrance(world.player, f"Franchise Run {run+1} - Day {d-1} -> Day {d}", parent=prev_r)
                prev_r.exits.append(e)

                prev_label = day_label(d - 1)
                req = leases_required_for(run, d)
                # Speed upgrades required based on global day progression
                global_day = run * 15 + d
                speed_req = min(int(world.options.player_speed_upgrade_count.value), (global_day - 1) // speed_interval)
                grp_req = min(group_item_count, max(0, (global_day - 1 - group_late_start) // group_interval)) if group_item_count > 0 else 0
                pat_req = min(patience_item_count, (global_day - 1) // patience_interval) if patience_item_count > 0 else 0
                cap_req = min(global_day // 15, money_cap_item_count) if money_cap_enabled else 0
                tbl_req = table_in_logic and global_day >= 15

                def rule_factory(pl=prev_label, s=suff, req=req, spd=speed_req, grp=grp_req, pat=pat_req, cap=cap_req, tbl=tbl_req):
                    return lambda state: (
                        state.can_reach(f"Franchise - Complete {pl}{s}", "Location", world.player)
                        and state.has("Day Lease", world.player, req)
                        and state.has("Speed Upgrade Player", world.player, spd)
                        and state.has("Reduce Group Size", world.player, grp)
                        and state.has("Global Patience Increase", world.player, pat)
                        and state.has("Money Cap Increase", world.player, cap)
                        and (state.has("Unlock Dining Table", world.player) if tbl else True)
                    )

                e.access_rule = rule_factory()
                try:
                    world.multiworld.register_indirect_condition(prev_r, e)
                except Exception:
                    pass
                e.connect(cur_r)

            # Cross-run chaining: last day 15 -> next run day 1
            if run + 1 < required_franchises:
                prev_r = run_day_regions[(run, 15)]
                cur_r = run_day_regions[(run + 1, 1)]
                e = Entrance(world.player, f"Franchise Run {run+1} - Day 15 -> Run {run+2} - Day 1", parent=prev_r)
                prev_r.exits.append(e)

                prev_label = day_label(15)  # "Day 15"
                # Entering next run Day 1 corresponds to global day 15*run + 16
                req = leases_required_for(run + 1, 1)
                global_day = (run + 1) * 15 + 1
                speed_req = min(int(world.options.player_speed_upgrade_count.value), (global_day - 1) // speed_interval)
                grp_req = min(group_item_count, max(0, (global_day - 1 - group_late_start) // group_interval)) if group_item_count > 0 else 0
                pat_req = min(patience_item_count, (global_day - 1) // patience_interval) if patience_item_count > 0 else 0
                cap_req = min(global_day // 15, money_cap_item_count) if money_cap_enabled else 0
                tbl_req = table_in_logic and global_day >= 15
                prev_suff = suff

                def next_run_rule_factory(pl=prev_label, ps=prev_suff, req=req, spd=speed_req, grp=grp_req, pat=pat_req, cap=cap_req, tbl=tbl_req):
                    return lambda state: (
                        state.can_reach(f"Franchise - Complete {pl}{ps}", "Location", world.player)
                        and state.has("Day Lease", world.player, req)
                        and state.has("Speed Upgrade Player", world.player, spd)
                        and state.has("Reduce Group Size", world.player, grp)
                        and state.has("Global Patience Increase", world.player, pat)
                        and state.has("Money Cap Increase", world.player, cap)
                        and (state.has("Unlock Dining Table", world.player) if tbl else True)
                    )

                e.access_rule = next_run_rule_factory()
                try:
                    world.multiworld.register_indirect_condition(prev_r, e)
                except Exception:
                    pass
                e.connect(cur_r)

        # Place franchise day locations into their regions (days 1..15 per run) and create Star regions
        for run in range(required_franchises):
            suff = run_suffix(run)
            for d in range(1, 16):
                label = day_label(d)
                name = f"Franchise - Complete {label}{suff}"
                loc_id = FRANCHISE_LOCATION_DICT.get(name)
                if loc_id is None:
                    continue
                r = run_day_regions[(run, d)]
                loc = PlateUpLocation(world.player, name, loc_id, parent=r)
                loc.sphere = (run * 15 + d - 1) // interval
                if loc_id in EXCLUDED_LOCATIONS:
                    loc.progress_type = LocationProgressType.EXCLUDED
                r.locations.append(loc)
                progression_locs.append(name)
                included_names.add(name)

            # Also create Star regions and connect from the day where they occur (3,6,9,12,15)
            for s, label in star_labels.items():
                star_day = s * 3
                name = f"Franchise - {label}{suff}"
                loc_id = FRANCHISE_LOCATION_DICT.get(name)
                if loc_id is None:
                    continue
                source_r = run_day_regions[(run, star_day)]
                star_region = Region(f"Franchise Run {run+1} - Star {s}", world.player, world.multiworld)
                world.multiworld.regions.append(star_region)
                # Entrance from the star day to the Star region; requires reaching that day's completion
                e = Entrance(world.player, f"Run {run+1} Day {star_day} -> Star {s}", parent=source_r)
                source_r.exits.append(e)
                prev_label = day_label(star_day)
                def star_rule_factory(pl=prev_label, suf=suff):
                    return lambda state: state.can_reach(f"Franchise - Complete {pl}{suf}", "Location", world.player)
                e.access_rule = star_rule_factory()
                try:
                    world.multiworld.register_indirect_condition(source_r, e)
                except Exception:
                    pass
                e.connect(star_region)

                loc = PlateUpLocation(world.player, name, loc_id, parent=star_region)
                loc.sphere = (run * 15 + star_day - 1) // interval
                if loc_id in EXCLUDED_LOCATIONS:
                    loc.progress_type = LocationProgressType.EXCLUDED
                star_region.locations.append(loc)
                progression_locs.append(name)
                included_names.add(name)

        # Place franchise milestone locations (Franchise i times) in the last day of that franchise (day 15)
        for i in range(1, required_franchises + 1):
            name = f"Franchise {i} times"
            loc_id = FRANCHISE_LOCATION_DICT.get(name)
            if loc_id is None:
                continue
            r = run_day_regions[(i - 1, 15)]
            loc = PlateUpLocation(world.player, name, loc_id, parent=r)
            loc.sphere = (i * 15 - 1) // interval  # last day of that franchise
            if loc_id in EXCLUDED_LOCATIONS:
                loc.progress_type = LocationProgressType.EXCLUDED
            r.locations.append(loc)
            progression_locs.append(name)
            included_names.add(name)

        # Ensure the single global "Lose a Run" location exists and is gated by completing Day 1.
        # Place it in the region reachable after Day 1 (i.e., Day 2 entrance), so players
        # cannot cheese access before completing the first day.
        try:
            lose_loc_id = FRANCHISE_LOCATION_DICT.get("Lose a Run") or DAY_LOCATION_DICT.get("Lose a Run")
            if lose_loc_id is not None:
                # Attach from Run 1 Day 1 so it's gated by completing that day.
                src_region = run_day_regions.get((0, 1))
                if src_region is not None:
                    lose_region = Region("Lose a Run", world.player, world.multiworld)
                    world.multiworld.regions.append(lose_region)
                    e = Entrance(world.player, "Day 1 -> Lose a Run", parent=src_region)
                    src_region.exits.append(e)
                    # Require completion of the first day (first run) to enter Lose a Run
                    e.access_rule = lambda state: state.can_reach("Franchise - Complete First Day", "Location", world.player)
                    try:
                        world.multiworld.register_indirect_condition(src_region, e)
                    except Exception:
                        pass
                    e.connect(lose_region)
                    loc = PlateUpLocation(world.player, "Lose a Run", lose_loc_id, parent=lose_region)
                    lose_region.locations.append(loc)
                    progression_locs.append("Lose a Run")
        except Exception:
            pass

        # Exclude any franchise locations not included
        for name, loc_id in FRANCHISE_LOCATION_DICT.items():
            if name not in included_names:
                world.excluded_locations.add(loc_id)

    elif user_goal in (1, 2):
        # Day goal (complete_x_days or reach_day_x_with_dishes):
        # Build one region per day with chained entrances and lease requirements.
        # Exclude all franchise locations
        for loc_id in FRANCHISE_LOCATION_DICT.values():
            world.excluded_locations.add(loc_id)

        if user_goal == 2:
            required_days = world.options.day_target.value
        else:
            required_days = world.options.day_count.value
        interval = max(1, int(world.options.day_lease_interval.value)) if world.options.day_leases_enabled.value else 9999
        # Use floor here; only create stars that correspond to an existing day (star*3)
        max_stars = required_days // 3
        # Speed upgrades gating: split required_days into chunks based on configured player speed upgrades
        speed_slots = max(1, int(world.options.player_speed_upgrade_count.value))
        speed_interval = max(1, math.ceil(required_days / speed_slots))

        group_size_opt = int(world.options.starting_group_size.value)
        group_item_count = max(0, group_size_opt - 1)
        # Push group reductions to the second half of the run so the larger group persists longer
        group_late_start = required_days // 2
        group_interval = max(1, math.ceil(max(1, required_days - group_late_start) / group_item_count)) if group_item_count > 0 else 9999

        patience_item_count = int(world.options.global_patience_upgrade_count.value) if world.options.global_patience_enabled.value else 0
        patience_interval = max(1, math.ceil(required_days / patience_item_count)) if patience_item_count > 0 else 9999
        money_cap_enabled = world.options.money_cap_enabled.value
        money_cap_item_count = int(world.options.money_cap_increase_count.value) if money_cap_enabled else 0
        table_in_logic = (
            world.options.appliance_unlocks.value and
            "Unlock Dining Table" in world.item_name_to_id
        )

        # Create per-day regions
        day_regions = {}
        for day in range(1, required_days + 1):
            r = Region(f"Day {day}", world.player, world.multiworld)
            day_regions[day] = r
        world.multiworld.regions.extend(day_regions.values())

        # Connect starting point to Day 1
        start_to_day1 = Entrance(world.player, "Start -> Day 1", parent=progression_region)
        progression_region.exits.append(start_to_day1)
        start_to_day1.connect(day_regions[1])

        # Chain Day N -> Day N+1
        for day in range(2, required_days + 1):
            prev_region = day_regions[day - 1]
            cur_region = day_regions[day]
            e = Entrance(world.player, f"Day {day-1} -> Day {day}", parent=prev_region)
            prev_region.exits.append(e)

            # Leases required to ENTER day d: floor((d-1)/interval)
            leases_required = (day - 1) // interval
            # Speed upgrades required to ENTER day d: floor((d-1)/speed_interval), capped at configured count
            speed_required = min(int(world.options.player_speed_upgrade_count.value), (day - 1) // speed_interval)
            group_size_required = min(group_item_count, max(0, (day - 1 - group_late_start) // group_interval)) if group_item_count > 0 else 0
            patience_required = min(patience_item_count, (day - 1) // patience_interval) if patience_item_count > 0 else 0
            day_money_cap_req = min(day // 15, money_cap_item_count) if money_cap_enabled else 0
            day_needs_table = table_in_logic and day >= 15

            # Access requires completion of previous day (location sits in source region => safe)
            def entrance_rule_factory(d=day, req=leases_required, spd=speed_required, grp=group_size_required, pat=patience_required, cap=day_money_cap_req, tbl=day_needs_table):
                return lambda state: (
                    state.can_reach(f"Complete Day {d-1}", "Location", world.player)
                    and state.has("Day Lease", world.player, req)
                    and state.has("Speed Upgrade Player", world.player, spd)
                    and state.has("Reduce Group Size", world.player, grp)
                    and state.has("Global Patience Increase", world.player, pat)
                    and state.has("Money Cap Increase", world.player, cap)
                    and (state.has("Unlock Dining Table", world.player) if tbl else True)
                )

            e.access_rule = entrance_rule_factory()
            # Tell the generator to re-check when prev region becomes accessible (belt-and-suspenders)
            try:
                world.multiworld.register_indirect_condition(prev_region, e)
            except Exception:
                pass
            e.connect(cur_region)

        # Place day locations into their corresponding regions
        for day in range(1, required_days + 1):
            loc_name = f"Complete Day {day}"
            loc_id = DAY_LOCATION_DICT.get(loc_name)
            if loc_id is None:
                continue
            loc = PlateUpLocation(world.player, loc_name, loc_id, parent=day_regions[day])
            # Sphere based on lease interval, not hardcoded 5-day blocks
            loc.sphere = (day - 1) // interval
            if loc_id in EXCLUDED_LOCATIONS:
                loc.progress_type = LocationProgressType.EXCLUDED
            day_regions[day].locations.append(loc)
            progression_locs.append(loc_name)

        # Create Star regions and connect from their respective day (star*3)
        for star in range(1, max_stars + 1):
            loc_name = f"Complete Star {star}"
            loc_id = DAY_LOCATION_DICT.get(loc_name)
            if loc_id is None:
                continue
            target_day = star * 3
            # Guard against any mismatch; skip if target day wasn't created
            if target_day not in day_regions:
                continue
            source_r = day_regions[target_day]
            star_region = Region(f"Star {star}", world.player, world.multiworld)
            world.multiworld.regions.append(star_region)
            e = Entrance(world.player, f"Day {target_day} -> Star {star}", parent=source_r)
            source_r.exits.append(e)
            def day_star_rule_factory(d=target_day):
                return lambda state: state.can_reach(f"Complete Day {d}", "Location", world.player)
            e.access_rule = day_star_rule_factory()
            try:
                world.multiworld.register_indirect_condition(source_r, e)
            except Exception:
                pass
            e.connect(star_region)

            loc = PlateUpLocation(world.player, loc_name, loc_id, parent=star_region)
            loc.sphere = (target_day - 1) // interval
            if loc_id in EXCLUDED_LOCATIONS:
                loc.progress_type = LocationProgressType.EXCLUDED
            star_region.locations.append(loc)
            progression_locs.append(loc_name)

        # Ensure the single global "Lose a Run" location exists and is gated by completing Day 1.
        # Place it as reachable after Day 1 so that the entrance requires completing Day 1 first.
        try:
            lose_loc_id = DAY_LOCATION_DICT.get("Lose a Run") or FRANCHISE_LOCATION_DICT.get("Lose a Run")
            if lose_loc_id is not None:
                # Only create if we have at least Day 1
                if 1 in day_regions:
                    src_region = day_regions.get(1)
                    if src_region is not None:
                        lose_region = Region("Lose a Run", world.player, world.multiworld)
                        world.multiworld.regions.append(lose_region)
                        e = Entrance(world.player, "Day 1 -> Lose a Run", parent=src_region)
                        src_region.exits.append(e)
                        # Require completion of Day 1 to enter Lose a Run
                        e.access_rule = lambda state: state.can_reach("Complete Day 1", "Location", world.player)
                        try:
                            world.multiworld.register_indirect_condition(src_region, e)
                        except Exception:
                            pass
                        e.connect(lose_region)
                        loc = PlateUpLocation(world.player, "Lose a Run", lose_loc_id, parent=lose_region)
                        lose_region.locations.append(loc)
                        progression_locs.append("Lose a Run")
        except Exception:
            pass

    # Provide progression locations both as names (legacy) and as Location objects
    # The Archipelago balancer expects `world.progression_locations` to be a list of
    # location names (strings). Older code sometimes used Location objects which
    # breaks matching in the balancer. Restore the legacy shape here and keep the
    # actual Location objects on a separate attribute for debugging/inspection.
    world.progression_locations = progression_locs
    # Keep the actual Location objects available if other code wants them
    try:
        # Aggregate from all regions added in this function (progression/day/franchise regions)
        all_prog_locs = []
        for r in world.multiworld.regions:
            if r.player != world.player:
                continue
            if r.name.startswith("Day ") or r.name.startswith("Franchise Run ") or r.name.startswith("Star "):
                all_prog_locs.extend(r.locations)
        if not all_prog_locs:
            all_prog_locs = list(progression_region.locations)
        world.progression_location_objects = all_prog_locs
    except Exception:
        world.progression_location_objects = list(progression_region.locations)
    # Also keep the legacy name list under a verbose attribute for compatibility
    world.progression_location_names = progression_locs
    # Emit an info-level summary so console runs will show progression location details
    # logging.info(f"[Player {world.multiworld.player_name[world.player]}] Final progression-locs count: {len(progression_locs)}")
    # logging.info(f"[Player {world.multiworld.player_name[world.player]}] Progression-locs sample: {progression_locs[:20]}")
    # Log actual Location objects added to the progression region and their progress_type
    for loc in world.progression_location_objects:
        try:
            ptype = getattr(loc, 'progress_type', None)
        except Exception:
            ptype = None
        # logging.info(f"[Player {world.multiworld.player_name[world.player]}] Region loc: {loc.name} (id={loc.address}) progress_type={ptype} sphere={getattr(loc, 'sphere', None)}")
    # Emit a grouped summary by the sphere value we assigned for easy verification
    spheres = {}
    for loc in world.progression_location_objects:
        s = getattr(loc, 'sphere', None)
        spheres.setdefault(s, []).append(loc.name)
    for s in sorted(spheres.keys()):
        # logging.info(f"[Player {world.multiworld.player_name[world.player]}] Assigned sphere {s}: {spheres[s]}")
        pass
    # logging.debug(f"[Player {world.multiworld.player_name[world.player]}] Final progression-locs: {progression_locs}")

    # Populate Dish Checks region with configured dish locations during region creation
    try:
        dish_count = world.options.dish.value
        if dish_count > 0:
            dishes = getattr(world, "selected_dishes", None)
            if not dishes or len(dishes) != dish_count:
                try:
                    world.set_selected_dishes()
                except Exception:
                    pass
                dishes = getattr(world, "selected_dishes", [])
            goal_val = getattr(world.options.goal, 'value', 0)
            dish_day_max = world.options.day_target.value if goal_val == 2 else 15
            for dish in dishes:
                for d in range(1, dish_day_max + 1):
                    loc_name = f"{dish} - Day {d}"
                    loc_id = DISH_LOCATIONS.get(loc_name)
                    if loc_id is None:
                        continue
                    loc = PlateUpLocation(world.player, loc_name, loc_id, parent=dish_region)
                    dish_region.locations.append(loc)
    except Exception:
        pass

    try:
        if world.options.setting_checks.value:
            world.set_selected_settings()
            for setting in getattr(world, "selected_settings", []):
                for d in range(1, 16):
                    loc_name = f"{setting} - Day {d}"
                    loc_id = SETTING_LOCATIONS.get(loc_name)
                    if loc_id is None:
                        continue
                    loc = PlateUpLocation(world.player, loc_name, loc_id, parent=setting_region)
                    # Keep setting checks as optional/filler by disallowing progression items.
                    loc.item_rule = lambda item: item.classification != ItemClassification.progression
                    setting_region.locations.append(loc)
    except Exception:
        pass

    # Populate Achievement Checks region
    try:
        if getattr(world.options, 'achievement_check_mode', None) is not None and world.options.achievement_check_mode.value != 2:
            planned = getattr(world, '_location_name_to_id', {})
            for loc_name, loc_id in ACHIEVEMENT_LOCATIONS.items():
                if loc_name not in planned:
                    continue
                loc = PlateUpLocation(world.player, loc_name, loc_id, parent=achievement_region)
                achievement_region.locations.append(loc)
    except Exception:
        pass

    # Populate Reroll Checks region — each location gated by money cap level
    try:
        planned = getattr(world, '_location_name_to_id', {})
        starting_cap = int(world.options.starting_money_cap.value)
        cap_amount = int(world.options.money_cap_increase_amount.value)
        cap_enabled = world.options.money_cap_enabled.value
        for loc_name, loc_id in REROLL_LOCATIONS.items():
            if loc_name not in planned:
                continue
            cost = int(loc_name.removeprefix("Reroll Cost "))
            if cap_enabled and cap_amount > 0:
                caps_needed = max(0, math.ceil((cost - starting_cap) / cap_amount))
            else:
                caps_needed = 0
            loc = PlateUpLocation(world.player, loc_name, loc_id, parent=reroll_region)
            if caps_needed > 0:
                loc.access_rule = lambda state, n=caps_needed: state.has("Money Cap Increase", world.player, n)
            reroll_region.locations.append(loc)
    except Exception:
        pass

    # Populate Blueprint Checks region
    # Checks 1-3 are always visible (player starts with 3 blueprints in the shop).
    # Check N (N > 3) requires check N-1 to have been purchased first (it replaces the bought slot).
    # If money_cap is enabled and the blueprint's cost exceeds the current cap, Money Cap Increase items
    # are required before that blueprint is affordable.
    try:
        planned = getattr(world, '_location_name_to_id', {})
        bp_base_price = int(world.options.blueprint_base_price.value)
        bp_price_increase = int(world.options.blueprint_price_increase.value)
        bp_cap_enabled = world.options.money_cap_enabled.value
        bp_starting_cap = int(world.options.starting_money_cap.value)
        bp_cap_amount = int(world.options.money_cap_increase_amount.value)
        # Clamp caps_needed so bonus checks (just beyond the hard cap) only require all available
        # cap items rather than an impossible count — the remainder is covered by in-day gold.
        bp_cap_count = int(world.options.money_cap_increase_count.value) if bp_cap_enabled else 0
        for loc_name, loc_id in BLUEPRINT_LOCATIONS.items():
            if loc_name not in planned:
                continue
            i = int(loc_name.removeprefix("Blueprint Check "))
            cost = bp_base_price + (i - 1) * bp_price_increase
            caps_needed = (
                min(max(0, math.ceil((cost - bp_starting_cap) / bp_cap_amount)), bp_cap_count)
                if bp_cap_enabled and bp_cap_amount > 0 and cost > bp_starting_cap
                else 0
            )
            loc = PlateUpLocation(world.player, loc_name, loc_id, parent=blueprint_region)
            needs_prev = i > 3
            if needs_prev and caps_needed > 0:
                prev = f"Blueprint Check {i - 1}"
                def _bp_rule(state, p=prev, n=caps_needed):
                    return (
                        state.can_reach(p, "Location", world.player)
                        and state.has("Money Cap Increase", world.player, n)
                    )
                loc.access_rule = _bp_rule
            elif needs_prev:
                prev = f"Blueprint Check {i - 1}"
                loc.access_rule = lambda state, p=prev: state.can_reach(p, "Location", world.player)
            elif caps_needed > 0:
                loc.access_rule = lambda state, n=caps_needed: state.has("Money Cap Increase", world.player, n)
            blueprint_region.locations.append(loc)
    except Exception:
        pass
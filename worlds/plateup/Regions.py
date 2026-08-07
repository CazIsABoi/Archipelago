# Regions.py
import logging
import math
import re
from typing import TYPE_CHECKING

from BaseClasses import Region, LocationProgressType, Entrance 
from .Locations import (
    PlateUpLocation,
    EXCLUDED_LOCATIONS,
    FRANCHISE_LOCATION_DICT,
    DAY_LOCATION_DICT,
    DISH_LOCATIONS,
    BLUEPRINT_LOCATIONS,
    SETTING_LOCATIONS,
    EXTRA_SETTING_LOCATIONS,
    _setting_slug_to_display,
)

if TYPE_CHECKING:
    from . import PlateUpWorld
    
# Import after TYPE_CHECKING to avoid circular import
from .World import _get_dishes_with_leases

def create_plateup_regions(world: "PlateUpWorld"):

    menu_region = Region("Menu", world.player, world.multiworld)
    progression_region = Region("Progression", world.player, world.multiworld)
    dish_region = Region("Dish Checks", world.player, world.multiworld)

    world.multiworld.regions.extend([menu_region, progression_region, dish_region])
    menu_region.connect(progression_region)
    progression_region.connect(dish_region)

    user_goal = world.options.goal.value
    progression_locs = []

    # Determine which item (if any) gates day-tier progression entrances.
    # Dish-specific mode: each dish's lease items cover that dish's day chain (days 1-15).
    # Overtime Day Lease covers days that exceed dish-lease capacity:
    #   overtime_days = max(0, total_days - 15 * num_dishes_with_leases)
    # If overtime_days == 0 every day is already covered by dish leases — no entrance gating needed.
    # Goal 2 uses dish leases only; entrance rules never require a lease item.
    # Global mode: Day Lease (unchanged).
    # When day_leases_enabled is false, no lease items are created, so skip lease gating entirely.
    _leases_enabled = bool(world.options.day_leases_enabled.value)
    _is_dish_specific = (
        _leases_enabled
        and world.options.day_lease_mode.value == 1
        and world.options.dish.value > 0
        and bool(getattr(world, 'selected_dishes', []))
    )

    # Mirror World.py's total_days computation.
    if user_goal == 0:
        _total_days_for_lease = 15 * int(world.options.franchise_count.value)
    elif user_goal == 2:
        _total_days_for_lease = int(world.options.day_target.value)
    else:
        _total_days_for_lease = int(world.options.day_count.value)

    # Use shared helper to determine which dishes get lease items (BUG FIX #3)
    dishes_with_leases_list = _get_dishes_with_leases(world)
    _dishes_with_leases_count = len(dishes_with_leases_list)
    
    if _is_dish_specific:
        _overtime_days = max(0, _total_days_for_lease - 15 * _dishes_with_leases_count)
    else:
        _overtime_days = 0

    if not _leases_enabled:
        _day_lease_item: str | None = None  # No lease items when day_leases_enabled=false
    elif _is_dish_specific and user_goal == 2:
        _day_lease_item = None  # dish leases are sufficient for goal 2
    elif _is_dish_specific and _overtime_days > 0:
        _day_lease_item = "Overtime Day Lease"
    elif _is_dish_specific:
        _day_lease_item = None  # dish leases cover every day — no extra gating needed
    else:
        _day_lease_item = "Day Lease"

    if user_goal == 0:
        # Franchise goal: Build per-run, per-day regions with chained entrances and lease requirements.
        # Exclude all day-goal locations (use per-world set to avoid cross-test pollution)
        for loc_id in DAY_LOCATION_DICT.values():
            world.excluded_locations.add(loc_id)

        required_franchises = world.options.franchise_count.value
        interval = max(1, int(world.options.day_lease_interval.value))

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

        # Helper to compute leases requirement based on global day number (run*15 + d).
        # In overtime mode, only global days beyond the dish-lease cap require a lease.
        def leases_required_for(run: int, d: int) -> int:
            global_day = run * 15 + d
            if _day_lease_item == "Overtime Day Lease":
                return max(0, math.ceil((global_day - 15 * _dishes_with_leases_count) / interval))
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

                def rule_factory(pl=prev_label, s=suff, req=req, lit=_day_lease_item):
                    if lit:
                        return lambda state: (
                            state.can_reach(f"Franchise - Complete {pl}{s}", "Location", world.player)
                            and state.has(lit, world.player, req)
                        )
                    return lambda state: state.can_reach(f"Franchise - Complete {pl}{s}", "Location", world.player)

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
                prev_suff = suff

                def next_run_rule_factory(pl=prev_label, ps=prev_suff, req=req, lit=_day_lease_item):
                    if lit:
                        return lambda state: (
                            state.can_reach(f"Franchise - Complete {pl}{ps}", "Location", world.player)
                            and state.has(lit, world.player, req)
                        )
                    return lambda state: state.can_reach(f"Franchise - Complete {pl}{ps}", "Location", world.player)

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
                    loc.progress_type = LocationProgressType.EXCLUDED
                    lose_region.locations.append(loc)
                    progression_locs.append("Lose a Run")
        except Exception:
            pass

        # Exclude any franchise locations not included
        for name, loc_id in FRANCHISE_LOCATION_DICT.items():
            if name not in included_names:
                world.excluded_locations.add(loc_id)

    elif user_goal == 1:
        # Day goal: Build one region per day with chained entrances and lease requirements.
        # Exclude all franchise locations
        for loc_id in FRANCHISE_LOCATION_DICT.values():
            world.excluded_locations.add(loc_id)

        required_days = world.options.day_count.value
        interval = max(1, int(world.options.day_lease_interval.value))
        # Use floor here; only create stars that correspond to an existing day (star*3)
        max_stars = required_days // 3

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

            # Leases required to ENTER day d.
            # In overtime mode, only days that exceed dish-lease coverage need a lease;
            # earlier days have req=0 (always satisfiable) since dish leases cover them.
            if _day_lease_item == "Overtime Day Lease":
                leases_required = max(0, math.ceil((day - 15 * _dishes_with_leases_count) / interval))
            else:
                leases_required = (day - 1) // interval

            # Access requires completion of previous day (location sits in source region => safe)
            def entrance_rule_factory(d=day, req=leases_required, lit=_day_lease_item):
                if lit:
                    return lambda state: (
                        state.can_reach(f"Complete Day {d-1}", "Location", world.player)
                        and state.has(lit, world.player, req)
                    )
                return lambda state: state.can_reach(f"Complete Day {d-1}", "Location", world.player)

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
                        loc.progress_type = LocationProgressType.EXCLUDED
                        lose_region.locations.append(loc)
                        progression_locs.append("Lose a Run")
        except Exception:
            pass

    elif user_goal == 2:
        # Reach day X with dishes: same region structure as goal 1 but uses day_target.
        for loc_id in FRANCHISE_LOCATION_DICT.values():
            world.excluded_locations.add(loc_id)

        required_days = world.options.day_target.value
        interval = max(1, int(world.options.day_lease_interval.value))
        max_stars = required_days // 3

        day_regions = {}
        for day in range(1, required_days + 1):
            r = Region(f"Day {day}", world.player, world.multiworld)
            day_regions[day] = r
        world.multiworld.regions.extend(day_regions.values())

        start_to_day1 = Entrance(world.player, "Start -> Day 1", parent=progression_region)
        progression_region.exits.append(start_to_day1)
        start_to_day1.connect(day_regions[1])

        for day in range(2, required_days + 1):
            prev_region = day_regions[day - 1]
            cur_region = day_regions[day]
            e = Entrance(world.player, f"Day {day-1} -> Day {day}", parent=prev_region)
            prev_region.exits.append(e)

            leases_required = (day - 1) // interval

            def entrance_rule_factory_g2(d=day, req=leases_required, lit=_day_lease_item):
                if lit:
                    return lambda state: (
                        state.can_reach(f"Complete Day {d-1}", "Location", world.player)
                        and state.has(lit, world.player, req)
                    )
                return lambda state: state.can_reach(f"Complete Day {d-1}", "Location", world.player)

            e.access_rule = entrance_rule_factory_g2()
            try:
                world.multiworld.register_indirect_condition(prev_region, e)
            except Exception:
                pass
            e.connect(cur_region)

        for day in range(1, required_days + 1):
            loc_name = f"Complete Day {day}"
            loc_id = DAY_LOCATION_DICT.get(loc_name)
            if loc_id is None:
                continue
            loc = PlateUpLocation(world.player, loc_name, loc_id, parent=day_regions[day])
            loc.sphere = (day - 1) // interval
            if loc_id in EXCLUDED_LOCATIONS:
                loc.progress_type = LocationProgressType.EXCLUDED
            day_regions[day].locations.append(loc)
            progression_locs.append(loc_name)

        for star in range(1, max_stars + 1):
            loc_name = f"Complete Star {star}"
            loc_id = DAY_LOCATION_DICT.get(loc_name)
            if loc_id is None:
                continue
            target_day = star * 3
            if target_day not in day_regions:
                continue
            source_r = day_regions[target_day]
            star_region = Region(f"Star {star}", world.player, world.multiworld)
            world.multiworld.regions.append(star_region)
            e = Entrance(world.player, f"Day {target_day} -> Star {star}", parent=source_r)
            source_r.exits.append(e)
            def day_star_rule_factory_g2(d=target_day):
                return lambda state: state.can_reach(f"Complete Day {d}", "Location", world.player)
            e.access_rule = day_star_rule_factory_g2()
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

    # Add blueprint check and setting check locations to the progression region (all goals).
    # These are identified by checking which names in the planned location table are not yet placed.
    placed_names = {loc.name for r in world.multiworld.regions if r.player == world.player for loc in r.locations}

    # Only these check families are intentionally always attached to Progression.
    # Prevent accidentally placing unhandled core progression locations here.
    optional_setting_prefixes = tuple(f"{display} - Day " for display in _setting_slug_to_display.values())

    def is_progression_fallback_location(name: str) -> bool:
        return (
            name.startswith("Blueprint Check ")
            or name.startswith("Reroll Cost Check ")
            or name.startswith("Base Setting - Day ")
            or name.startswith(optional_setting_prefixes)
        )

    for loc_name, loc_id in world._location_name_to_id.items():
        if loc_name in placed_names:
            continue
        if not is_progression_fallback_location(loc_name):
            continue
        loc = PlateUpLocation(world.player, loc_name, loc_id, parent=progression_region)
        progression_region.locations.append(loc)

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
            for dish in dishes:
                for d in range(1, 16):
                    loc_name = f"{dish} - Day {d}"
                    loc_id = DISH_LOCATIONS.get(loc_name)
                    if loc_id is None:
                        continue
                    loc = PlateUpLocation(world.player, loc_name, loc_id, parent=dish_region)
                    dish_region.locations.append(loc)
    except Exception:
        pass
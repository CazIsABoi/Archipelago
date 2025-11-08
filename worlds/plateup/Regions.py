# Regions.py
import logging
import math
import re
from typing import TYPE_CHECKING

from BaseClasses import Region, LocationProgressType  # <-- IMPORT LocationProgressType
from .Locations import (
    PlateUpLocation,
    EXCLUDED_LOCATIONS,
    FRANCHISE_LOCATION_DICT,
    DAY_LOCATION_DICT
)

if TYPE_CHECKING:
    from . import PlateUpWorld

def create_plateup_regions(world: "PlateUpWorld"):

    menu_region = Region("Menu", world.player, world.multiworld)
    progression_region = Region("Progression", world.player, world.multiworld)
    dish_region = Region("Dish Checks", world.player, world.multiworld)

    world.multiworld.regions.extend([menu_region, progression_region, dish_region])
    menu_region.connect(progression_region)
    progression_region.connect(dish_region)

    user_goal = world.options.goal.value
    progression_locs = []

    if user_goal == 0:
        # Franchise goal
        for loc_id in DAY_LOCATION_DICT.values():
            EXCLUDED_LOCATIONS.add(loc_id)

        required_franchises = world.options.franchise_count.value

        def run_index_from_name(n: str):
            if not n.startswith("Franchise - "):
                return None
            if " After Franchised" not in n:
                return 0
            suffix_part = n.split(" After Franchised", 1)[1]
            if suffix_part == "":
                return 1
            suffix_part = suffix_part.strip()
            if suffix_part.isdigit():
                return int(suffix_part)
            return None

        for name, loc_id in FRANCHISE_LOCATION_DICT.items():
            include = False
            if name.startswith("Franchise ") and name.endswith(" times"):
                try:
                    count = int(name.removeprefix("Franchise ").removesuffix(" times"))
                    include = count <= required_franchises
                except ValueError:
                    include = False
            else:
                run_idx = run_index_from_name(name)
                if run_idx is not None and (run_idx + 1) <= required_franchises:
                    include = True

            if include:
                loc = PlateUpLocation(world.player, name, loc_id, parent=progression_region)

                # Determine sphere based on day blocks and franchise run index.
                # Sphere 0 => days 1-5 (no leases). Each 5-day block increments base lease count by 1.
                # For franchise runs, each additional franchise run adds +3 leases (offset = run_idx * 3).
                # The first franchise run (run_idx == 0) therefore uses only the base block values.
                try:
                    # Extract run index using the helper above (0 for first run)
                    run_idx = run_index_from_name(name)
                except Exception:
                    run_idx = 0

                sphere = 0
                # Day-style labels: try to extract a day number first
                day_match = re.search(r"Complete Day (\d+)", name)
                if day_match:
                    day = int(day_match.group(1))
                    base = (day - 1) // 5
                    sphere = base + (run_idx * 3)
                else:
                    # Check for textual day labels (First/Second/Third/Fourth/Fifth Day)
                    if "First Day" in name:
                        day = 1
                    elif "Second Day" in name:
                        day = 2
                    elif "Third Day" in name:
                        day = 3
                    elif "Fourth Day" in name:
                        day = 4
                    elif "Fifth Day" in name:
                        day = 5
                    else:
                        day = None

                    if day is not None:
                        base = (day - 1) // 5
                        sphere = base + (run_idx * 3)
                    else:
                        # Star labels (First Star...Fifth Star) or other franchise entries:
                        # map them to the end of the 15-day block for the run (i.e. base=2)
                        if "Star" in name:
                            sphere = 2 + (run_idx * 3)

                loc.sphere = sphere

                # Mark as excluded if explicitly listed; otherwise leave default progress_type
                if loc_id in EXCLUDED_LOCATIONS:
                    loc.progress_type = LocationProgressType.EXCLUDED
                progression_region.locations.append(loc)
                progression_locs.append(name)
            else:
                world.excluded_locations.add(loc_id)

    elif user_goal == 1:
        # Day goal
        # Exclude all franchise locations
        for loc_id in FRANCHISE_LOCATION_DICT.values():
            world.excluded_locations.add(loc_id)

        required_days = world.options.day_count.value
        max_stars = math.ceil(required_days / 3)

        # Only add "Complete Day" locations that are within the required days
        for name, loc_id in DAY_LOCATION_DICT.items():
            if name.startswith("Complete Day "):
                day = int(name.removeprefix("Complete Day ").strip())
                if day <= required_days:
                    loc = PlateUpLocation(world.player, name, loc_id, parent=progression_region)
                    # Sphere mapping for day goal: sphere = floor((day-1)/5)
                    loc.sphere = (day - 1) // 5
                    # Mark as excluded if explicitly listed; otherwise leave default progress_type
                    if loc_id in EXCLUDED_LOCATIONS:
                        loc.progress_type = LocationProgressType.EXCLUDED
                    progression_locs.append(name)
                    progression_region.locations.append(loc)
                else:
                    world.excluded_locations.add(loc_id)

        # Only add "Complete Star" locations that are within the allowed stars
        for name, loc_id in DAY_LOCATION_DICT.items():
            if name.startswith("Complete Star "):
                star = int(name.removeprefix("Complete Star ").strip())
                if star <= max_stars:
                    loc = PlateUpLocation(world.player, name, loc_id, parent=progression_region)
                    # Map star to the day it represents (each star ~= 3 days). Use the last day
                    # of that star to determine the lease block so progression gating continues.
                    last_day_of_star = star * 3
                    loc.sphere = (last_day_of_star - 1) // 5
                    # Mark as excluded if explicitly listed; otherwise leave default progress_type
                    if loc_id in EXCLUDED_LOCATIONS:
                        loc.progress_type = LocationProgressType.EXCLUDED
                    progression_locs.append(name)
                    progression_region.locations.append(loc)
                else:
                    world.excluded_locations.add(loc_id)

    world.progression_locations = progression_locs
    # Emit an info-level summary so console runs will show progression location details
    logging.info(f"[Player {world.multiworld.player_name[world.player]}] Final progression-locs count: {len(progression_locs)}")
    logging.info(f"[Player {world.multiworld.player_name[world.player]}] Progression-locs sample: {progression_locs[:20]}")
    # Log actual Location objects added to the progression region and their progress_type
    for loc in progression_region.locations:
        try:
            ptype = getattr(loc, 'progress_type', None)
        except Exception:
            ptype = None
        logging.info(f"[Player {world.multiworld.player_name[world.player]}] Region loc: {loc.name} (id={loc.address}) progress_type={ptype} sphere={getattr(loc, 'sphere', None)}")
    logging.debug(f"[Player {world.multiworld.player_name[world.player]}] Final progression-locs: {progression_locs}")
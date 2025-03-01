import typing
from BaseClasses import MultiWorld, Location
from Options import Accessibility

if typing.TYPE_CHECKING:
    import BaseClasses

    CollectionRule = typing.Callable[[BaseClasses.CollectionState], bool]
    ItemRule = typing.Callable[[BaseClasses.Item], bool]
else:
    CollectionRule = typing.Callable[[object], bool]
    ItemRule = typing.Callable[[object], bool]


def set_rule(spot: typing.Union["BaseClasses.Location", "BaseClasses.Entrance"], rule: CollectionRule):
    """Sets an access rule on a location or entrance."""
    spot.access_rule = rule


def add_rule(spot: typing.Union["BaseClasses.Location", "BaseClasses.Entrance"], rule: CollectionRule, combine="and"):
    """Adds an access rule while preserving existing ones."""
    old_rule = spot.access_rule
    if old_rule is Location.access_rule:
        spot.access_rule = rule if combine == "and" else old_rule
    else:
        if combine == "and":
            spot.access_rule = lambda state: rule(state) and old_rule(state)
        else:
            spot.access_rule = lambda state: rule(state) or old_rule(state)


def restrict_locations_by_progression(multiworld: MultiWorld, player: int):
    """Enforces a sequential progression system for PlateUp."""

    franchise_order = [
        "Lose a Run", "Complete First Day", "Complete Second Day", "Complete Third Day",
        "First Star", "Complete Fourth Day", "Complete Fifth Day", "Complete Day 6", "Second Star",
        "Complete Day 7", "Complete Day 8", "Complete Day 9", "Third Star", "Complete Day 10",
        "Complete Day 11", "Complete Day 12", "Fourth Star", "Complete Day 13", "Complete Day 14",
        "Complete Day 15", "Fifth Star", "Complete Day 16", "Complete Day 17", "Complete Day 18",
        "Complete Day 19", "Complete Day 20", "Franchise Once", "Complete First Day After Franchised",
        "Complete Second Day After Franchised", "Complete Third Day After Franchised", "First Star Franchised",
        "Complete Fourth Day After Franchised", "Complete Fifth Day After Franchised", "Complete Day 6 After Franchised",
        "Second Star Franchised", "Complete Day 7 After Franchised", "Complete Day 8 After Franchised",
        "Complete Day 9 After Franchised", "Third Star Franchised", "Complete Day 10 After Franchised",
        "Complete Day 11 After Franchised", "Complete Day 12 After Franchised", "Fourth Star Franchised",
        "Complete Day 13 After Franchised", "Complete Day 14 After Franchised", "Complete Day 15 After Franchised",
        "Fifth Star Franchised", "Complete Day 16 After Franchised", "Complete Day 17 After Franchised",
        "Complete Day 18 After Franchised", "Complete Day 19 After Franchised", "Complete Day 20 After Franchised",
        "Franchise Twice", "Complete First Day After Franchised Twice", "Complete Second Day After Franchised Twice",
        "Complete Third Day After Franchised Twice", "First Star Franchised Twice", "Complete Fourth Day After Franchised Twice",
        "Complete Fifth Day After Franchised Twice", "Complete Day 6 After Franchised Twice", "Second Star Franchised Twice",
        "Complete Day 7 After Franchised Twice", "Complete Day 8 After Franchised Twice", "Complete Day 9 After Franchised Twice",
        "Third Star Franchised Twice", "Complete Day 10 After Franchised Twice", "Complete Day 11 After Franchised Twice",
        "Complete Day 12 After Franchised Twice", "Fourth Star Franchised Twice", "Complete Day 13 After Franchised Twice",
        "Complete Day 14 After Franchised Twice", "Complete Day 15 After Franchised Twice", "Fifth Star Franchised Twice",
        "Complete Day 16 After Franchised Twice", "Complete Day 17 After Franchised Twice", "Complete Day 18 After Franchised Twice",
        "Complete Day 19 After Franchised Twice", "Complete Day 20 After Franchised Twice", "Franchise Thrice"
    ]

    plateup_world = multiworld.worlds[player]  # Get the player's world instance

    for i in range(len(franchise_order) - 1):
        current_location = franchise_order[i]
        next_location = franchise_order[i + 1]

        if next_location in plateup_world.location_name_to_id:
            try:
                loc = multiworld.get_location(next_location, player)
                loc.access_rule = lambda state, cur=current_location: state.can_reach(cur, "Location", player)
            except KeyError:
                print(f"⚠ Skipping rule for {next_location}: Not found in MultiWorld.")
        else:
            print(f"⚠ Skipping rule for {next_location}: Not in location_name_to_id.")





def apply_rules(multiworld: MultiWorld, player: int):
    """Apply all game rules for PlateUp."""
    restrict_locations_by_progression(multiworld, player)

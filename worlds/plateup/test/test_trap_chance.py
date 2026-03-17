from BaseClasses import ItemClassification
from worlds.plateup.test.bases import PlateUpTestBase

_TRAP_NAMES = {
    "Random Customer Card",
    "Patience Decrease",
    "More Customers",
    "Minimum Group Size Increase",
    "Maximum Group Size Increase",
    "EVERYTHING IS ON FIRE",
    "Super Slow",
    "Random Dish Extra",
    "Random Side Dish",
    "Tip Jar Drain",
    "Good Advertisement",
    "Card Swap",
}


class TestTrapChanceZeroDisablesTraps(PlateUpTestBase):
    """trap_chance=0 disables all traps — no trap-classified items appear."""
    options = {
        "goal": 1,
        "day_count": 30,
        "trap_chance": 0,
    }

    def test_no_traps_in_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        traps = [item for item in items if item.classification == ItemClassification.trap]
        self.assertEqual(len(traps), 0)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestTrapChanceHalf(PlateUpTestBase):
    """trap_chance=50 places traps via the percentage path in ~half the remaining filler slots."""
    options = {
        "goal": 1,
        "day_count": 30,
        "trap_chance": 50,
    }

    def test_traps_present(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        traps = [item for item in items if item.name in _TRAP_NAMES]
        self.assertGreater(len(traps), 0)

    def test_all_traps_from_valid_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        trap_items = [item for item in items if item.classification == ItemClassification.trap]
        for item in trap_items:
            self.assertIn(item.name, _TRAP_NAMES)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestTrapChanceMax(PlateUpTestBase):
    """trap_chance=100 converts all remaining filler slots to traps.

    With a day-based goal (no excluded franchise locations) and appliance/decoration unlocks
    disabled, the only post-progression items are traps — no filler-classified items remain.
    """
    options = {
        "goal": 1,
        "day_count": 30,
        "trap_chance": 100,
        "appliance_unlocks": 0,
        "decoration_unlocks": 0,
    }

    def test_no_filler_items_in_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        filler_items = [item for item in items if item.classification == ItemClassification.filler]
        self.assertEqual(len(filler_items), 0)

    def test_all_traps_from_valid_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        trap_items = [item for item in items if item.classification == ItemClassification.trap]
        self.assertGreater(len(trap_items), 0)
        for item in trap_items:
            self.assertIn(item.name, _TRAP_NAMES)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestTrapChanceZeroAlsoDisablesTraps(PlateUpTestBase):
    """trap_chance=0 disables all traps regardless of other settings."""
    options = {
        "goal": 1,
        "day_count": 30,
        "trap_chance": 0,
    }

    def test_no_traps_in_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        trap_items = [item for item in items if item.classification == ItemClassification.trap]
        self.assertEqual(len(trap_items), 0)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))

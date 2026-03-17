from worlds.plateup.test.bases import PlateUpTestBase


class TestGlobalPatienceEnabled(PlateUpTestBase):
    """When global_patience_enabled is on, exactly global_patience_upgrade_count progression items appear."""
    options = {
        "goal": 1,
        "day_count": 30,
        "global_patience_enabled": 1,
        "global_patience_upgrade_count": 5,
    }

    def test_correct_patience_item_count(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        patience_items = [item for item in items if item.name == "Global Patience Increase"]
        self.assertEqual(len(patience_items), 5)

    def test_patience_items_are_progression(self) -> None:
        from BaseClasses import ItemClassification
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        patience_items = [item for item in items if item.name == "Global Patience Increase"]
        for item in patience_items:
            self.assertEqual(item.classification, ItemClassification.progression)


class TestGlobalPatienceDisabled(PlateUpTestBase):
    """When global_patience_enabled is off, no Global Patience Increase items are placed."""
    options = {
        "goal": 1,
        "day_count": 30,
        "global_patience_enabled": 0,
    }

    def test_no_patience_items_in_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        patience_items = [item for item in items if item.name == "Global Patience Increase"]
        self.assertEqual(len(patience_items), 0)


class TestGlobalPatienceUpgradeCountVariants(PlateUpTestBase):
    """global_patience_upgrade_count=1 places exactly one item."""
    options = {
        "goal": 1,
        "day_count": 30,
        "global_patience_enabled": 1,
        "global_patience_upgrade_count": 1,
    }

    def test_single_patience_item(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        patience_items = [item for item in items if item.name == "Global Patience Increase"]
        self.assertEqual(len(patience_items), 1)


class TestGlobalPatienceDebuffBoundaryValues(PlateUpTestBase):
    """global_patience_starting_debuff at its minimum (-100) still generates successfully."""
    options = {
        "goal": 1,
        "day_count": 30,
        "global_patience_enabled": 1,
        "global_patience_starting_debuff": -100,
    }

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestGlobalPatienceDebuffZero(PlateUpTestBase):
    """global_patience_starting_debuff=0 (no penalty) still generates successfully."""
    options = {
        "goal": 1,
        "day_count": 30,
        "global_patience_enabled": 1,
        "global_patience_starting_debuff": 0,
    }

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))

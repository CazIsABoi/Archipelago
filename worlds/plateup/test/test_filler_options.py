from BaseClasses import ItemClassification
from worlds.plateup.test.bases import PlateUpTestBase


class TestPatienceFillerPercent(PlateUpTestBase):
    """patience_filler_percent=100 fills all remaining filler capacity with Patience Increase items.

    With trap_cards disabled and a day-based goal, all remaining slots after progression items
    should become Patience Increase.  No generic appliance filler should appear.
    """
    options = {
        "goal": 1,
        "day_count": 30,
        "patience_filler_percent": 100,
    }

    def test_patience_increase_present(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        patience_items = [item for item in items if item.name == "Patience Increase"]
        self.assertGreater(len(patience_items), 5)

    def test_patience_increase_is_dominant_filler(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        patience_items = [item for item in items if item.name == "Patience Increase"]
        filler_items = [item for item in items if item.classification == ItemClassification.filler]
        # Patience Increase should account for more than half the filler item pool
        self.assertGreater(len(patience_items), len(filler_items) // 2)

    def test_no_random_appliance_filler(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        appliance_filler = [item for item in items if item.name in ("Random Appliance", "Random Filler Appliance")]
        self.assertEqual(len(appliance_filler), 0)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestCustomerFillerPercent(PlateUpTestBase):
    """customer_filler_percent=100 fills all remaining filler capacity with Less Customers items."""
    options = {
        "goal": 1,
        "day_count": 30,
        "customer_filler_percent": 100,
    }

    def test_less_customers_present(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        less_customers = [item for item in items if item.name == "Less Customers"]
        self.assertGreater(len(less_customers), 5)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestGroupSizeFillerEvenSplit(PlateUpTestBase):
    """group_size_filler_percent splits the allocation evenly between Minimum and Maximum Group Size Decrease."""
    options = {
        "goal": 1,
        "day_count": 30,
        "group_size_filler_percent": 50,
    }

    def test_min_and_max_group_size_equal(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        min_gsd = sum(1 for item in items if item.name == "Minimum Group Size Decrease")
        max_gsd = sum(1 for item in items if item.name == "Maximum Group Size Decrease")
        self.assertEqual(min_gsd, max_gsd)
        self.assertGreater(min_gsd, 0)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestMessReductionPercent(PlateUpTestBase):
    """mess_reduction_percent=100 fills all remaining filler capacity with Mess Reduction items."""
    options = {
        "goal": 1,
        "day_count": 30,
        "mess_reduction_percent": 100,
    }

    def test_mess_reduction_present(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        mess_items = [item for item in items if item.name == "Mess Reduction"]
        self.assertGreater(len(mess_items), 5)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestFillerPercentBudgetNoOverflow(PlateUpTestBase):
    """All four filler percentages set to 100 must not overflow available location slots.

    Because each percentage is calculated against the budget remaining at that point (not the
    original capacity), the sum can never exceed total available filler slots.
    """
    options = {
        "goal": 1,
        "day_count": 30,
        "patience_filler_percent": 100,
        "customer_filler_percent": 100,
        "group_size_filler_percent": 100,
        "mess_reduction_percent": 100,
    }

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))

    def test_patience_increase_is_only_explicit_filler(self) -> None:
        """With patience first at 100%, budget drops to 0 before other percents run."""
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        patience_items = [item for item in items if item.name == "Patience Increase"]
        less_customers = [item for item in items if item.name == "Less Customers"]
        mess_items = [item for item in items if item.name == "Mess Reduction"]
        # patience consumes entire budget first; customer/mess should get 0
        self.assertGreater(len(patience_items), 0)
        self.assertEqual(len(less_customers), 0)
        self.assertEqual(len(mess_items), 0)

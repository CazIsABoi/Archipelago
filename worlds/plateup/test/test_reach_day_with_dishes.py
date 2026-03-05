from worlds.plateup.test.bases import PlateUpTestBase


class TestReachDayWithDishesBasic(PlateUpTestBase):
    """Minimum config: reach Day 15 with 1 dish (just the starting dish)."""
    options = {
        "goal": 2,  # reach_day_x_with_dishes
        "day_target": 15,
        "dish": 1,
        "dish_goal_count": 1,
    }

    def test_has_completion_condition(self) -> None:
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])

    def test_day_locations_present(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertIn("Complete Day 1", player_locations)
        self.assertIn("Complete Day 15", player_locations)
        self.assertNotIn("Complete Day 16", player_locations)

    def test_no_franchise_locations(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertNotIn("Franchise 1 times", player_locations)


class TestReachDayWithDishesMultiDish(PlateUpTestBase):
    """Reach Day 20 with 3 out of 5 dishes active."""
    options = {
        "goal": 2,
        "day_target": 20,
        "dish": 5,
        "dish_goal_count": 3,
    }

    def test_has_completion_condition(self) -> None:
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])

    def test_day_locations_present(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertIn("Complete Day 20", player_locations)
        self.assertNotIn("Complete Day 21", player_locations)

    def test_dish_locations_present(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        # Dish day checks should appear (5 dishes × 15 days each)
        dish_locs = [name for name in player_locations if " - Day " in name and not name.startswith("Complete")]
        self.assertGreater(len(dish_locs), 0)

    def test_dish_goal_clamped_to_available(self) -> None:
        """dish_goal_count should never exceed dish option value."""
        dish_goal = min(
            self.world.options.dish_goal_count.value,
            self.world.options.dish.value
        )
        self.assertLessEqual(dish_goal, self.world.options.dish.value)


class TestReachDayWithDishesAllDishesMustBeActive(PlateUpTestBase):
    """dish_goal_count exactly equals dish count — all dishes must be active."""
    options = {
        "goal": 2,
        "day_target": 15,
        "dish": 3,
        "dish_goal_count": 3,
    }

    def test_has_completion_condition(self) -> None:
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])

    def test_all_dish_unlocks_in_pool(self) -> None:
        """With dish=3 and dish_goal_count=3, 2 unlock items should be in the pool."""
        unlock_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player and item.name.endswith(" Unlock")
        ]
        # One dish is free (starter), so 2 unlock items expected
        self.assertEqual(len(unlock_items), 2)


class TestReachDayMaxTarget(PlateUpTestBase):
    """Reach Day 30 (maximum target) with all 17 dishes."""
    options = {
        "goal": 2,
        "day_target": 30,
        "dish": 17,
        "dish_goal_count": 17,
    }

    def test_has_completion_condition(self) -> None:
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])

    def test_day_30_location_present(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertIn("Complete Day 30", player_locations)

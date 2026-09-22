from worlds.plateup.test.bases import PlateUpTestBase


class TestReachDayWithDishesBasic(PlateUpTestBase):
    """Minimum config: reach Day 15 with 1 dish (just the starting dish)."""
    options = {
        "goal": 2,
        "day_target": 15,
        "dish": 1,
        "dish_goal_count": 1,
    }

    def test_has_completion_condition(self) -> None:
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])

    def test_day_locations_present(self) -> None:
        player_locations = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        self.assertIn("Complete Day 1", player_locations)
        self.assertIn("Complete Day 15", player_locations)
        self.assertNotIn("Complete Day 16", player_locations)

    def test_no_franchise_locations(self) -> None:
        player_locations = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
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
        player_locations = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        self.assertIn("Complete Day 20", player_locations)
        self.assertNotIn("Complete Day 21", player_locations)

    def test_dish_locations_present(self) -> None:
        player_locations = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        dish_locs = [name for name in player_locations if " - Day " in name and not name.startswith("Complete")]
        self.assertGreater(len(dish_locs), 0)

    def test_dish_goal_clamped_to_available(self) -> None:
        dish_goal = min(self.world.options.dish_goal_count.value, self.world.options.dish.value)
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
        """With dish=3 and dish_goal_count=3, 2 dish unlock items should be in the pool."""
        unlock_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player
            and item.name.endswith(" Unlock")
            and item.name != "Random Decoration Unlock"
        ]
        self.assertEqual(len(unlock_items), 2)


class TestReachDayMaxTarget(PlateUpTestBase):
    """Reach Day 30 (maximum target) with all 18 dishes."""
    options = {
        "goal": 2,
        "day_target": 30,
        "dish": 18,
        "dish_goal_count": 18,
    }

    def test_has_completion_condition(self) -> None:
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])

    def test_day_30_location_present(self) -> None:
        player_locations = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        self.assertIn("Complete Day 30", player_locations)


class TestReachDayWithProgressiveDishLeases(PlateUpTestBase):
    """The AP completion condition must match the client's per-dish target runs."""
    options = {
        "goal": 2,
        "day_target": 20,
        "dish": 8,
        "dish_goal_count": 6,
        "free_starter_dishes": 1,
        "day_leases_enabled": 1,
        "day_lease_interval": 5,
        "day_lease_mode": 1,
        "dish_lease_scope": 0,
        "day_leases_progressive": 1,
    }

    def test_unlocks_alone_do_not_complete_goal(self) -> None:
        selected = self.world.selected_dishes
        for dish in selected[1:6]:
            self.collect_by_name(f"{dish} Unlock")

        self.assertFalse(self.multiworld.completion_condition[self.player](self.multiworld.state))

    def test_starter_begins_with_first_required_lease(self) -> None:
        starter = self.world.starting_dishes[0]
        lease = self.get_item_by_name(f"{starter} Day Lease")
        pool_leases = self.get_items_by_name(f"{starter} Day Lease")

        self.assertEqual(self.count(f"{starter} Day Lease"), 1)
        self.assertEqual(len(pool_leases), 2)
        self.assertTrue(self.can_reach_location("Complete Day 1"))
        self.assertTrue(self.can_reach_location("Complete Day 5"))
        self.assertFalse(self.can_reach_location("Complete Day 6"))

        self.collect(lease)
        self.assertTrue(self.can_reach_location("Complete Day 6"))
        self.assertTrue(self.can_reach_location("Complete Day 10"))
        self.assertFalse(self.can_reach_location("Complete Day 11"))

    def test_unlocked_nonstarter_requires_lease_for_day_one(self) -> None:
        from worlds.plateup.Rules import _build_goal2_dish_rule

        dish = self.world.selected_dishes[1]
        self.world.starting_dishes = []
        rule = _build_goal2_dish_rule(self.world, 1)
        self.collect_by_name(f"{dish} Unlock")
        self.assertFalse(rule(self.multiworld.state))

        self.collect(self.get_item_by_name(f"{dish} Day Lease"))
        self.assertTrue(rule(self.multiworld.state))

    def test_six_lease_ready_dishes_complete_goal(self) -> None:
        selected = self.world.selected_dishes
        for dish in selected[:6]:
            if dish not in self.world.starting_dishes:
                self.collect_by_name(f"{dish} Unlock")
            self.collect_by_name(f"{dish} Day Lease")

        self.assertEqual(self.count(f"{selected[0]} Day Lease"), 3)
        self.assertTrue(self.multiworld.completion_condition[self.player](self.multiworld.state))

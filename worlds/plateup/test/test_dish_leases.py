"""Tests for dish-specific Day Lease items (day_lease_mode = dish_specific)."""
from worlds.plateup.test.bases import PlateUpTestBase


_BASE_OPTIONS = {
    "goal": 2,          # reach_day_x_with_dishes
    "day_target": 20,
    "day_leases_enabled": 1,
    "day_lease_interval": 5,
    # Disable optional item types to keep counts predictable.
    "enable_money_cap": 0,
    "enable_global_patience": 0,
    "appliance_unlocks": 0,
    "decoration_unlocks": 0,
    "blueprint_check_count": 0,
    "trap_chance": 0,
    "player_speed_upgrade_count": 0,
    "appliance_speed_upgrade_count": 0,
    "enable_setting_checks": 0,
    "achievement_check_mode": "none",
}


class TestDishSpecificLeasesAllDishes(PlateUpTestBase):
    """dish_specific + all_dishes: every selected dish gets ceil(15/interval) lease items."""
    options = {
        **_BASE_OPTIONS,
        "dish": 3,
        "dish_goal_count": 2,
        "free_starter_dishes": 1,
        "day_lease_mode": 1,   # dish_specific
        "dish_lease_scope": 0,  # all_dishes
    }

    def test_dish_lease_items_in_pool(self) -> None:
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        dish_leases = [i for i in items if i.name.endswith(" Day Lease")
                       and i.name not in ("Day Lease", "Overtime Day Lease")]
        # 3 dishes × ceil(15/5) = 3 × 3 = 9
        self.assertEqual(len(dish_leases), 9)

    def test_day_lease_items_still_present(self) -> None:
        """The flat Complete Day N chain is always gated by the Day Lease pool, regardless
        of day_lease_mode — dish leases only gate each dish's own day chain. Previously
        goal 2 + dish_specific created zero Day Lease items, leaving Complete Day N (and
        therefore the goal itself) reachable with no items at all."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        global_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(global_leases), 4)  # ceil(20/5)
        overtime_leases = [i for i in items if i.name == "Overtime Day Lease"]
        self.assertEqual(len(overtime_leases), 0)

    def test_item_location_balance(self) -> None:
        locs = self.multiworld.get_locations(self.player)
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        self.assertEqual(len(items), len(locs))


class TestDishSpecificLeasesAreIndependent(PlateUpTestBase):
    """Regression test: each dish's day chain must be independently reachable — giving one
    dish's own items must not require unlocking a different dish first.

    Previously, restrict_locations_by_progression chained dish day-locations as one flat
    list spanning every selected dish back-to-back, so the second dish's Day 1 silently
    required reaching the first dish's Day 15, defeating the point of dish_specific mode."""
    options = {
        **_BASE_OPTIONS,
        "dish": 2,
        "dish_goal_count": 1,
        "free_starter_dishes": 1,
        "day_lease_mode": 1,   # dish_specific
        "dish_lease_scope": 0,  # all_dishes
    }

    def test_second_dish_day1_reachable_without_first_dish_items(self) -> None:
        dish1, dish2 = self.world.selected_dishes[0], self.world.selected_dishes[1]
        # Give only what the second dish needs for itself.
        self.collect_by_name([f"{dish2} Unlock", f"{dish2} Day Lease"])
        self.assertTrue(
            self.can_reach_location(f"{dish2} - Day 1"),
            f"{dish2} - Day 1 should be reachable with only {dish2}'s own items"
        )
        # Sanity check: the first dish's later days are still gated (we gave it nothing),
        # confirming the test setup isn't accidentally granting blanket access.
        self.assertFalse(self.can_reach_location(f"{dish1} - Day 15"))


class TestDishSpecificLeasesGoalCountOnly(PlateUpTestBase):
    """goal_count_only scope: only dish_goal_count dishes receive dish-specific lease items."""
    options = {
        **_BASE_OPTIONS,
        "dish": 5,
        "dish_goal_count": 3,
        "free_starter_dishes": 1,
        "day_lease_mode": 1,   # dish_specific
        "dish_lease_scope": 1,  # goal_count_only
    }

    def test_only_goal_count_dishes_have_leases(self) -> None:
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        dish_leases = [i for i in items if i.name.endswith(" Day Lease")
                       and i.name not in ("Day Lease", "Overtime Day Lease")]
        # 3 dishes × ceil(15/5) = 9
        self.assertEqual(len(dish_leases), 9)

    def test_day_leases_still_present(self) -> None:
        """The flat Complete Day N chain is gated by Day Lease regardless of dish_lease_scope
        — goal_count_only only affects which dishes get per-dish leases, not this pool."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        global_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(global_leases), 4)  # ceil(20/5)
        overtime_leases = [i for i in items if i.name == "Overtime Day Lease"]
        self.assertEqual(len(overtime_leases), 0)

    def test_item_location_balance(self) -> None:
        locs = self.multiworld.get_locations(self.player)
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        self.assertEqual(len(items), len(locs))


class TestGlobalLeaseMode(PlateUpTestBase):
    """Global mode produces only generic Day Lease items, no dish-specific ones."""
    options = {
        **_BASE_OPTIONS,
        "dish": 3,
        "dish_goal_count": 2,
        "free_starter_dishes": 1,
        "day_lease_mode": 0,   # global
    }

    def test_no_dish_lease_items_in_pool(self) -> None:
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        dish_leases = [i for i in items if i.name.endswith(" Day Lease")]
        self.assertEqual(len(dish_leases), 0)

    def test_global_leases_present(self) -> None:
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        global_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(global_leases), 4)  # ceil(20/5)

    def test_item_location_balance(self) -> None:
        locs = self.multiworld.get_locations(self.player)
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        self.assertEqual(len(items), len(locs))


class TestDishSpecificLeasesGoalNotReachDay(PlateUpTestBase):
    """For franchise goal (goal 0) with dish_specific leases, the flat Complete Day N chain
    is gated by the Day Lease pool sized to the full total_days (franchise_count=4 → 60
    days → ceil(60/5)=12), independent of dish-specific lease coverage."""
    options = {
        **_BASE_OPTIONS,
        "goal": 0,          # franchise
        "franchise_count": 4,
        "dish": 3,
        "dish_goal_count": 1,
        "free_starter_dishes": 1,
        "day_lease_mode": 1,   # dish_specific
        "dish_lease_scope": 1,  # goal_count_only — ignored for non-goal-2
    }

    def test_all_dishes_get_leases_for_non_goal2(self) -> None:
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        dish_leases = [i for i in items if i.name.endswith(" Day Lease")
                       and i.name not in ("Day Lease", "Overtime Day Lease")]
        # All 3 dishes get leases since goal != 2 overrides goal_count_only
        self.assertEqual(len(dish_leases), 9)  # 3 × ceil(15/5)

    def test_day_leases_present_for_non_goal2(self) -> None:
        """franchise_count=4 → total_days=60 → ceil(60/5)=12 Day Lease items.
        Overtime Day Lease is never generated any more (superseded by Day Lease)."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        generic_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(generic_leases), 12)
        overtime_leases = [i for i in items if i.name == "Overtime Day Lease"]
        self.assertEqual(len(overtime_leases), 0)

    def test_item_location_balance(self) -> None:
        locs = self.multiworld.get_locations(self.player)
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        self.assertEqual(len(items), len(locs))


class TestDishSpecificLeasesGoal1Overtime(PlateUpTestBase):
    """Goal 1 (complete_x_days) with dish_specific: day_count=50, interval=5.
    The flat Complete Day N chain is gated by Day Lease sized to the full day_count
    (ceil(50/5)=10), independent of how many dishes have their own per-dish leases."""
    options = {
        **_BASE_OPTIONS,
        "goal": 1,          # complete_x_days
        "day_count": 50,
        "dish": 3,
        "dish_goal_count": 2,
        "free_starter_dishes": 1,
        "day_lease_mode": 1,   # dish_specific
        "dish_lease_scope": 0,  # all_dishes
    }

    def test_day_leases_generated(self) -> None:
        """50 days, interval 5 → ceil(50/5)=10 Day Lease items; no Overtime Day Lease."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        generic_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(generic_leases), 10)
        overtime_leases = [i for i in items if i.name == "Overtime Day Lease"]
        self.assertEqual(len(overtime_leases), 0)

    def test_dish_leases_present(self) -> None:
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        dish_leases = [i for i in items if i.name.endswith(" Day Lease")
                       and i.name not in ("Day Lease", "Overtime Day Lease")]
        # 3 dishes × ceil(15/5) = 9
        self.assertEqual(len(dish_leases), 9)

    def test_item_location_balance(self) -> None:
        locs = self.multiworld.get_locations(self.player)
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        self.assertEqual(len(items), len(locs))

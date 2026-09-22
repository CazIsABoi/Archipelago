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

    def test_generic_lease_items_still_present(self) -> None:
        """Goal 2 + dish_specific: entrance rules have no lease gating, so no generic
        Day Lease or Overtime Day Lease items are generated — only the per-dish leases."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        global_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(global_leases), 0)
        overtime_leases = [i for i in items if i.name == "Overtime Day Lease"]
        self.assertEqual(len(overtime_leases), 0)

    def test_item_location_balance(self) -> None:
        locs = self.multiworld.get_locations(self.player)
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        self.assertEqual(len(items), len(locs))


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

    def test_generic_leases_still_present(self) -> None:
        """Goal 2 + dish_specific: no generic Day Lease or Overtime Day Lease generated."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        global_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(global_leases), 0)  # goal 2 + dish_specific = no generic leases
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


class TestDishSpecificLeasesFranchiseGoal(PlateUpTestBase):
    """Franchise runs reuse each selected dish's Day 1-15 lease progression."""
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

    def test_franchise_goal_has_no_global_leases(self) -> None:
        """Franchise count does not turn fresh Day 1-15 runs into overtime days."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        overtime_leases = [i for i in items if i.name == "Overtime Day Lease"]
        self.assertEqual(len(overtime_leases), 0)
        generic_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(generic_leases), 0)

    def test_item_location_balance(self) -> None:
        locs = self.multiworld.get_locations(self.player)
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        self.assertEqual(len(items), len(locs))


class TestDishSpecificLeasesGoal1Overtime(PlateUpTestBase):
    """Goal 1 (complete_x_days) with dish_specific: day_count=50, 3 dishes, interval=5.
    overtime_days = max(0, 50 - 15*3) = 5; ceil(5/5) = 1 overtime lease.
    This matches the user’s worked example."""
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

    def test_one_overtime_lease_generated(self) -> None:
        """The user’s example: 50 days, 3 dishes, interval 5 → 1 overtime lease."""
        items = [i for i in self.multiworld.itempool if i.player == self.player]
        overtime_leases = [i for i in items if i.name == "Overtime Day Lease"]
        self.assertEqual(len(overtime_leases), 1)
        generic_leases = [i for i in items if i.name == "Day Lease"]
        self.assertEqual(len(generic_leases), 0)

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

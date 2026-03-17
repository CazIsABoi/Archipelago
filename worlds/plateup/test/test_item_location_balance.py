from worlds.plateup.test.bases import PlateUpTestBase

# Options that produce ~66 mandatory items vs only ~45 locations
# (goal=reach_day_x_with_dishes, day_target=15, heaps of speed/cap items).
_OVERFLOW_OPTIONS = {
    "goal": 2,                       # reach_day_x_with_dishes
    "day_target": 15,
    "dish": 1,
    "dish_goal_count": 1,
    "free_starter_dishes": 1,
    "day_leases_enabled": 1,
    "day_lease_interval": 5,         # ceil(15/5) = 3 leases, ceil(60/5) = 12 leases
    "player_speed_upgrade_count": 10,
    "appliance_speed_upgrade_count": 10,
    "appliance_speed_mode": 1,       # separate → 10 × 3 = 30 items
    "money_cap_enabled": 1,
    "money_cap_increase_count": 20,
    "starting_cards": 3,             # both
    "starting_cards_amount": 3,
    "achievement_check_mode": 2,     # none
}


class TestItemLocationOverflowRaisesEarly(PlateUpTestBase):
    """Validates that over-configured item counts raise a clear error instead of a FillError."""

    auto_construct = False

    def test_overflow_raises_with_message(self) -> None:
        """66 mandatory items vs 45 locations should raise before reaching fill."""
        self.options = _OVERFLOW_OPTIONS
        with self.assertRaises(Exception) as ctx:
            self.world_setup()
        error = str(ctx.exception)
        self.assertIn("mandatory items", error)
        self.assertIn("locations are available", error)

    def test_sufficient_day_target_resolves_overflow(self) -> None:
        """Raising day_target to 60 gives 105 locations vs 75 mandatory items, resolving the overflow."""
        self.options = {**_OVERFLOW_OPTIONS, "day_target": 60}
        self.world_setup()  # must not raise

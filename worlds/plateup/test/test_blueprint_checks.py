from worlds.plateup.test.bases import PlateUpTestBase


class TestBlueprintChecksDefault(PlateUpTestBase):
    """Default options: 10 blueprint checks, all affordable with default cap."""
    options = {"blueprint_check_count": 10}

    def test_blueprint_locations_present(self) -> None:
        names = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        for i in range(1, 11):
            self.assertIn(f"Blueprint Check {i}", names)

    def test_no_extra_blueprint_locations(self) -> None:
        names = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        self.assertNotIn("Blueprint Check 11", names)


class TestBlueprintChecksClampedByMoneyCapCap(PlateUpTestBase):
    """Requesting 40 checks: 11 within max cap (120g), plus ceil(11*1.3)=15 total.
    Checks 12-15 are bonus checks requiring all 5 cap items; checks 16-40 are excluded."""
    options = {
        "blueprint_check_count": 40,
        "blueprint_base_price": 20,
        "blueprint_price_increase": 10,
        "money_cap_enabled": 1,
        "starting_money_cap": 20,
        "money_cap_increase_amount": 20,
        "money_cap_increase_count": 5,  # max cap = 20 + 5*20 = 120
        # check 11 costs 120 → within cap; check 12 costs 130 → bonus; check 16 costs 170 → excluded
    }

    def test_within_cap_checks_present(self) -> None:
        names = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        for i in range(1, 12):
            self.assertIn(f"Blueprint Check {i}", names)

    def test_bonus_checks_present(self) -> None:
        """ceil(11 * 1.3) = 15, so checks 12-15 are included as bonus."""
        names = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        for i in range(12, 16):
            self.assertIn(f"Blueprint Check {i}", names)

    def test_excess_checks_excluded(self) -> None:
        names = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        for i in range(16, 41):
            self.assertNotIn(f"Blueprint Check {i}", names)

    def test_all_locations_reachable(self) -> None:
        """Bonus checks clamp to all-cap-items requirement — must be fully accessible."""
        self.test_all_state_can_reach_everything()


class TestBlueprintChecksNoCapLimit(PlateUpTestBase):
    """When money_cap_enabled is off, all requested blueprint checks are included."""
    options = {
        "blueprint_check_count": 20,
        "blueprint_base_price": 50,
        "blueprint_price_increase": 50,
        "money_cap_enabled": 0,
    }

    def test_all_requested_checks_present(self) -> None:
        names = {loc.name for loc in self.multiworld.get_locations() if loc.player == self.player}
        for i in range(1, 21):
            self.assertIn(f"Blueprint Check {i}", names)

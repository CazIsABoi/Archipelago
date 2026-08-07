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


class TestBlueprintChecksMoneyCapAccessRules(PlateUpTestBase):
    """Test that expensive blueprint checks require Money Cap Increase items to prevent softlocks."""
    options = {
        "blueprint_check_count": 10,
        "blueprint_base_price": 10,
        "blueprint_price_increase": 20,
        "money_cap_enabled": 1,
        "starting_money_cap": 20,
        "money_cap_increase_amount": 20,
        "money_cap_increase_count": 5,
        # check 1: 10g (within starting cap)
        # check 2: 30g (needs 1 cap increase: 30-20=10, ceil(10/20)=1)
        # check 3: 50g (needs 2 cap increases: 50-20=30, ceil(30/20)=2)
        # check 6: 110g (needs 5 cap increases: 110-20=90, ceil(90/20)=5)
    }

    def test_cheap_check_no_cap_required(self) -> None:
        """Blueprint Check 1 costs 10g, within starting cap of 20g."""
        loc = self.multiworld.get_location("Blueprint Check 1", self.player)
        self.assertTrue(self.multiworld.state.can_reach(loc, player=self.player))

    def test_expensive_check_requires_cap_increases(self) -> None:
        """Blueprint Check 2 costs 30g, requires 1 Money Cap Increase."""
        loc = self.multiworld.get_location("Blueprint Check 2", self.player)
        # Without any cap increases, should not be accessible
        self.assertFalse(self.multiworld.state.can_reach(loc, player=self.player))
        
        # With 1 cap increase, should be accessible
        self.collect_by_name("Money Cap Increase")
        self.assertTrue(self.multiworld.state.can_reach(loc, player=self.player))

    def test_very_expensive_check_requires_multiple_increases(self) -> None:
        """Blueprint Check 6 costs 110g, requires multiple Money Cap Increases."""
        loc = self.multiworld.get_location("Blueprint Check 6", self.player)
        
        # Without any cap increases, should not be accessible
        self.assertFalse(self.multiworld.state.can_reach(loc, player=self.player))
        
        # With all 5 increases (cap = 120), accessible
        for _ in range(5):
            self.collect_by_name("Money Cap Increase")
        self.assertTrue(self.multiworld.state.can_reach(loc, player=self.player))


class TestBlueprintChecksStartOfDayEarningHeadroom(PlateUpTestBase):
    """Test that start_of_day activation mode allows earning headroom for checks slightly above cap."""
    options = {
        "blueprint_check_count": 10,
        "blueprint_base_price": 10,
        "blueprint_price_increase": 25,
        "money_cap_enabled": 1,
        "starting_money_cap": 20,
        "money_cap_increase_amount": 20,
        "money_cap_increase_count": 5,
        "money_cap_activation": 1,  # start_of_day mode
        # With start_of_day + 60g earning headroom:
        # check 1: 10g (within starting cap + headroom = 80g)
        # check 3: 60g (within starting cap + headroom = 80g, no increases needed)
        # check 4: 85g (needs 1 increase: 85-80=5, ceil(5/20)=1, giving cap 40+60=100)
        # check 5: 110g (needs 2 increases: 110-80=30, ceil(30/20)=2, giving cap 60+60=120)
    }

    def test_check_within_earning_headroom_no_increases_needed(self) -> None:
        """Blueprint Check 3 costs 60g, within starting cap (20g) + earning headroom (60g)."""
        loc = self.multiworld.get_location("Blueprint Check 3", self.player)
        # Should be accessible without any cap increases due to earning headroom
        self.assertTrue(self.multiworld.state.can_reach(loc, player=self.player))

    def test_check_above_headroom_requires_increases(self) -> None:
        """Blueprint Check 4 costs 85g, requires cap increases even with earning headroom."""
        loc = self.multiworld.get_location("Blueprint Check 4", self.player)
        # Without cap increases, not accessible (20 + 60 = 80 < 85)
        self.assertFalse(self.multiworld.state.can_reach(loc, player=self.player))
        
        # With 1 cap increase (cap = 40, effective = 100), now accessible
        self.collect_by_name("Money Cap Increase")
        self.assertTrue(self.multiworld.state.can_reach(loc, player=self.player))

    def test_expensive_check_with_headroom(self) -> None:
        """Blueprint Check 5 costs 110g, demonstrates headroom reduces required increases."""
        loc = self.multiworld.get_location("Blueprint Check 5", self.player)
        
        # Without increases, not accessible (effective cap = 20+60 = 80 < 110)
        self.assertFalse(self.multiworld.state.can_reach(loc, player=self.player))
        
        # With 2 increases (cap = 60, effective = 120), accessible
        for _ in range(2):
            self.collect_by_name("Money Cap Increase")
        self.assertTrue(self.multiworld.state.can_reach(loc, player=self.player))

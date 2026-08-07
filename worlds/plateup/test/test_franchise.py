import logging
import os
from collections import Counter

import Utils
from BaseClasses import LocationProgressType
from worlds.plateup.test.bases import PlateUpTestBase


class TestFranchiseOptionLogic(PlateUpTestBase):
    options = {
        "goal": 0,  # Franchise x times
        "franchise_count": 2,
    }

    # Optionally, turn up the logging
    # logging.getLogger().setLevel(logging.INFO)

    def test_has_completion_condition(self) -> None:
        """ Can you even beat PlateUp? """
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])


class _MockState:
    def __init__(self, inventory=None):
        self.inventory = Counter(inventory or {})

    def can_reach(self, *_args, **_kwargs):
        # Treat previous-day chaining as satisfied so tests isolate lease gating behavior.
        return True

    def has(self, item_name, _player, count=1):
        return self.inventory[item_name] >= count

    def count(self, item_name, _player):
        return self.inventory[item_name]


class TestFranchiseLeaseStrictness(PlateUpTestBase):
    options = {
        "goal": 0,
        "franchise_count": 2,
        "day_leases_enabled": 1,
        "day_lease_interval": 4,
        "day_lease_mode": 1,  # dish_specific
        "dish": 1,
        "free_starter_dishes": 1,
    }

    def test_post_franchise_requires_overtime_lease(self) -> None:
        loc = self.world.get_location("Franchise - Complete First Day After Franchised")

        no_items = _MockState()
        speed_only = _MockState({"Speed Upgrade Cook": 1})
        lease_only = _MockState({"Overtime Day Lease": 1})

        self.assertFalse(loc.access_rule(no_items))
        self.assertFalse(loc.access_rule(speed_only))
        self.assertTrue(loc.access_rule(lease_only))

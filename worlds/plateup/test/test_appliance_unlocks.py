from BaseClasses import ItemClassification
from worlds.plateup.Items import APPLIANCE_UNLOCK_POOL, APPLIANCE_UNLOCK_PRIORITY
from worlds.plateup.test.bases import PlateUpTestBase


class TestApplianceUnlocksEnabled(PlateUpTestBase):
    """appliance_unlocks=1 places named 'Unlock X' items up to the pool size."""
    options = {
        "goal": 1,
        "day_count": 30,
        "appliance_unlocks": 1,
        "appliance_unlock_pool_size": 10,
    }

    def test_unlock_items_in_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        unlock_items = [item for item in items if item.name.startswith("Unlock ")]
        self.assertEqual(len(unlock_items), min(10, len(APPLIANCE_UNLOCK_POOL)))

    def test_unlock_items_are_useful(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        unlock_items = [item for item in items if item.name.startswith("Unlock ")]
        for item in unlock_items:
            self.assertEqual(item.classification, ItemClassification.useful)

    def test_priority_appliances_always_included(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        unlock_names = {item.name.removeprefix("Unlock ") for item in items if item.name.startswith("Unlock ")}
        pool_size = min(10, len(APPLIANCE_UNLOCK_POOL))
        for appliance in APPLIANCE_UNLOCK_PRIORITY[:pool_size]:
            self.assertIn(appliance, unlock_names)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestApplianceUnlocksDisabled(PlateUpTestBase):
    """appliance_unlocks=0 places no 'Unlock X' items."""
    options = {
        "goal": 1,
        "day_count": 30,
        "appliance_unlocks": 0,
    }

    def test_no_unlock_items_in_pool(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        unlock_items = [item for item in items if item.name.startswith("Unlock ")]
        self.assertEqual(len(unlock_items), 0)

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))


class TestApplianceUnlocksSlotData(PlateUpTestBase):
    """unlocked_appliances in slot data equals the complement of the selected pool."""
    options = {
        "goal": 1,
        "day_count": 30,
        "appliance_unlocks": 1,
        "appliance_unlock_pool_size": 10,
    }

    def test_unlocked_appliances_is_complement(self) -> None:
        slot_data = self.world.fill_slot_data()
        unlocked = slot_data["unlocked_appliances"]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        selected = {item.name.removeprefix("Unlock ") for item in items if item.name.startswith("Unlock ")}
        # Every appliance in the pool should be either selected (has item) or pre-unlocked
        for appliance in APPLIANCE_UNLOCK_POOL:
            self.assertTrue(
                appliance in selected or appliance in unlocked,
                f"{appliance} is neither selected nor in unlocked_appliances"
            )
        # No appliance should appear in both
        for appliance in APPLIANCE_UNLOCK_POOL:
            self.assertFalse(
                appliance in selected and appliance in unlocked,
                f"{appliance} appears in both selected pool and unlocked_appliances"
            )

    def test_unlocked_appliances_all_strings(self) -> None:
        slot_data = self.world.fill_slot_data()
        for entry in slot_data["unlocked_appliances"]:
            self.assertIsInstance(entry, str)


class TestApplianceUnlocksDisabledSlotData(PlateUpTestBase):
    """When appliance_unlocks=0, unlocked_appliances contains the full pool."""
    options = {
        "goal": 1,
        "day_count": 30,
        "appliance_unlocks": 0,
    }

    def test_all_appliances_unlocked(self) -> None:
        slot_data = self.world.fill_slot_data()
        unlocked = set(slot_data["unlocked_appliances"])
        for appliance in APPLIANCE_UNLOCK_POOL:
            self.assertIn(appliance, unlocked)


class TestApplianceUnlocksFullPool(PlateUpTestBase):
    """Pool size at maximum — no crash and count capped to actual pool length (89)."""
    options = {
        "goal": 1,
        "day_count": 60,
        "appliance_unlocks": 1,
        "appliance_unlock_pool_size": 89,  # max option value == len(APPLIANCE_UNLOCK_POOL)
    }

    def test_unlock_count_capped_at_pool_length(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        unlock_items = [item for item in items if item.name.startswith("Unlock ")]
        self.assertLessEqual(len(unlock_items), len(APPLIANCE_UNLOCK_POOL))

    def test_item_count_matches_location_count(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations() if loc.player == self.player]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(items), len(locations))

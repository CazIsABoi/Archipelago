from BaseClasses import ItemClassification
from worlds.plateup.test.bases import PlateUpTestBase


class TestTrapCardsEnabled(PlateUpTestBase):
    options = {
        "goal": 1,
        "day_count": 30,
    }  # default trap_chance=10 places traps

    def test_trap_cards_present(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        traps = [item for item in items if item.classification == ItemClassification.trap]
        self.assertGreater(len(traps), 0)


class TestTrapCardsDisabled(PlateUpTestBase):
    options = {
        "goal": 1,
        "day_count": 30,
        "trap_chance": 0,
    }

    def test_trap_cards_removed(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        traps = [item for item in items if item.classification == ItemClassification.trap]
        self.assertEqual(len(traps), 0)

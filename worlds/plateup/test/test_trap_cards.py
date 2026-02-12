from worlds.plateup.test.bases import PlateUpTestBase


class TestTrapCardsEnabled(PlateUpTestBase):
    options = {
        "goal": 1,
        "day_count": 30,
    }

    def test_trap_cards_present(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        traps = [item for item in items if item.name == "Random Customer Card"]
        self.assertGreater(len(traps), 0)


class TestTrapCardsDisabled(PlateUpTestBase):
    options = {
        "goal": 1,
        "day_count": 30,
        "trap_cards": 0,
    }

    def test_trap_cards_removed(self) -> None:
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        traps = [item for item in items if item.name == "Random Customer Card"]
        self.assertEqual(len(traps), 0)

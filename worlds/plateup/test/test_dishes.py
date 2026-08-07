import logging
from worlds.plateup.Items import ITEMS
from worlds.plateup.Locations import dish_dictionary
from worlds.plateup.test.bases import PlateUpTestBase


class TestDishOptionLogic(PlateUpTestBase):
    options = {
        "goal": 0, # Franchise x times
        "franchise_count": 1,
        "dish": 2,
    }

    # Optionally, turn up the logging
    # logging.getLogger().setLevel(logging.INFO)

    def test_has_completion_condition(self) -> None:
        """ Can you even beat PlateUp? """
        self.assertIsNotNone(self.multiworld.completion_condition[self.player])


class TestDishRegistryIncludesFajitas(PlateUpTestBase):
    def test_fajitas_is_registered(self) -> None:
        self.assertIn(118, dish_dictionary)
        self.assertEqual(dish_dictionary[118], "Fajitas")

    def test_fajitas_items_exist(self) -> None:
        self.assertIn("Fajitas Unlock", ITEMS)
        self.assertIn("Fajitas Day Lease", ITEMS)

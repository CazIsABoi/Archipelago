from worlds.plateup.Options import SettingCheckMode
from worlds.plateup.test.bases import PlateUpTestBase


class TestSettingChecksDisabled(PlateUpTestBase):
    options = {
        "setting_checks": 0,
    }

    def test_setting_locations_absent(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertNotIn("Base Setting - Day 1", player_locations)


class TestSettingChecksBaseDefaults(PlateUpTestBase):
    options = {
        "setting_checks": 1,
    }

    def test_base_settings_present(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertIn("Base Setting - Day 1", player_locations)
        self.assertNotIn("Witch Hut - Day 1", player_locations)


class TestSettingChecksWithExtras(PlateUpTestBase):
    options = {
        "setting_checks": 1,
        "setting_extra_checks": ["witch", "turbo"],
        "setting_check_mode": SettingCheckMode.option_base_and_extras,
    }

    def test_extras_added(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertIn("Witch Hut - Day 1", player_locations)
        self.assertIn("Turbo - Day 1", player_locations)
        self.assertIn("Base Setting - Day 1", player_locations)


class TestSettingChecksExtrasOnly(PlateUpTestBase):
    options = {
        "setting_checks": 1,
        "setting_check_mode": SettingCheckMode.option_extras_only,
        "setting_extra_checks": ["autumn"],
    }

    def test_only_extras_present(self) -> None:
        player_locations = {
            loc.name for loc in self.multiworld.get_locations() if loc.player == self.player
        }
        self.assertIn("Autumn - Day 1", player_locations)
        self.assertNotIn("Base Setting - Day 1", player_locations)

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld
from Options import OptionGroup
from .Options import (
    Goal, FranchiseCount, DayCount, DayTarget, DishGoalCount, DishCount, FreeStarterDishes,
    DayLeasesEnabled, DayLeaseInterval, DayLeaseMode, DishLeaseScope,
    MoneyCapEnabled, StartingMoneyCap, MoneyCapIncreaseAmount, MoneyCapIncreaseCount, MoneyCapActivation,
    ApplianceUnlocks, ApplianceUnlockPoolSize, ApplianceUnlockGrantsAppliance, UnlockedAppliancesInShop,
    DecorationUnlocks, PlayerSpeedUpgradeCount, ApplianceSpeedUpgradeCount, ApplianceSpeedMode, ItemsKept,
    StartingCards, StartingCardsAmount, ExtraStartingCards, StartingGroupSize,
    GlobalPatienceEnabled, GlobalPatienceUpgradeCount, GlobalPatienceStartingDebuff,
    PatienceFillerPercent, CustomerFillerPercent, GroupSizeFillerPercent, MessReductionPercent, CoinFillerPercent,
    TrapChance, TrapWeights,
    SettingChecks, SettingCheckMode, SettingExtraChecks, AchievementCheckMode,
    BlueprintCheckCount, BlueprintBasePrice, BlueprintPriceIncrease,
    RerollCheckCount,
    DeathLink, DeathLinkBehavior,
)

option_groups = [
    OptionGroup("Goal Settings", [
        Goal, FranchiseCount, DayCount, DayTarget, DishGoalCount, DishCount, FreeStarterDishes,
    ]),
    OptionGroup("Progression Gates", [
        DayLeasesEnabled, DayLeaseInterval, DayLeaseMode, DishLeaseScope,
        MoneyCapEnabled, StartingMoneyCap, MoneyCapIncreaseAmount, MoneyCapIncreaseCount, MoneyCapActivation,
    ]),
    OptionGroup("Item Pool", [
        ApplianceUnlocks, ApplianceUnlockPoolSize, ApplianceUnlockGrantsAppliance, UnlockedAppliancesInShop,
        DecorationUnlocks, PlayerSpeedUpgradeCount, ApplianceSpeedUpgradeCount, ApplianceSpeedMode, ItemsKept,
    ]),
    OptionGroup("Difficulty", [
        StartingCards, StartingCardsAmount, ExtraStartingCards, StartingGroupSize,
        GlobalPatienceEnabled, GlobalPatienceUpgradeCount, GlobalPatienceStartingDebuff,
        DeathLink, DeathLinkBehavior,
    ]),
    OptionGroup("Filler Weights", [
        PatienceFillerPercent, CustomerFillerPercent, GroupSizeFillerPercent, MessReductionPercent, CoinFillerPercent,
    ]),
    OptionGroup("Traps", [
        TrapChance, TrapWeights,
    ]),
    OptionGroup("Checks", [
        SettingChecks, SettingCheckMode, SettingExtraChecks, AchievementCheckMode,
        BlueprintCheckCount, BlueprintBasePrice, BlueprintPriceIncrease,
        RerollCheckCount,
    ]),
]


class PlateUpWebWorld(WebWorld):
    game = "PlateUp"

    # You can choose between dirt, grass, grassFlowers, ice, jungle, ocean, partyTime, and stone.
    theme = "dirt"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up PlateUp for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["CazIsABoi"],
    )

    tutorials = [setup_en]

    option_groups = option_groups

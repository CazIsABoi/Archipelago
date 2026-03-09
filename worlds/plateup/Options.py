from dataclasses import dataclass
from Options import Choice, OptionList, PerGameCommonOptions, Range, Toggle
from .Locations import OPTIONAL_SETTING_NAMES

class Goal(Choice):
    """Set the goal for completion."""
    display_name = "Goal"
    option_franchise_x_times = 0
    option_complete_x_days = 1
    option_reach_day_x_with_dishes = 2
    default = 0

class FranchiseCount(Range):
    """Select how many franchises are required for completion.(Only used if Goal=complete_x_franchises)"""
    display_name = "Required Franchise Count"
    range_start = 1
    range_end = 50
    default = 1

class DayCount(Range):
    """Select how many days are required for completion. (Only used if Goal=complete_x_days)"""
    display_name = "Required Day Count"
    range_start = 10
    range_end = 1000
    default = 10

class DayTarget(Range):
    """Target day to reach for the 'reach_day_x_with_dishes' goal. The player must survive to this global day with the required number of dishes active. (Only used if Goal=reach_day_x_with_dishes)"""
    display_name = "Day Target"
    range_start = 15
    range_end = 100
    default = 15

class DishGoalCount(Range):
    """How many dishes must be active when the player reaches the target day. Must not exceed the 'dish' option value. (Only used if Goal=reach_day_x_with_dishes)"""
    display_name = "Required Dishes at Target Day"
    range_start = 1
    range_end = 17
    default = 3

class DayLeasesEnabled(Toggle):
    """Enable Day Lease progression items. When disabled, no Day Lease items are placed and days are never gated by leases."""
    display_name = "Enable Day Leases"
    default = 1


class DayLeaseInterval(Range):
    """How many in-game days between each required Day Lease (min 1). Only relevant when day_leases_enabled is on."""
    display_name = "Day Lease Interval"
    range_start = 1
    range_end = 30
    default = 5

class DishCount(Range):
    """How many dishes get dedicated checks and unlocks. 0 keeps every dish unlocked and disables dish checks."""
    display_name = "Starting Dish Count"
    range_start = 0
    range_end = 17
    default = 1


class FreeStarterDishes(Range):
    """How many dishes the player starts with already unlocked when playing with locked dishes (dish > 0). Defaults to 1 (the classic single free starter). Set to 0 to require unlocking every dish, or higher to begin with more dishes pre-unlocked."""
    display_name = "Free Starter Dishes"
    range_start = 0
    range_end = 17
    default = 1

class ItemsKept(Range):
    """How many appliances the player keeps each run."""
    display_name = "Starting Appliance Count"
    range_start = 1
    range_end = 5
    default = 1

class DeathLink(Toggle):
    """Enable death link mode, affecting all linked players."""
    display_name = "Death Link"
    default = 0

class DeathLinkBehavior(Choice):
    """Choose what happens when DeathLink triggers."""
    display_name = "Death Link Behavior"
    option_reset_run = 0
    option_reset_to_last_star = 1
    default = 0

class ApplianceSpeedMode(Choice):
    """
    Choose whether all Speed Upgrade Appliances are "grouped" (single item),
    or "separate" (Cook, Chop, Clean).
    """
    display_name = "Appliance Speed Upgrade Mode"
    option_grouped = 0
    option_separate = 1
    default = 0

class PlayerSpeedUpgradeCount(Range):
    """How many Player Speed Upgrade items to place (0-10)."""
    display_name = "Player Speed Upgrade Count"
    range_start = 0
    range_end = 10
    default = 5

class ApplianceSpeedUpgradeCount(Range):
    """How many Appliance Speed Upgrade items to place (0-10)."""
    display_name = "Appliance Speed Upgrade Count"
    range_start = 0
    range_end = 10
    default = 5

class MoneyCapEnabled(Toggle):
    """Enable the money cap mechanic. When disabled, players have no gold limit and no Money Cap Increase items are placed."""
    display_name = "Enable Money Cap"
    default = 1

class StartingMoneyCap(Range):
    """Starting total money cap (in gold). You cannot hold more than this amount at any time until increased by items."""
    display_name = "Starting Money Cap"
    range_start = 10
    range_end = 40
    default = 20

class MoneyCapIncreaseAmount(Range):
    """How much gold each Money Cap Increase item adds to the player's maximum coin cap."""
    display_name = "Money Cap Increase Amount"
    range_start = 5
    range_end = 100
    default = 20


class ApplianceUnlocks(Toggle):
    """Enable specific appliance unlock items in the pool. When disabled, only Random Appliance items are used."""
    display_name = "Enable Appliance Unlocks"
    default = 1


class ApplianceUnlockGrantsAppliance(Toggle):
    """When enabled, finding an appliance unlock item also immediately grants the appliance for use. When disabled, it only adds the appliance to future shop pools."""
    display_name = "Appliance Unlock Grants Appliance"
    default = 1


class DecorationUnlocks(Toggle):
    """Enable Random Decoration Unlock filler items in the pool."""
    display_name = "Enable Decoration Unlocks"
    default = 1


class TrapCards(Toggle):
    """Enable trap cards that add Random Customer Card items to the pool."""
    display_name = "Enable Trap Cards"
    default = 1


class SettingChecks(Toggle):
    """Enable combined day checks for Country, City, and Alpine settings (cosmetic variants)."""
    display_name = "Enable Setting Checks"
    default = 0


class SettingCheckMode(Choice):
    """Choose whether base settings, extra settings, or both should generate checks. Only relevant if setting_checks is enabled. 
    base_only generates checks for the 3 base settings (Country, City, Alpine). base_and_extras generates checks for those plus any extra settings selected in the option below. 
    extras_only generates checks only for the extra settings selected in the option below."""
    display_name = "Setting Check Mode"
    option_base_only = 0
    option_base_and_extras = 1
    option_extras_only = 2
    default = 0


class SettingExtraChecks(OptionList):
    """Optional settings (beyond Country/City/Alpine) that should receive day checks.

    Use YAML flow-list syntax, e.g.
    `setting_extra_checks: [autumn, witch, turbo]`. Slugs are lowercase; copy/paste
    any of: autumn, banquet, turbo, witch."""
    display_name = "Additional Setting Checks"
    default = ()
    _allowed = tuple(OPTIONAL_SETTING_NAMES)


class StartingCards(Choice):
    """Choose which difficulty of Customer Cards the player starts with. The client will deal these cards at the start of a run. Pair with starting_cards_amount to set how many are dealt."""
    display_name = "Starting Cards"
    option_none = 0
    option_easy = 1
    option_hard = 2
    option_both = 3
    default = 0


class StartingCardsAmount(Range):
    """How many starting Customer Cards are dealt at the start of a run. Requires starting_cards to not be none. Also determines how many Remove Card items are placed in the pool."""
    display_name = "Starting Cards Amount"
    range_start = 1
    range_end = 8
    default = 3


class StartingGroupSize(Range):
    """Set the starting customer group size. Higher values make the game significantly harder. When enabled (>0), places (starting_group_size - 1) 'Reduce Group Size' progression items in the pool, distributed evenly across the run like speed upgrades. Set to 0 to disable."""
    display_name = "Starting Group Size"
    range_start = 0
    range_end = 8
    default = 0


class GlobalPatienceEnabled(Toggle):
    """Enable Global Patience Increase progression items. When enabled, places 'global_patience_upgrade_count' items that are required to reach later days, distributed evenly across the run like speed upgrades."""
    display_name = "Enable Global Patience Upgrades"
    default = 0


class GlobalPatienceUpgradeCount(Range):
    """How many Global Patience Increase items to place (1-10). Only relevant when global_patience_enabled is on."""
    display_name = "Global Patience Upgrade Count"
    range_start = 1
    range_end = 10
    default = 5


class AchievementChecks(Toggle):
    """Enable achievement location checks. Adds in-game achievements as checks. Some are
    restricted by goal (Overtime) or appliance unlocks (Charcoal Factory, Safety Last)."""
    display_name = "Enable Achievement Checks"
    default = 1


@dataclass
class PlateUpOptions(PerGameCommonOptions):
    goal: Goal
    franchise_count: FranchiseCount
    day_count: DayCount
    day_target: DayTarget
    dish_goal_count: DishGoalCount
    dish: DishCount
    free_starter_dishes: FreeStarterDishes
    appliances_kept: ItemsKept
    death_link: DeathLink
    death_link_behavior: DeathLinkBehavior
    appliance_speed_mode: ApplianceSpeedMode
    day_leases_enabled: DayLeasesEnabled
    day_lease_interval: DayLeaseInterval
    player_speed_upgrade_count: PlayerSpeedUpgradeCount
    appliance_speed_upgrade_count: ApplianceSpeedUpgradeCount
    money_cap_enabled: MoneyCapEnabled
    starting_money_cap: StartingMoneyCap
    money_cap_increase_amount: MoneyCapIncreaseAmount
    appliance_unlocks: ApplianceUnlocks
    appliance_unlock_grants_appliance: ApplianceUnlockGrantsAppliance
    decoration_unlocks: DecorationUnlocks
    trap_cards: TrapCards
    setting_checks: SettingChecks
    setting_check_mode: SettingCheckMode
    setting_extra_checks: SettingExtraChecks
    starting_cards: StartingCards
    starting_cards_amount: StartingCardsAmount
    starting_group_size: StartingGroupSize
    global_patience_enabled: GlobalPatienceEnabled
    global_patience_upgrade_count: GlobalPatienceUpgradeCount
    achievement_checks: AchievementChecks
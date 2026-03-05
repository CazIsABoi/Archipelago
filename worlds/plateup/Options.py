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

class DayLeaseInterval(Range):
    """How many in-game days between each required Day Lease (min 1)."""
    display_name = "Day Lease Interval"
    range_start = 1
    range_end = 30
    default = 5

class DishCount(Range):
    """How many dishes get dedicated checks and unlocks -1 (1 free starter dish). 0 keeps every dish unlocked and disables dish checks."""
    display_name = "Starting Dish Count"
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

class StartingMoneyCap(Range):
    """Starting total money cap (in gold). You cannot hold more than this amount at any time until increased by items."""
    display_name = "Starting Money Cap"
    range_start = 10
    range_end = 40
    default = 20


class ApplianceUnlocks(Toggle):
    """Enable specific appliance unlock items in the pool. When disabled, only Random Appliance items are used."""
    display_name = "Enable Appliance Unlocks"
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


@dataclass
class PlateUpOptions(PerGameCommonOptions):
    goal: Goal
    franchise_count: FranchiseCount
    day_count: DayCount
    day_target: DayTarget
    dish_goal_count: DishGoalCount
    dish: DishCount
    appliances_kept: ItemsKept
    death_link: DeathLink
    death_link_behavior: DeathLinkBehavior
    appliance_speed_mode: ApplianceSpeedMode
    day_lease_interval: DayLeaseInterval
    player_speed_upgrade_count: PlayerSpeedUpgradeCount
    appliance_speed_upgrade_count: ApplianceSpeedUpgradeCount
    starting_money_cap: StartingMoneyCap
    appliance_unlocks: ApplianceUnlocks
    trap_cards: TrapCards
    setting_checks: SettingChecks
    setting_check_mode: SettingCheckMode
    setting_extra_checks: SettingExtraChecks
    starting_cards: StartingCards
    starting_cards_amount: StartingCardsAmount
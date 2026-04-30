from dataclasses import dataclass
from Options import Choice, OptionCounter, OptionGroup, OptionList, PerGameCommonOptions, Range, Toggle
from .Locations import OPTIONAL_SETTING_NAMES

class Goal(Choice):
    """Choose the win condition for your PlateUp run.
    franchise_x_times: Franchise your restaurant the required number of times (see franchise_count).
    complete_x_days: Survive and complete a set number of in-game days (see day_count).
    reach_day_x_with_dishes: Reach a specific global day while having a minimum number of dishes active (see day_target and dish_goal_count)."""
    display_name = "Goal"
    option_franchise_x_times = 0
    option_complete_x_days = 1
    option_reach_day_x_with_dishes = 2
    default = 0

class FranchiseCount(Range):
    """How many times you must franchise your restaurant to trigger completion.
    Each franchise resets your kitchen but lets you keep a number of appliances (see appliances_kept).
    Only used when goal is set to franchise_x_times."""
    display_name = "Required Franchise Count"
    range_start = 1
    range_end = 50
    default = 1

class DayCount(Range):
    """How many in-game days you must complete to trigger completion.
    Each day is a full restaurant service. Higher values create longer runs with more locations and items.
    Only used when goal is set to complete_x_days."""
    display_name = "Required Day Count"
    range_start = 10
    range_end = 1000
    default = 10

class DayTarget(Range):
    """The global day number you must survive to in order to trigger completion.
    You must reach this day with at least dish_goal_count dishes actively unlocked.
    Only used when goal is set to reach_day_x_with_dishes."""
    display_name = "Day Target"
    range_start = 15
    range_end = 100
    default = 15

class DishGoalCount(Range):
    """How many dish unlocks must be in your possession when you reach the target day.
    Must not exceed the dish count option — if it does, generation will raise an error.
    Only used when goal is set to reach_day_x_with_dishes."""
    display_name = "Required Dishes at Target Day"
    range_start = 1
    range_end = 17
    default = 3

class DayLeasesEnabled(Toggle):
    """Enable Day Lease progression items in the pool.
    When enabled, Day Lease items gate progress: you must have received enough leases before you can play the next block of days (see day_lease_interval for block size).
    When disabled, no lease items are placed and no days are gated — useful if you prefer a free-flowing run without hard progression locks."""
    display_name = "Enable Day Leases"
    default = 1


class DayLeaseInterval(Range):
    """How many days pass between each required Day Lease block.
    With day_leases_progressive off (default): days 1-N are free, days N+1 to 2N require 1 lease, etc.
    With day_leases_progressive on: days 1-N require 1 lease, days N+1 to 2N require 2, etc.
    Lower values create more frequent, smaller progression gates; higher values create larger, rarer gates.
    Only relevant when day_leases_enabled is on."""
    display_name = "Day Lease Interval"
    range_start = 1
    range_end = 30
    default = 5

class DayLeaseMode(Choice):
    """Controls how Day Lease items are organised when day_leases_enabled is on.
    global: a single shared 'Day Lease' item gates progression across all day-based content (default behaviour).
    dish_specific: each dish gets its own named lease items (e.g. 'Steak Day Lease') that only gate progress on that dish's day locations. Requires dish_count > 0.
    Only relevant when day_leases_enabled is on."""
    display_name = "Day Lease Mode"
    option_global = 0
    option_dish_specific = 1
    default = 0

class DishLeaseScope(Choice):
    """When day_lease_mode is dish_specific, controls which dishes receive their own lease items.
    all_dishes: every selected dish gets its own set of Day Lease items, one block per dish.
    goal_count_only: only the first dish_goal_count dishes receive lease items; any remaining dishes have their day locations ungated by leases.
    Only relevant when goal is reach_day_x_with_dishes, day_leases_enabled is on, and day_lease_mode is dish_specific."""
    display_name = "Dish Lease Scope"
    option_all_dishes = 0
    option_goal_count_only = 1
    default = 0


class DayLeasesProgressive(Toggle):
    """Make day leases act as progressive items: the first lease for each food/dish is required to play even Day 1.
    When enabled, leases_required = ceil(day / interval) — every day block requires at least one lease, so the
    first lease acts as an unlock, preventing players from starting a food freely and then being gated mid-run.
    When disabled (default), the first block of days (1 to interval) is free, and leases gate subsequent blocks.
    This can help prevent players from being locked out of foods after franchising elsewhere.
    Only relevant when day_leases_enabled is on."""
    display_name = "Progressive Day Leases"
    default = 0

class DishCount(Range):
    """How many dishes are randomized into the item pool as unlock items, and how many dish-day location checks are generated.
    Each selected dish contributes up to 15 day-based checks (one per day of a run).
    Setting this to 0 leaves all dishes permanently unlocked and disables all dish-related checks."""
    display_name = "Dish Count"
    range_start = 0
    range_end = 17
    default = 1


class FreeStarterDishes(Range):
    """How many of the selected dishes the player starts with already unlocked, at no cost.
    The starting dish(es) are weighted toward easier options (Salad, Pizza, Coffee, Breakfast).
    Set to 0 to require receiving every dish unlock from the multiworld.
    Set equal to dish_count to start with all dishes already unlocked (making dish unlocks purely cosmetic checks).
    Only relevant when dish count is greater than 0."""
    display_name = "Free Starter Dishes"
    range_start = 0
    range_end = 17
    default = 1

class ItemsKept(Range):
    """How many appliances you are allowed to keep when franchising.
    Higher values make each franchise run easier since you carry over more of your kitchen setup.
    This is sent directly to the client and enforced in-game."""
    display_name = "Appliances Kept Each Run"
    range_start = 1
    range_end = 5
    default = 1

class DeathLink(Toggle):
    """Enable DeathLink, which ties your fate to other DeathLink-enabled players in the multiworld.
    When your run ends (e.g. a day fails), it triggers a death for all linked players, and vice versa.
    The exact effect of a received DeathLink is controlled by death_link_behavior."""
    display_name = "Death Link"
    default = 0

class DeathLinkBehavior(Choice):
    """What happens when a DeathLink signal is received from another player.
    reset_run: immediately end your current run and start fresh.
    reset_to_last_star: roll back your restaurant to the state it was in at your last earned star.
    Only relevant when death_link is enabled."""
    display_name = "Death Link Behavior"
    option_reset_run = 0
    option_reset_to_last_star = 1
    default = 0

class PlayerSpeedUpgradeCount(Range):
    """How many Player Speed Upgrade items to place in the pool.
    These increase your chef's movement speed, making it easier to serve customers in time.
    They are distributed as progression items evenly across the run, so later days require more of them.
    Set to 0 to remove player speed upgrades entirely."""
    display_name = "Player Speed Upgrade Count"
    range_start = 0
    range_end = 10
    default = 5

class ApplianceSpeedUpgradeCount(Range):
    """How many Appliance Speed Upgrade items to place in the pool.
    These increase the processing speed of your kitchen appliances (cooking, chopping, cleaning).
    Whether this produces one grouped item or three separate items depends on appliance_speed_mode.
    Set to 0 to remove appliance speed upgrades entirely."""
    display_name = "Appliance Speed Upgrade Count"
    range_start = 0
    range_end = 10
    default = 5

class ApplianceSpeedMode(Choice):
    """Controls how Appliance Speed Upgrades are split in the item pool.
    grouped: all appliance speed upgrades are a single generic item that boosts all appliance speeds.
    separate: speed upgrades are split into three distinct items — Speed Upgrade Cook, Speed Upgrade Chop, and Speed Upgrade Clean — giving finer control over which stations improve first."""
    display_name = "Appliance Speed Upgrade Mode"
    option_grouped = 0
    option_separate = 1
    default = 0

class MoneyCapEnabled(Toggle):
    """Enable the gold cap mechanic, which limits how much gold you can hold at once.
    When enabled, Money Cap Increase items are placed in the pool as progression items that raise your cap.
    When disabled, you have no gold limit and no Money Cap Increase items are placed — also disables reroll cost checks that depend on the cap."""
    display_name = "Enable Money Cap"
    default = 1

class StartingMoneyCap(Range):
    """The gold cap you begin with at the start of the run.
    You cannot hold more gold than this at any time until you receive Money Cap Increase items.
    Lower values create more pressure in early days; higher values give more starting freedom.
    Only relevant when money_cap_enabled is on."""
    display_name = "Starting Money Cap"
    range_start = 10
    range_end = 40
    default = 20

class MoneyCapIncreaseAmount(Range):
    """How much gold each Money Cap Increase item permanently adds to your maximum gold cap.
    Higher values mean fewer items are needed to reach a comfortable cap, but each individual item is more impactful.
    Only relevant when money_cap_enabled is on."""
    display_name = "Money Cap Increase Amount"
    range_start = 5
    range_end = 100
    default = 20


class MoneyCapIncreaseCount(Range):
    """How many Money Cap Increase items to place in the item pool.
    Each item permanently raises your gold cap by money_cap_increase_amount.
    Higher values spread cap increases more gradually across the run; lower values mean fewer but larger milestones.
    Only relevant when money_cap_enabled is on."""
    display_name = "Money Cap Increase Count"
    range_start = 1
    range_end = 20
    default = 5


class MoneyCapActivation(Choice):
    """Controls when a received Money Cap Increase item takes effect.
    instant: your gold cap rises the moment the item is received, even during an active service day.
    start_of_day: the cap increase is held until the beginning of your next cooking day, when the timer starts.
    Only relevant when money_cap_enabled is on."""
    display_name = "Money Cap Activation Method"
    option_instant = 0
    option_start_of_day = 1
    default = 0


class ApplianceUnlocks(Toggle):
    """Enable named appliance unlock items in the pool (e.g. 'Unlock Hob', 'Unlock Belt').
    When enabled, finding one of these items adds that specific appliance to your future shop offerings, and optionally grants it immediately (see appliance_unlock_grants_appliance).
    When disabled, only generic Random Appliance items are used, which grant a random appliance from the full pool."""
    display_name = "Enable Appliance Unlocks"
    default = 1


class ApplianceUnlockPoolSize(Range):
    """How many named appliance unlock items to include in the pool when appliance_unlocks is enabled.
    The pool always prioritises progression-critical appliances (Hob, Counter, Sink, Plate Stack, Research Desk, Conveyor Belt, Grabber) first, then randomly samples from the remaining appliances up to the chosen size.
    Lower values create a tighter, more focused pool; higher values allow more variety.
    The maximum of 89 includes all 58 useful and 31 filler appliances from the mod's dictionaries.
    Only relevant when appliance_unlocks is enabled."""
    display_name = "Appliance Unlock Pool Size"
    range_start = 10
    range_end = 89
    default = 30


class ApplianceUnlockGrantsAppliance(Toggle):
    """Controls whether receiving a named appliance unlock item also immediately places that appliance in your kitchen.
    When enabled, the item acts as both an unlock and a direct grant — you get the appliance right away.
    When disabled, the item only adds the appliance to your available shop pool for future purchase; you still need to buy it.
    Only relevant when appliance_unlocks is enabled."""
    display_name = "Appliance Unlock Grants Appliance"
    default = 1


class DecorationUnlocks(Toggle):
    """Enable Random Decoration Unlock items as filler in the pool.
    These items are cosmetic-only and unlock random decorations (wallpapers, floors, etc.) for use in your restaurant.
    Disabling this replaces decoration unlock slots in the filler queue with Random Filler Appliances."""
    display_name = "Enable Decoration Unlocks"
    default = 1


class TrapChance(Range):
    """The percentage of remaining filler slots that will be replaced by trap items.
    Set to 0 to disable traps entirely.
    At 100, every available filler slot becomes a trap.
    Which traps appear and their relative frequency is controlled by trap_weights."""
    display_name = "Trap Chance"
    range_start = 0
    range_end = 100
    default = 10


_TRAP_WEIGHT_KEYS = [
    "everything_is_on_fire", "super_slow", "random_customer_card",
    "patience_decrease", "more_customers", "min_group_size_increase", "max_group_size_increase",
    "random_dish_extra", "random_side_dish",
    "tip_jar_drain", "good_advertisement", "card_swap",
]


class TrapWeights(OptionCounter):
    """Relative weights for each trap type. Higher values make that trap more likely to appear.
    Set a trap's weight to 0 to exclude it entirely from the pool.
    Set trap_chance to 0 to disable traps entirely.
    random_dish_extra: adds a random dish extra requirement (e.g. extra napkins, candles) for the day.
    random_side_dish: adds a random side dish requirement for the day.
    tip_jar_drain: empties your tip jar for the day.
    good_advertisement: floods the restaurant with extra customers.
    card_swap: swaps one of your active customer cards for a random different one."""
    display_name = "Trap Weights"
    valid_keys = _TRAP_WEIGHT_KEYS
    min = 0
    default = {k: 1 for k in _TRAP_WEIGHT_KEYS}


class SettingChecks(Toggle):
    """Enable location checks tied to in-game restaurant settings (Country, City, Alpine, and optionally others).
    Each enabled setting generates up to 15 day-based checks, one per day of a run played in that setting.
    Settings are cosmetic map variants and do not affect gameplay balance, but playing them becomes required to clear their checks.
    Configure which settings are included using setting_check_mode and setting_extra_checks."""
    display_name = "Enable Setting Checks"
    default = 0


class SettingCheckMode(Choice):
    """Controls which settings generate day-based location checks.
    base_only: generates checks only for the 3 base settings (Country, City, Alpine).
    base_and_extras: generates checks for the base 3 settings plus any extras listed in setting_extra_checks.
    extras_only: generates checks only for the extras listed in setting_extra_checks, skipping the base settings.
    Only relevant when setting_checks is enabled."""
    display_name = "Setting Check Mode"
    option_base_only = 0
    option_base_and_extras = 1
    option_extras_only = 2
    default = 0


class SettingExtraChecks(OptionList):
    """A list of additional settings beyond the base three (Country, City, Alpine) that should generate day-based checks.
    Only settings listed here will be included when setting_check_mode is extras_only or base_and_extras.
    Use YAML flow-list syntax, e.g. setting_extra_checks: [autumn, witch, turbo].
    Valid slugs (lowercase): autumn, banquet, turbo, witch."""
    display_name = "Additional Setting Checks"
    default = ()
    _allowed = tuple(OPTIONAL_SETTING_NAMES)


class StartingCards(Choice):
    """Which difficulty tier of Customer Cards are automatically dealt at the start of every run.
    Customer Cards impose penalty rules on customers (e.g. impatience, larger groups).
    none: no starting cards, normal difficulty.
    easy: one or more easy cards are dealt each run.
    hard: one or more hard cards are dealt each run.
    both: a mix of easy and hard cards are dealt each run.
    The number of cards dealt is set by starting_cards_amount. An equal number of Remove Card items are added to the pool to let you undo them."""
    display_name = "Starting Cards"
    option_none = 0
    option_easy = 1
    option_hard = 2
    option_both = 3
    default = 1

class StartingCardsAmount(Range):
    """How many Customer Cards are dealt at the start of each run.
    This also determines how many Remove Card progression items are placed in the pool — one per starting card — so you can gradually cancel out the penalty cards as you receive items.
    Only relevant when starting_cards is not none."""
    display_name = "Starting Cards Amount"
    range_start = 1
    range_end = 8
    default = 4


EXTRA_CARD_VALID_KEYS = (
    "individual_dining", "medium_groups", "large_groups", "flexible_dining",
    "morning_rush", "lunch_rush", "dinner_rush", "herd_mentality",
    "advertising", "advertising_2", "all_you_can_eat", "double_helpings",
    "blindfolded_chefs", "closing_time", "discounts", "empathy",
    "health_and_safety", "high_expectations", "high_quality", "high_standards",
    "instant_service", "leisurely_eating", "personalized_waiting", "picky_eaters",
    "relaxed_atmosphere", "sedate_atmosphere", "simplicity", "splash_zone",
    "victorian_standards",
)


class ExtraStartingCards(OptionList):
    """A list of specific customer cards to deal at the start of every run, on top of any random starting_cards.
    For each card listed, one Remove Card progression item is added to the pool so you can cancel it.
    Use lowercase_underscore slugs, e.g. [high_expectations, large_groups].
    Valid slugs: individual_dining, medium_groups, large_groups, flexible_dining,
    morning_rush, lunch_rush, dinner_rush, herd_mentality, advertising, advertising_2,
    all_you_can_eat, double_helpings, blindfolded_chefs, closing_time, discounts, empathy,
    health_and_safety, high_expectations, high_quality, high_standards, instant_service,
    leisurely_eating, personalized_waiting, picky_eaters, relaxed_atmosphere,
    sedate_atmosphere, simplicity, splash_zone, victorian_standards."""
    display_name = "Extra Starting Cards"
    valid_keys = EXTRA_CARD_VALID_KEYS
    valid_keys_casefold = True
    default = []


class StartingGroupSize(Range):
    """The customer group size your restaurant starts with at the beginning of the run.
    Larger groups are significantly harder to serve in time. In the base game the group size starts at 1.
    When set above 1, (starting_group_size - 1) Reduce Group Size progression items are placed in the pool and distributed evenly across the run, gradually bringing the group size back down to 1.
    Set to 0 to disable this mechanic entirely and use the normal starting group size."""
    display_name = "Starting Group Size"
    range_start = 0
    range_end = 8
    default = 0


class GlobalPatienceEnabled(Toggle):
    """Enable Global Patience Increase as a progression mechanic.
    When enabled, customer patience starts reduced and Global Patience Increase items are required to progress to later days.
    The items are distributed evenly across the run, so you need more of them to reach later days.
    When disabled, patience behaves normally and no patience upgrade items are placed."""
    display_name = "Enable Global Patience Upgrades"
    default = 0


class GlobalPatienceUpgradeCount(Range):
    """How many Global Patience Increase progression items to place in the pool.
    These are gated evenly across the run — more are required before you can reach later days.
    Higher counts create more patience-gated progression milestones throughout the run.
    Only relevant when global_patience_enabled is on."""
    display_name = "Global Patience Upgrade Count"
    range_start = 1
    range_end = 10
    default = 5


class GlobalPatienceStartingDebuff(Range):
    """How much patience is subtracted from all customers at the start of the run.
    This is the baseline penalty before any Global Patience Increase items are received.
    At 0, customers start with normal patience (no debuff).
    Values around -40 are where the early game starts to feel very punishing — customers leave quickly and mistakes are costly.
    Values below -40 approach impossible territory: at -70 or lower, early days are effectively unwinnable without significant kitchen optimisation and luck.
    The range extends to -100 for completeness, but practical play recommends staying above -50.
    Each Global Patience Increase item received will partially restore patience toward the normal level.
    Only relevant when global_patience_enabled is on."""
    display_name = "Global Patience Starting Debuff"
    range_start = -100
    range_end = 0
    default = -20


class PatienceFillerPercent(Range):
    """What percentage of the remaining filler capacity to fill with Patience Increase items.
    Patience Increase gives a temporary buff to customer patience for a day, making service easier.
    At 0, Patience Increase items still appear naturally through the standard filler queue rotation.
    The budget is consumed in order across all filler percent options, so the total can never overflow."""
    display_name = "Patience Filler Percent"
    range_start = 0
    range_end = 100
    default = 0


class CustomerFillerPercent(Range):
    """What percentage of the remaining filler capacity to fill with Less Customers items.
    Less Customers temporarily reduces the number of customers served in a day, giving some breathing room.
    At 0, Less Customers items still appear naturally through the standard filler queue rotation.
    The budget is consumed in order across all filler percent options, so the total can never overflow."""
    display_name = "Customer Filler Percent"
    range_start = 0
    range_end = 100
    default = 0


class GroupSizeFillerPercent(Range):
    """What percentage of the remaining filler capacity to fill with Group Size Decrease items.
    The allocated slots are split evenly between Minimum Group Size Decrease and Maximum Group Size Decrease.
    These items reduce the minimum and maximum number of customers in each arriving group, making service more manageable.
    At 0, Group Size Decrease items still appear naturally through the standard filler queue rotation.
    The budget is consumed in order across all filler percent options, so the total can never overflow."""
    display_name = "Group Size Filler Percent"
    range_start = 0
    range_end = 100
    default = 0


class MessReductionPercent(Range):
    """What percentage of the remaining filler capacity to fill with Mess Reduction items.
    Mess Reduction decreases the amount of mess generated on a given day, reducing the cleaning burden.
    At 0, Mess Reduction items still appear naturally through the standard filler queue rotation.
    The budget is consumed in order across all filler percent options, so the total can never overflow."""
    display_name = "Mess Reduction Percent"
    range_start = 0
    range_end = 100
    default = 0


class CoinFillerPercent(Range):
    """What percentage of the remaining filler capacity to fill with Coin items (10 Coins each).
    Coins provide small amounts of in-game currency when received.
    At 0, coins still appear naturally through the standard filler queue rotation.
    The budget is consumed in order across all filler percent options, so the total can never overflow."""
    display_name = "Coin Filler Percent"
    range_start = 0
    range_end = 100
    default = 0


class UnlockedAppliancesInShop(Toggle):
    """Controls whether appliances that have no unlock item in the pool are immediately available in the shop.
    When enabled, any appliance not included in the appliance_unlock_pool (because it was not sampled or appliance_unlocks is off) is treated as already unlocked and available to purchase from the start.
    When disabled, only appliances that have been explicitly unlocked via received items appear in the shop."""
    display_name = "Unlocked Appliances In Shop"
    default = 1


class AchievementCheckMode(Choice):
    """Controls which achievement location checks are included.
    all: includes all achievements reachable given the current goal settings (overtime and New Chef Plus are filtered by day count automatically).
    earned_only: additionally excludes achievements gated behind specific option combinations that are currently disabled (e.g. Charcoal Factory and Safety Last when appliance_unlocks is off).
    none: disables all achievement checks."""
    display_name = "Achievement Check Mode"
    option_all = 0
    option_earned_only = 1
    option_none = 2
    default = 0


class BlueprintCheckCount(Range):
    """How many Archipelago blueprint checks to add to the location pool.
    On appliance shop days, 3 Archipelago pedestals appear by the street alongside the regular shop.
    Buying a pedestal sends a check and replaces it with the next one in the pool, so the 3 visible slots
    cycle through the entire queue over time.
    Set to 0 to disable pedestal checks entirely.
    When money_cap_enabled is on, checks whose cost exceeds the maximum achievable cap are excluded so they
    are never permanently inaccessible. A buffer of ~30% extra checks beyond that hard limit is still included
    because gold earned during a service day (before the cap is applied) can cover the shortfall — those bonus
    checks simply require all available Money Cap Increase items to be in logic."""
    display_name = "Blueprint Check Count"
    range_start = 0
    range_end = 100
    default = 10


class BlueprintBasePrice(Range):
    """The coin cost of the very first Archipelago pedestal.
    Each subsequent pedestal costs this amount plus blueprint_price_increase, so costs rise as more are purchased.
    If the price of a pedestal would exceed the maximum achievable money cap (starting_money_cap +
    money_cap_increase_amount × money_cap_increase_count) for more than ~30%% of the requested checks, the
    excess checks are silently dropped from the pool to prevent inaccessible locations.
    Only relevant when blueprint_check_count is greater than 0."""
    display_name = "Blueprint Base Price"
    range_start = 0
    range_end = 200
    default = 10


class BlueprintPriceIncrease(Range):
    """How many extra coins each successive pedestal costs compared to the one before it.
    For example, with a base price of 10 and an increase of 20, the pedestals cost 10, 30, 50, 70, and so on.
    Set to 0 to keep all pedestals at the same price.
    High values combined with a low money cap will cause later checks to be excluded or capped at the
    all-items-required access rule (see blueprint_check_count for details).
    Only relevant when blueprint_check_count is greater than 0."""
    display_name = "Blueprint Price Increase"
    range_start = 0
    range_end = 100
    default = 10


class RerollCheckCount(Range):
    """How many reroll cost checks to add to the location pool.
    On appliance shop days, rerolling the shop costs coins and sends a check each time.
    Set to 0 to disable reroll cost checks entirely.
    Location IDs are in the range 130001–130100."""
    display_name = "Reroll Check Count"
    range_start = 0
    range_end = 100
    default = 0


class AllowSaveFileEditing(Toggle):
    """Allow the client to make direct edits to your PlateUp save file.
    Modifying player level (set to level 17), modifying garage.
    When enabled, the client may write to your save file to apply these changes.
    When disabled, no save file modifications are made. 
    DOES NOTHING YET — this is a placeholder for future features that require save edits, and currently has no effect on generation or gameplay."""
    display_name = "Allow Save File Editing"
    default = 0


class RandomResearch(Toggle):
    """Enable random research mode.
    When enabled, the research desk randomly researches into any appliance in the pool instead of the fixed progression path. 
    When disabled, the research desk works as in vanilla."""
    display_name = "Random Research"
    default = 0


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
    day_leases_enabled: DayLeasesEnabled
    day_lease_interval: DayLeaseInterval
    day_lease_mode: DayLeaseMode
    dish_lease_scope: DishLeaseScope
    day_leases_progressive: DayLeasesProgressive
    player_speed_upgrade_count: PlayerSpeedUpgradeCount
    appliance_speed_upgrade_count: ApplianceSpeedUpgradeCount
    appliance_speed_mode: ApplianceSpeedMode
    money_cap_enabled: MoneyCapEnabled
    starting_money_cap: StartingMoneyCap
    money_cap_increase_amount: MoneyCapIncreaseAmount
    money_cap_increase_count: MoneyCapIncreaseCount
    money_cap_activation: MoneyCapActivation
    appliance_unlocks: ApplianceUnlocks
    appliance_unlock_pool_size: ApplianceUnlockPoolSize
    appliance_unlock_grants_appliance: ApplianceUnlockGrantsAppliance
    unlocked_appliances_in_shop: UnlockedAppliancesInShop
    decoration_unlocks: DecorationUnlocks
    trap_chance: TrapChance
    trap_weights: TrapWeights
    patience_filler_percent: PatienceFillerPercent
    customer_filler_percent: CustomerFillerPercent
    group_size_filler_percent: GroupSizeFillerPercent
    mess_reduction_percent: MessReductionPercent
    coin_filler_percent: CoinFillerPercent
    setting_checks: SettingChecks
    setting_check_mode: SettingCheckMode
    setting_extra_checks: SettingExtraChecks
    starting_cards: StartingCards
    starting_cards_amount: StartingCardsAmount
    extra_starting_cards: ExtraStartingCards
    starting_group_size: StartingGroupSize
    global_patience_enabled: GlobalPatienceEnabled
    global_patience_upgrade_count: GlobalPatienceUpgradeCount
    global_patience_starting_debuff: GlobalPatienceStartingDebuff
    achievement_check_mode: AchievementCheckMode
    blueprint_check_count: BlueprintCheckCount
    blueprint_base_price: BlueprintBasePrice
    blueprint_price_increase: BlueprintPriceIncrease
    reroll_check_count: RerollCheckCount
    allow_save_file_editing: AllowSaveFileEditing
    random_research: RandomResearch
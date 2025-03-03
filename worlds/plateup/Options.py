from dataclasses import dataclass, field
from Options import Choice, PerGameCommonOptions, ItemSet, ItemDict, Range, OptionError, Toggle
from typing import Dict, Set

# --- Goal Option ---
class Goal(Choice):
    """Set the franchise goal for completion."""
    display_name = "Goal"
    option_franchise_once = 0
    option_franchise_twice = 1
    option_franchise_thrice = 2
    default = 0

class DishCount(Range):
    """Select how many dishes the player starts with (between 1-15).

    You can define additional values between the minimum and maximum.
    - Minimum value: 1
    - Maximum value: 15
    """
    display_name = "Starting Dish Count"
    range_start = 1  # Minimum: 1 dish
    range_end = 15  # Maximum: 15 dishes
    default = 1  # Default to 1 dish

# Deathlink Toggle
class DeathLink(Toggle):
    """When you die, everyone who enabled death link dies. Of course, the reverse is true too."""
    display_name = "Death Link"
    rich_text_doc = True
    default = 0  # Default is disabled

# Deathlink Behavior Choice
class DeathLinkBehavior(Choice):
    """Choose what happens when DeathLink triggers:
    
    - **Reset Run:** The entire run is reset.
    - **Reset to Last Star:** Resets to the last earned star instead of fully resetting.
    """
    display_name = "Death Link Behavior"
    option_reset_run = 0
    option_reset_to_last_star = 1
    default = 0  # Default behavior is resetting the run



class Accessibility(Choice):
    """Set rules for reachability of your items/locations.
    
    - **Full:** Ensure everything can be reached and acquired.
    - **Minimal:** Ensure what is needed to reach your goal can be acquired.
    """
    display_name = "Accessibility"
    option_full = 0
    option_minimal = 1
    default = 0  # Default to "Full"

# --- PlateUp Options ---
class PlateUpOptions(PerGameCommonOptions):
    goal: Goal
    dish: DishCount
    death_link: DeathLink
    death_link_behavior: DeathLinkBehavior



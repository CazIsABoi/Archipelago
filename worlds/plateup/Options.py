# Options.py
from Options import Range, OptionList

class PlateUpGoal(OptionList):
    """Which PlateUp Goal do you want to use?"""
    display_name = "PlateUp Goal"
    # Each entry has an integer key and a string description
    options = {
        0: "Franchise Once",
        1: "Franchise Twice",
    }

    default = 0

plateup_options = {
    "plateup_goal": PlateUpGoal
}
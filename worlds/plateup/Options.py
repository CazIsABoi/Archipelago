from Options import OptionList

class PlateUpGoal(OptionList):
    """Which PlateUp Goal do you want to use?"""
    display_name = "PlateUp Goal"
    # Only one option available now
    options = {
        0: "Franchise Twice",
    }
    default = 0

plateup_options = {
    "plateup_goal": PlateUpGoal
}

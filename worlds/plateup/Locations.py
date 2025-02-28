from typing import Dict
from BaseClasses import Location

class PlateUpLocation(Location):
    game = "plateup"

LOCATIONS: Dict[str, int] = {
    "Lose a Run": 100000,
    "Complete First Day": 100001,
    "Complete Second Day": 100002,
    "Complete Third Day": 100003,
    "First Star": 1000031,
    "Complete Fourth Day": 100004,
    "Complete Fifth Day": 100005,
    "Complete Day 6": 100006,
    "Second Star": 1000061,
    "Complete Day 7": 100007,
    "Complete Day 8": 100008,
    "Complete Day 9": 100009,
    "Third Star": 1000091,
    "Complete Day 10": 100010,
    "Complete Day 11": 100011,
    "Complete Day 12": 100012,
    "Fourth Star": 10000121,
    "Complete Day 13": 100013,
    "Complete Day 14": 100014,
    "Complete Day 15": 100015,
    "Fifth Star": 10000151,
    "Complete Day 16": 100016,
    "Complete Day 17": 100017,
    "Complete Day 18": 100018,
    "Complete Day 19": 100019,
    "Complete Day 20": 100020,
    "Franchise Once": 200000,
    "Complete First Day After Franchised": 200001,
    "Complete Second Day After Franchised": 200002,
    "Complete Third Day After Franchised": 200003,
    "First Star Franchised": 2000031,
    "Complete Fourth Day After Franchised": 200004,
    "Complete Fifth Day After Franchised": 200005,
    "Complete Day 6 After Franchised": 200006,
    "Second Star Franchised": 2000061,
    "Complete Day 7 After Franchised": 200007,
    "Complete Day 8 After Franchised": 200008,
    "Complete Day 9 After Franchised": 200009,
    "Third Star Franchised": 2000091,
    "Complete Day 10 After Franchised": 200010,
    "Complete Day 11 After Franchised": 200011,
    "Complete Day 12 After Franchised": 200012,
    "Fourth Star Franchised": 20000121,
    "Complete Day 13 After Franchised": 200013,
    "Complete Day 14 After Franchised": 200014,
    "Complete Day 15 After Franchised": 200015,
    "Fifth Star Franchised": 20000151,
    "Complete Day 16 After Franchised": 200016,
    "Complete Day 17 After Franchised": 200017,
    "Complete Day 18 After Franchised": 200018,
    "Complete Day 19 After Franchised": 200019,
    "Complete Day 20 After Franchised": 200020,
    "Franchise Twice": 300000,
    "Complete First Day After Franchised Twice": 300001,
    "Complete Second Day After Franchised Twice": 300002,
    "Complete Third Day After Franchised Twice": 300003,
    "First Star Franchised Twice": 3000031,
    "Complete Fourth Day After Franchised Twice": 300004,
    "Complete Fifth Day After Franchised Twice": 300005,
    "Complete Day 6 After Franchised Twice": 300006,
    "Second Star Franchised Twice": 3000061,
    "Complete Day 7 After Franchised Twice": 300007,
    "Complete Day 8 After Franchised Twice": 300008,
    "Complete Day 9 After Franchised Twice": 300009,
    "Third Star Franchised Twice": 3000091,
    "Complete Day 10 After Franchised Twice": 300010,
    "Complete Day 11 After Franchised Twice": 300011,
    "Complete Day 12 After Franchised Twice": 300012,
    "Fourth Star Franchised Twice": 30000121,
    "Complete Day 13 After Franchised Twice": 300013,
    "Complete Day 14 After Franchised Twice": 300014,
    "Complete Day 15 After Franchised Twice": 300015,
    "Fifth Star Franchised Twice": 30000151,
    "Complete Day 16 After Franchised Twice": 300016,
    "Complete Day 17 After Franchised Twice": 300017,
    "Complete Day 18 After Franchised Twice": 300018,
    "Complete Day 19 After Franchised Twice": 300019,
    "Complete Day 20 After Franchised Twice": 300020,
    "Franchise Thrice": 400000,
}

# Dish Dictionary with their ID prefixes
dish_dictionary = {
    101: "Salad",
    102: "Steak",
    103: "Burger",
    104: "Coffee",
    105: "Pizza",
    106: "Dumplings",
    107: "Turkey",
    108: "Pie",
    109: "Cakes",
    110: "Spaghetti",
    111: "Fish",
    112: "Tacos",
    113: "Hot Dogs",
    114: "Breakfast",
    115: "Stir Fry",
}

def add_filtered_dish_locations(selected_dishes):
    """Only adds locations for selected dishes to the global LOCATIONS dictionary"""
    global LOCATIONS

    for dish_id in selected_dishes:
        dish_name = dish_dictionary[dish_id]  # Retrieve dish name
        for day in range(1, 16):  # Days 1 to 15
            location_name = f"{dish_name} - Day {day}"
            location_id = (dish_id * 1000) + day  # Unique ID
            LOCATIONS[location_name] = location_id  # Add named location


    print(f"LOCATIONS after filtering: {list(LOCATIONS.keys())}")

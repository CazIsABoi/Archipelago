from typing import List
from BaseClasses import Region, ItemClassification, LocationProgressType
from worlds.AutoWorld import World
from .Locations import LOCATIONS, PlateUpLocation
from .Items import ITEMS, PlateUpItem

class PlateUpWorld(World):
    game = "plateup"
    
    # Build mapping from item names to their IDs.
    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}  # e.g. {"Hob": 1001, ...}
    location_name_to_id = LOCATIONS

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.progression):
        return PlateUpItem(name, classification, self.item_name_to_id[name], self.player)

    def create_items(self):
        self.itempool = []
        for name in self.item_name_to_id:
            # Use the helper to create each item.
            self.itempool.append(self.create_item(name, ItemClassification.progression))
        # Add these items to the multiworld's overall item pool.
        self.multiworld.itempool += self.itempool

    @classmethod
    def get_filler_item_name(cls):
        return "Hob"

    def create_regions(self):
        # Create a required "Menu" region.
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)
        
        # Create a main region that will contain all PlateUp locations.
        main_region = Region("Main", self.player, self.multiworld)
        self.multiworld.regions.append(main_region)
        
        # Connect the Menu region to the Main region bidirectionally.
        menu_region.connect(main_region)
        main_region.connect(menu_region)
        
        # Iterate through the locations and mark only the first 15 as progression.
        for loc_name, loc_id in LOCATIONS.items():
            loc = PlateUpLocation(self.player, loc_name, loc_id, parent=main_region)
            if loc_id < 100016:  # Only days 1-15 are progression locations.
                loc.progress_type = LocationProgressType.PRIORITY
            else:
                loc.progress_type = LocationProgressType.DEFAULT
            main_region.locations.append(loc)

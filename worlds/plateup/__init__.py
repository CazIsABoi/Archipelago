from typing import List
from BaseClasses import Region, ItemClassification, LocationProgressType
from worlds.AutoWorld import World
from .Locations import LOCATIONS, PlateUpLocation
from .Items import ITEMS, PlateUpItem

class PlateUpWorld(World):
    game = "plateup"
    
    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = LOCATIONS

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.progression):
        return PlateUpItem(name, classification, self.item_name_to_id[name], self.player)

def create_items(self):
    self.itempool = []
    for name, (code, classification) in ITEMS.items():
        self.itempool.append(PlateUpItem(name, classification, code, self.player))
    self.multiworld.itempool += self.itempool


    @classmethoda
    
    def get_filler_item_name(cls):
        return "Hob"

    def create_regions(self):

        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)
        
        main_region = Region("Main", self.player, self.multiworld)
        self.multiworld.regions.append(main_region)
        
        menu_region.connect(main_region)
        main_region.connect(menu_region)
        
        for loc_name, loc_id in LOCATIONS.items():
            loc = PlateUpLocation(self.player, loc_name, loc_id, parent=main_region)
            if (100001 <= loc_id <= 100015) or (200000 <= loc_id <= 200015):
                loc.progress_type = LocationProgressType.PRIORITY
            else:
                loc.progress_type = LocationProgressType.DEFAULT
            main_region.locations.append(loc)

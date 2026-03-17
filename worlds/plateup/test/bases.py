from test.bases import WorldTestBase
from ..World import PlateUpWorld


class PlateUpTestBase(WorldTestBase):
    game = "PlateUp"
    world: PlateUpWorld

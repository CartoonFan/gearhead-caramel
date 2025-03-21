import gears
import pbge
import pygame

from pbge.randmaps.decor import OmniDec
from pbge.randmaps.rooms import FuzzyRoom, OpenRoom, ClumpyRoom
from . import ghterrain, ghwaypoints
import random


class MSWreckageDecor(OmniDec):
    FLOOR_DECOR = (ghterrain.MSWreckage,)
    FLOOR_FILL_FACTOR = 0.15


class DragonToothDecor(OmniDec):
    FLOOR_DECOR = (ghterrain.DragonTeethWall, ghterrain.DragonTeethWall, ghterrain.Forest)
    FLOOR_FILL_FACTOR = 0.25
    PLACE_FLOOR_DECOR_AS_WALL = True


class ForestRoom(ClumpyRoom):
    CLUMP_WALL = ghterrain.Forest


class BushesRoom(ClumpyRoom):
    CLUMP_WALL = ghterrain.Bushes


class GrassRoom(ClumpyRoom):
    CLUMP_FLOOR = ghterrain.GreenZoneGrass


class FlagstoneRoom(ClumpyRoom):
    CLUMP_FLOOR = ghterrain.Flagstone


class ToxicSludgeRoom(ClumpyRoom):
    CLUMP_FLOOR = ghterrain.ToxicSludge


class MechaScaleResidentialArea(pbge.randmaps.rooms.MiniCityRoom):
    ROAD_TERRAIN = ghterrain.Pavement
    ROADSIDE_TERRAIN = (
        ghterrain.Forest, ghterrain.MSResidentialBuildings, ghterrain.MSResidentialBuildings,
        ghterrain.MSResidentialBuildings, ghterrain.MSResidentialBuildings, ghterrain.MSResidentialBuildings
    )


class IndicatedRoom(OpenRoom):
    def build(self, gb: gears.GearHeadScene, archi):
        super().build(gb, archi)
        for x in range(self.area.x+1, self.area.x + self.area.width-1):
            gb.set_decor(x, self.area.y, ghterrain.BorderMarkerN)
            gb.set_decor(x, self.area.y + self.area.height - 1, ghterrain.BorderMarkerS)
        for y in range(self.area.y+1, self.area.y + self.area.height-1):
            gb.set_decor(self.area.x, y, ghterrain.BorderMarkerW)
            gb.set_decor(self.area.x + self.area.width - 1, y, ghterrain.BorderMarkerE)
        gb.set_decor(self.area.x, self.area.y, ghterrain.BorderMarkerNW)
        gb.set_decor(self.area.x, self.area.y+self.area.height-1, ghterrain.BorderMarkerSW)
        gb.set_decor(self.area.x+self.area.width-1, self.area.y, ghterrain.BorderMarkerNE)
        gb.set_decor(self.area.x+self.area.width-1, self.area.y+self.area.height-1, ghterrain.BorderMarkerSE)


class HighwayRoom(OpenRoom):
    DEFAULT_FLOOR = ghterrain.Pavement
    def build(self, gb, archi):
        super().build(gb, archi)
        gb.fill(self.area, floor=self.DEFAULT_FLOOR)


class LakeRoom(FuzzyRoom):
    def build(self, gb, archi):
        super().build(gb, archi)

        # Add some random lake blobs.
        if self.area.width > 8 and self.area.height > 8:
            for t in range(random.randint(1, 3)):
                x = random.randint(self.area.left + 3, self.area.right - 4)
                y = random.randint(self.area.top + 3, self.area.bottom - 4)
                s = random.randint(3, 5)
                gb.fill_blob(pygame.Rect(x - 1, y - 1, s, s), floor=ghterrain.Water)
        else:
            mydest = pygame.Rect(0, 0, 3, 3)
            mydest.center = self.area.center
            gb.fill(mydest, floor=ghterrain.Water)


class WreckageRoom(FuzzyRoom):
    DECORATE = MSWreckageDecor(floor_fill_factor=0.2)


class DragonToothRoom(FuzzyRoom):
    DECORATE = DragonToothDecor()


class MSRuinsRoom(FuzzyRoom):
    DECORATE = MSWreckageDecor(floor_fill_factor=0.05)

    def build(self, gb, archi):
        super().build(gb, archi)

        # Add some random ruins.
        ruin_list = list()
        safe_area = self.area.inflate(-4, -4)
        if safe_area.width > 8 and safe_area.height > 8:
            for t in range(random.randint(3, 8)):
                x = random.randint(self.area.left + 3, self.area.right - 4)
                y = random.randint(self.area.top + 3, self.area.bottom - 4)
                myroomdest = pygame.Rect(0, 0, random.randint(2, 4), random.randint(2, 4))
                myroomdest.center = (x, y)
                myroomdest = myroomdest.clamp(safe_area)
                if myroomdest.inflate(2, 2).collidelist(ruin_list) == -1:
                    gb.fill(myroomdest, wall=ghterrain.MSRuinedWall)
                    ruin_list.append(myroomdest)
        else:
            mydest = pygame.Rect(0, 0, 3, 3)
            mydest.center = self.area.center
            gb.fill(mydest, wall=ghterrain.MSRuinedWall)


class BarArea(OpenRoom):
    MIN_RANDOM_SIZE = 3
    MAX_RANDOM_SIZE = 5
    COUNTER_TYPE = ghterrain.BarTerrain
    def build(self, gb: gears.GearHeadScene, archi):
        super().build(gb, archi)

        # Add a bar along the south and maybe along one side.
        left_counter_ok, right_counter_ok = True, True
        x0 = self.area.x
        x1 = self.area.x + self.area.width - 1
        y = self.area.y + self.area.height - 1
        if self.probably_blocks_movement(gb, x0-1, y, archi):
            x0 += 1
            left_counter_ok = False
        if self.probably_blocks_movement(gb, x1+1, y, archi):
            x1 -= 1
            right_counter_ok = False

        if x1 > x0:
            for x in range(x0, x1+1):
                gb.set_wall(x, y, self.COUNTER_TYPE)

            if self.area.height > 2:
                if random.randint(1, 3) == 1 and left_counter_ok:
                    for y in range(self.area.y + 1, self.area.y + self.area.height):
                        gb.set_wall(x0, y, self.COUNTER_TYPE)

                if random.randint(1, 3) == 1:
                    for y in range(self.area.y + 1, self.area.y + self.area.height):
                        gb.set_wall(x1, y, self.COUNTER_TYPE)


class ShopCounterArea(BarArea):
    COUNTER_TYPE = ghterrain.ShopCounterTerrain


class WorkbenchArea(BarArea):
    COUNTER_TYPE = ghterrain.WorkbenchTerrain


class LongVehicleRoom(pbge.randmaps.rooms.Room):
    MIN_RANDOM_SIZE = 12
    # Suggested dimensions: 16x8 or longer. Keep the height even if possible.

    def build(self, gb: gears.GearHeadScene, archi):
        # Call to super just to keep PyCharm happy.
        super().build(gb, archi)

        # Okay, so we're building a long vehicle like a Mobile HQ or a Field Hospital. Stick the cabin to the west
        # and a larger open room to the east.
        archi = self.archi or archi
        # self.dont_touch_edge(gb)

        self.cabin1 = pygame.Rect(0, 0, 6, 3)
        self.cabin1.midleft = self.area.midleft
        self.cabin1.y -= 1
        gb.fill(self.cabin1, floor=archi.floor_terrain, wall=None)
        self.cabin2 = pygame.Rect(self.cabin1.x + 1, self.cabin1.y - 1, 2, 5)
        gb.fill(self.cabin2, floor=archi.floor_terrain, wall=None)

        gb.set_decor(self.cabin1.x, self.cabin1.top, ghterrain.KenneyChairWest)
        gb.set_decor(self.cabin1.x, self.cabin1.bottom - 1, ghterrain.KenneyChairWest)

        my_orientation = random.sample((0, 2), 2)
        gb.set_decor(self.cabin1.x - 1, self.cabin1.top + my_orientation[0], ghterrain.Dashboard1)
        gb.set_decor(self.cabin1.x - 1, self.cabin1.top + 1, ghterrain.Dashboard2)
        gb.set_decor(self.cabin1.x - 1, self.cabin1.top + my_orientation[1], ghterrain.Dashboard3)

        if random.randint(1, 3) != 2:
            x_off = random.randint(0, 1)
            gb.set_decor(self.cabin2.x + x_off, self.cabin2.top, ghterrain.KenneyChairNorth)
            gb.set_decor(self.cabin2.x + x_off, self.cabin2.top - 1, ghterrain.VehicleControlPanel)
            if random.randint(1, 5) == 2:
                x_off = 1 - x_off
                gb.set_decor(self.cabin2.x + x_off, self.cabin2.top, ghterrain.KenneyChairNorth)
                gb.set_decor(self.cabin2.x + x_off, self.cabin2.top - 1, ghterrain.VehicleControlPanel)

        if random.randint(1, 3) != 2:
            x_off = random.randint(0, 1)
            gb.set_decor(self.cabin2.x + x_off, self.cabin2.bottom - 1, ghterrain.KenneyChairSouth)
            if random.randint(1, 5) == 2:
                x_off = 1 - x_off
                gb.set_decor(self.cabin2.x + x_off, self.cabin2.bottom - 1, ghterrain.KenneyChairSouth)

        self.body_area: pygame.Rect = self.area.inflate(-4, 0)
        self.body_area.x += 2
        self.body_area.h -= 1
        # body.width -= 4
        gb.fill(self.body_area, floor=archi.floor_terrain, wall=None)


class MechaScaleFortressRoom(pbge.randmaps.rooms.Room):
    FLOOR_TERRAIN = ghterrain.MSConcreteSlabFloor
    WALL_TERRAIN = ghterrain.MechaFortressWall
    def build(self, gb, archi):
        gb.fill(self.area.inflate(2, 2), floor=archi.floor_terrain, wall=None)
        gb.fill(self.area, floor=self.FLOOR_TERRAIN)
        for x in range(self.area.w // 2 - 1):
            gb.set_wall(x + self.area.left, self.area.top, self.WALL_TERRAIN)
            gb.set_wall(self.area.right - x - 1, self.area.top, self.WALL_TERRAIN)
            gb.set_wall(x + self.area.left, self.area.bottom - 1, self.WALL_TERRAIN)
            gb.set_wall(self.area.right - x - 1, self.area.bottom - 1, self.WALL_TERRAIN)
        for y in range(self.area.h // 2 - 1):
            gb.set_wall(self.area.left, y + self.area.top, self.WALL_TERRAIN)
            gb.set_wall(self.area.left, self.area.bottom - y - 1, self.WALL_TERRAIN)
            gb.set_wall(self.area.right - 1, y + self.area.top, self.WALL_TERRAIN)
            gb.set_wall(self.area.right - 1, self.area.bottom - y - 1, self.WALL_TERRAIN)


class MobileHQRoom(LongVehicleRoom):
    MIN_RANDOM_SIZE = 12
    # Suggested dimensions: 16x8 or longer. Keep the height even if possible.

    def build(self, gb: gears.GearHeadScene, archi):
        # Call to super for the basic vehicle details.
        super().build(gb, archi)

        # Stick some command tables in the middle and some control panels along the top wall. Done.
        if random.randint(1,3) != 1:
            gb.set_decor(*self.body_area.center, ghterrain.KenneyCommandTable)
        elif random.randint(1,23) != 5:
            gb.set_decor(self.body_area.centerx - self.body_area.w//4, self.body_area.centery, ghterrain.KenneyCommandTable)
            gb.set_decor(self.body_area.centerx + self.body_area.w//4, self.body_area.centery, ghterrain.KenneyCommandTable)

        for x in range(self.body_area.w - 2):
            if random.randint(1,5) == 3:
                gb.set_decor(self.body_area.x + x, self.body_area.y - 1, ghterrain.VehicleControlPanel)


class FieldHospitalRoom(LongVehicleRoom):
    MIN_RANDOM_SIZE = 12
    # Suggested dimensions: 16x8 or longer. Keep the height even if possible.

    POSSIBLE_TANKS = (ghterrain.BiotankTerrain, ghterrain.EmptyBiotankTerrain)

    def build(self, gb: gears.GearHeadScene, archi):
        # Call to super for the basic vehicle details.
        super().build(gb, archi)

        # Stick some flotation tanks in the middle and some control panels along the top wall. Done.
        if random.randint(1,3) != 1:
            gb.set_decor(self.body_area.centerx - self.body_area.w//4+1, self.body_area.centery, random.choice(self.POSSIBLE_TANKS))
            gb.set_decor(self.body_area.centerx + self.body_area.w//4+1, self.body_area.centery, random.choice(self.POSSIBLE_TANKS))
        elif random.randint(1,5) != 5:
            gb.set_decor(self.body_area.centerx+2, self.body_area.centery, random.choice(self.POSSIBLE_TANKS))

        half_width = (self.body_area.w - 2)//2
        medical_sign = random.randint(1,half_width-1)
        for x in range(half_width):
            if x == medical_sign:
                gb.set_decor(self.body_area.x + x, self.body_area.y - 1, ghterrain.HospitalSign)
            elif random.randint(1,5) == 3:
                gb.set_decor(self.body_area.x + x, self.body_area.y - 1, ghterrain.VehicleControlPanel)

            if x % 2 == 0:
                mybed = ghwaypoints.Bunk(gb, (self.body_area.centerx+x, self.body_area.y))

""" How Terrain Works: Each terraintype is supposed to be a singleton, so
    every reference to a particular terrain type points at the same thing,
    and there will be no problems with serialization. So, to create a new
    terrain type, create a subclass of the closest match and change its
    constants.
"""
from .. import Singleton
from .movement import Walking, Flying, Vision
import random


# Each terrain type can have up to four rendering actions:
# - render_bottom draws a layer beneath all models
# - render_biddle draws a layer above a submerged model, but below a non-submerged one
#   biddle = between bottom and middle
# - render_middle draws a layer beneath a model in the same tile
# - render_top draws a layer on top of a model in the same tile

class FloorBorder(object):
    # Certain floor tiles will draw an overlapping fringe on top of other floor tiles.
    # A terrain will draw its border on top of terrain with lower border_priority.
    def __init__(self, border_image):
        self.border_image = border_image

    def floor_border_matches_self(self, scene, x, y):
        myfloor = scene.get_floor(x, y)
        return myfloor and myfloor.border is self

    def pre_calc_border_data(self, view, x, y):
        """Return the floor border frame for this tile."""
        edges = 0
        check_nw, check_ne, check_sw, check_se = True, True, True, True
        if self.floor_border_matches_self(view.scene, x - 1, y):
            edges += 1
            check_nw, check_sw = False, False
        if self.floor_border_matches_self(view.scene, x, y-1):
            edges += 2
            check_nw, check_ne = False, False
        if self.floor_border_matches_self(view.scene, x + 1, y):
            edges += 4
            check_ne, check_se = False, False
        if self.floor_border_matches_self(view.scene, x, y+1):
            edges += 8
            check_sw, check_se = False, False
        corners = 16
        if check_nw and self.floor_border_matches_self(view.scene, x-1, y-1):
            corners += 1
        if check_ne and self.floor_border_matches_self(view.scene, x+1, y-1):
            corners += 2
        if check_se and self.floor_border_matches_self(view.scene, x+1, y+1):
            corners += 4
        if check_sw and self.floor_border_matches_self(view.scene, x-1, y+1):
            corners += 8

        if edges > 0 or corners > 16:
            return edges, corners

    def render(self, dest, view, x, y, edges, corners):
        # Step One: See if there are any of the terrain in question to
        # deal with.
        if edges > 0 or corners > 16:
            spr = view.get_terrain_sprite(self.border_image, (x, y))
            if edges > 0:
                spr.render(dest, edges)
            if corners > 16:
                spr.render(dest, corners)


class DuckTerrain(object):
    def __init__(self, name="Duck Terrain", image_bottom='', image_biddle='', image_middle='', image_top='', blocks=(),
                 frame=0, altitude=0, colors=None, transparent=False, border=None, border_priority=0,
                 movement_cost=None):
        self.name = name
        self.image_bottom = image_bottom
        self.image_biddle = image_biddle
        self.image_middle = image_middle
        self.image_top = image_top
        self.blocks = tuple(blocks)
        self.frame = frame
        self.altitude = altitude
        self.colors = colors
        self.transparent = transparent
        self.border = border
        self.border_priority = border_priority
        self.movement_cost = dict()
        if movement_cost:
            self.movement_cost.update(movement_cost)

    def render_top(self, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_top:
            spr = view.get_terrain_sprite(self.image_top, (x, y), transparent=self.transparent, colors=self.colors)
            spr.render(dest, self.frame)

    def render_biddle(self, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_biddle:
            spr = view.get_terrain_sprite(self.image_biddle, (x, y), transparent=self.transparent, colors=self.colors)
            spr.render(dest, self.frame)

    def render_middle(self, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if self.image_middle:
            spr = view.get_terrain_sprite(self.image_middle, (x, y), transparent=self.transparent, colors=self.colors)
            spr.render(dest, self.frame)

    def render_bottom(self, dest, view, x, y):
        """Draw terrain that should appear behind a model in the same tile"""
        if self.image_bottom:
            spr = view.get_terrain_sprite(self.image_bottom, (x, y), transparent=self.transparent, colors=self.colors)
            spr.render(dest, self.frame)

    def place(self, scene, pos):
        if scene.on_the_map(*pos):
            scene._map[pos[0]][pos[1]].decor = self

    def __str__(self):
        return self.name

    @classmethod
    def from_other_terrain(cls, terr, colors=None):
        myduck = cls(terr.name, terr.image_bottom, terr.image_biddle, terr.image_middle, terr.image_top, terr.blocks,
                     terr.frame, terr.altitude, colors, terr.transparent, terr.border, terr.border_priority,
                     terr.movement_cost)
        return myduck

    @classmethod
    def get_south_duck(cls, terr, colors=None):
        # For "on the wall" terrain, take the/a south-facing frame.
        myduck = cls.from_other_terrain(terr, colors)
        if hasattr(terr, "SOUTH_FRAME"):
            myduck.frame = terr.SOUTH_FRAME
        elif hasattr(terr, "south_frames"):
            myduck.frame = random.choice(terr.south_frames)
        return myduck

    @classmethod
    def get_east_duck(cls, terr, colors=None):
        # For "on the wall" terrain, take the/a south-facing frame.
        myduck = cls.from_other_terrain(terr, colors)
        if hasattr(terr, "EAST_FRAME"):
            myduck.frame = terr.SOUTH_FRAME
        elif hasattr(terr, "east_frames"):
            myduck.frame = random.choice(terr.south_frames)
        return myduck


class Terrain(Singleton):
    name = 'Undefined Terrain'
    image_bottom = ''
    image_biddle = ''
    image_middle = ''
    image_top = ''
    blocks = ()
    frame = 0
    altitude = 0
    transparent = False
    # If this tile has a border, it will draw its border on nearby tiles with a lower
    # border priority.
    border = None
    border_priority = 0
    # You may set different movement costs by movement mode;
    # defaults to x1.0.
    movement_cost = {}
    tags = {}

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_top:
            spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frame)

    @classmethod
    def render_biddle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_biddle:
            spr = view.get_terrain_sprite(cls.image_biddle, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frame)

    @classmethod
    def render_middle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_middle:
            spr = view.get_terrain_sprite(cls.image_middle, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frame)

    @classmethod
    def render_bottom(cls, dest, view, x, y):
        """Draw terrain that should appear behind a model in the same tile"""
        if cls.image_bottom:
            spr = view.get_terrain_sprite(cls.image_bottom, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frame)

    @classmethod
    def place(cls, scene, pos):
        if scene.on_the_map(*pos):
            scene._map[pos[0]][pos[1]].decor = cls


class VariableTerrain(Terrain):
    frames = (0, 1, 2, 3, 4, 5, 6, 7)

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_top:
            spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frames[view.get_pseudo_random(x, y) % len(cls.frames)])

    @classmethod
    def render_middle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_middle:
            spr = view.get_terrain_sprite(cls.image_middle, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frames[view.get_pseudo_random(x, y) % len(cls.frames)])

    @classmethod
    def render_biddle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_biddle:
            spr = view.get_terrain_sprite(cls.image_biddle, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frames[view.get_pseudo_random(x, y) % len(cls.frames)])

    @classmethod
    def render_bottom(cls, dest, view, x, y):
        """Draw terrain that should appear behind a model in the same tile"""
        if cls.image_bottom:
            spr = view.get_terrain_sprite(cls.image_bottom, (x, y), transparent=cls.transparent)
            spr.render(dest, cls.frames[view.get_pseudo_random(x, y) % len(cls.frames)])


class AnimTerrain(Terrain):
    frames = (0, 1, 2, 3, 4, 5, 6, 7)
    anim_delay = 4
    position_dependent = True

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_top:
            spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
            if cls.position_dependent:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay + (x + y) * 4) % len(cls.frames)])
            else:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay) % len(cls.frames)])

    @classmethod
    def render_middle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_middle:
            spr = view.get_terrain_sprite(cls.image_middle, (x, y), transparent=cls.transparent)
            if cls.position_dependent:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay + (x + y) * 4) % len(cls.frames)])
            else:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay) % len(cls.frames)])

    @classmethod
    def render_biddle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model under the same tile"""
        if cls.image_biddle:
            spr = view.get_terrain_sprite(cls.image_biddle, (x, y), transparent=cls.transparent)
            if cls.position_dependent:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay + (x + y) * 4) % len(cls.frames)])
            else:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay) % len(cls.frames)])

    @classmethod
    def render_bottom(cls, dest, view, x, y):
        """Draw terrain that should appear behind a model in the same tile"""
        if cls.image_bottom:
            spr = view.get_terrain_sprite(cls.image_bottom, (x, y), transparent=cls.transparent)
            if cls.position_dependent:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay + (x + y) * 4) % len(cls.frames)])
            else:
                spr.render(dest, cls.frames[(view.phase // cls.anim_delay) % len(cls.frames)])


class WallTerrain(Terrain):
    blocks = (Walking, Flying, Vision)
    bordername = 'terrain_wbor_tall.png'
    TAKES_WALL_DECOR = True

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        wal, bor = view.tile_data.get((x,y,cls), (0,-1))

        if wal is not None:
            spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
            spr.render(dest, wal)
        if bor > 0:
            spr = view.get_named_sprite(cls.bordername)
            spr.render(dest, bor)

    @classmethod
    def prep_tile_data(cls, view, x, y):
        if cls.bordername:
            bor = view.calc_border_score(x, y)
            if bor == 15:
                wal = None
            else:
                wal = view.calc_wall_score(x, y, WallTerrain)
        else:
            bor = -1
            wal = view.calc_wall_score(x, y, WallTerrain)\

        view.tile_data[(x,y,cls)] = (wal, bor)


class DoorTerrain(WallTerrain):
    # A singleton terrain class; use these objects as tokens for maps.
    @classmethod
    def render_bottom(cls, dest, view, x, y):
        if view.space_or_door_to_south(x, y):
            wal = 1
        else:
            wal = 0

        spr = view.get_terrain_sprite(cls.image_bottom, (x, y), transparent=cls.transparent)
        spr.render(dest, cls.frame + wal)

    @classmethod
    def render_middle(cls, dest, view, x, y):
        if view.space_to_south(x, y):
            wal = 1
        else:
            wal = 0

        spr = view.get_terrain_sprite(cls.image_middle, (x, y), transparent=cls.transparent)
        spr.render(dest, cls.frame + wal)

    @classmethod
    def render_top(cls, dest, view, x, y):
        if view.space_to_south(x, y):
            wal = 1
        else:
            wal = 0

        spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
        spr.render(dest, cls.frame + wal)


class RoadTerrain(Terrain):
    @classmethod
    def render_bottom(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        d = view.calc_decor_score(x, y, RoadTerrain)
        spr = view.get_terrain_sprite(cls.image_bottom, (x, y), transparent=cls.transparent)
        spr.render(dest, d)


class HillTerrain(Terrain):
    bordername = None

    @classmethod
    def render_middle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        wal, bor = view.tile_data.get((x,y,cls), (0,-1))
        if wal is not None:
            spr = view.get_terrain_sprite(cls.image_middle, (x, y), transparent=cls.transparent)
            spr.render(dest, wal)
        if bor > 0:
            spr = view.get_named_sprite(cls.bordername)
            spr.render(dest, bor)

    @classmethod
    def prep_tile_data(cls, view, x, y):
        if cls.bordername:
            bor = view.calc_border_score(x, y)
            if bor == 15:
                wal = None
            else:
                wal = view.calc_wall_score(x, y, HillTerrain)
        else:
            bor = -1
            wal = view.calc_wall_score(x, y, HillTerrain)

        view.tile_data[(x,y,cls)] = (wal, bor)



class OnTheWallTerrain(Terrain):
    SOUTH_FRAME = 1
    EAST_FRAME = 0

    @classmethod
    def render_top(cls, dest, view, x, y):
        if view.space_to_south(x, y):
            frame = cls.SOUTH_FRAME
        else:
            frame = cls.EAST_FRAME
        spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
        spr.render(dest, frame)


class OnTheWallVariableTerrain(Terrain):
    south_frames = (0, 1, 2, 3, 4)
    east_frames = (5, 6, 7, 8, 9)

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_top:
            spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
            if view.space_to_south(x, y):
                frame = cls.south_frames[view.get_pseudo_random(x, y) % len(cls.south_frames)]
            else:
                frame = cls.east_frames[view.get_pseudo_random(x, y) % len(cls.east_frames)]
            spr.render(dest, frame)


class OnTheWallAnimTerrain(Terrain):
    south_frames = (0, 1, 2, 3, 4)
    east_frames = (5, 6, 7, 8, 9)
    anim_delay = 4

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_top:
            spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
            if view.space_to_south(x, y):
                frames = cls.south_frames
            else:
                frames = cls.east_frames
            spr.render(dest, frames[(view.phase // cls.anim_delay + (x + y) * 4) % len(frames)])


class TerrSetTerrain(Terrain):
    # A terrain type that partners with a TerrSet to arrange a whole bunch of
    # sprite frames into a coherent picture.
    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_top:
            spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
            spr.render(dest, view.scene.data.get((x, y), 0))

    @classmethod
    def render_biddle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_biddle:
            spr = view.get_terrain_sprite(cls.image_biddle, (x, y), transparent=cls.transparent)
            spr.render(dest, view.scene.data.get((x, y), 0))

    @classmethod
    def render_middle(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        if cls.image_middle:
            spr = view.get_terrain_sprite(cls.image_middle, (x, y), transparent=cls.transparent)
            spr.render(dest, view.scene.data.get((x, y), 0))

    @classmethod
    def render_bottom(cls, dest, view, x, y):
        """Draw terrain that should appear behind a model in the same tile"""
        if cls.image_bottom:
            spr = view.get_terrain_sprite(cls.image_bottom, (x, y), transparent=cls.transparent)
            spr.render(dest, view.scene.data.get((x, y), 0))

import random
import pygame
from . import decor
from . import rooms


#  **********************
#  ***   GAPFILLERS   ***
#  **********************

class RoomFiller(object):
    """If this room has empty spots, add some more rooms."""

    def __init__(self, *args, spacing=4):
        self.room_types = list(args)
        self.spacing = spacing

    def __call__(self, gb, room):
        # Determine the areas occupied by rooms.
        closed_area = list()
        for r in room.contents:
            if hasattr(r, "area") and r.area:
                closed_area.append(r.area)

        # Attempt to add some random rooms.
        for t in range(random.randint(5, 20)):
            myroomclass = random.choice(self.room_types)
            myroom = myroomclass()
            myrect = pygame.Rect(0, 0, myroom.width, myroom.height)
            count = 0
            while (count < 100) and not myroom.area:
                myrect.x = random.choice(list(range(room.area.x, room.area.x + room.area.width - myroom.width)))
                myrect.y = random.choice(list(range(room.area.y, room.area.y + room.area.height - myroom.height)))
                if myrect.inflate(self.spacing, self.spacing).collidelist(closed_area) == -1:
                    myroom.area = myrect
                    closed_area.append(myrect)
                count += 1
                if count > 50:
                    if random.randint(1, 3) == 3 and myroom.width > myroom.MIN_RANDOM_SIZE:
                        myroom.width -= 1
                    if random.randint(1, 3) == 3 and myroom.height > myroom.MIN_RANDOM_SIZE:
                        myroom.height -= 1

            if myroom.area:
                room.contents.append(myroom)
            else:
                break


class MonsterFiller(object):
    """If this room has empty spots, add some monster zones."""

    def __init__(self, min_mz=3, max_mz=10, spacing=16):
        self.min_mz = min_mz
        self.max_mz = max_mz
        self.spacing = spacing

    def __call__(self, gb, room):
        # Determine the areas occupied by rooms.
        closed_area = list()
        for r in room.contents:
            if hasattr(r, "area") and r.area:
                closed_area.append(r.area)

        if hasattr(room, "DEFAULT_ROOM"):
            rclass = room.DEFAULT_ROOM
        else:
            rclass = rooms.FuzzyRoom

        # Attempt to add some random rooms.
        for t in range(random.randint(self.min_mz, self.max_mz)):
            myroom = rclass()
            myroom.DECORATE = decor.MonsterDec()
            myrect = pygame.Rect(0, 0, myroom.width, myroom.height)
            count = 0
            while (count < 100) and not myroom.area:
                myrect.x = random.choice(list(range(room.area.x, room.area.x + room.area.width - myroom.width)))
                myrect.y = random.choice(list(range(room.area.y, room.area.y + room.area.height - myroom.height)))
                if myrect.inflate(self.spacing, self.spacing).collidelist(closed_area) == -1:
                    myroom.area = myrect
                    closed_area.append(myrect)
                count += 1
            if myroom.area:
                room.contents.append(myroom)
            else:
                break

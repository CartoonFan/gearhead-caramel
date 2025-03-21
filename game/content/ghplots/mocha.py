from pbge.plots import Plot, Adventure, PlotState
import gears
import pbge
import pygame
from game import teams, ghdialogue
from game.ghdialogue import context
from pbge.scenes.movement import Walking, Flying
from gears.tags import Skimming, Rolling
import random
from pbge.dialogue import Cue, ContextTag, Offer, Reply
from gears import personality, color, stats
import game.content.ghcutscene
from game.content import ghwaypoints, ghterrain, gharchitecture
from game.content.plotutility import AdventureModuleData


# ********************************
# ***   TERRAIN  DEFINITIONS   ***
# ********************************

class WinterMochaSnowdrift(pbge.scenes.terrain.HillTerrain):
    altitude = 20
    image_middle = 'terrain_wintermocha_snowdrift.png'
    bordername = ''
    blocks = (Walking, Skimming, Rolling)


class WinterMochaHangarTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_wintermocha_hangar.png'
    blocks = (Walking, Skimming, Rolling, Flying)


class WinterMochaHangar(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = WinterMochaHangarTerrain
    TERRAIN_MAP = (
        (0, 1),
        (2, 3, 4),
        (5, 6, 7, 8),
        (9, 10, 11, 12, 13, 14),
        (15, 16, 17, 18, 19, 20),
        (21, 22, 23, 24, 25, 26),
        (None, 27, 28, 29, 30, 31),
        (None, None, 32, 33, 34, 35),
        (None, None, 36, 37, 38, 39),
        (None, None, WinterMochaSnowdrift, WinterMochaSnowdrift, WinterMochaSnowdrift)
    )
    WAYPOINT_POS = {
        "DOOR": (3, 8), "DRIFT": (3, 9)
    }


class WinterMochaFenceTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_wintermocha_fence.png'
    blocks = (Walking, Skimming, Rolling, Flying)


class WinterMochaFence(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = WinterMochaFenceTerrain
    TERRAIN_MAP = (
        (WinterMochaSnowdrift,),
        (0,),
        (1,),
        (2,),
        (WinterMochaSnowdrift, WinterMochaSnowdrift,)
    )
    WAYPOINT_POS = {
        "DOOR": (0, 2)
    }


class WinterMochaBurningBarrelTerrain(pbge.scenes.terrain.AnimTerrain):
    frames = (6, 7)
    anim_delay = 2
    image_top = 'terrain_wintermocha.png'
    blocks = (Walking, Skimming, Rolling)


class WinterMochaBurningBarrel(ghwaypoints.Waypoint):
    name = 'Barrel Fire'
    TILE = pbge.scenes.Tile(None, None, WinterMochaBurningBarrelTerrain)
    desc = "There's a fire in this barrel. It's nice and warm."


class WinterMochaGeneratorTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 4
    blocks = (Walking, Skimming, Rolling)


class WinterMochaGenerator(ghwaypoints.Waypoint):
    name = 'Geothermal Generator'
    TILE = pbge.scenes.Tile(None, None, WinterMochaGeneratorTerrain)
    desc = "You stand before a geothermal generator."


class WinterMochaToolbox(ghwaypoints.Waypoint):
    name = 'Toolbox'
    TILE = pbge.scenes.Tile(None, None, ghterrain.WinterMochaToolboxTerrain)
    desc = "You stand before an abandoned toolbox."


class WinterMochaHeatLampTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 5
    blocks = (Walking, Skimming, Rolling)


class WinterMochaHeatLamp(ghwaypoints.Waypoint):
    name = 'Heat Lamp'
    TILE = pbge.scenes.Tile(None, None, WinterMochaHeatLampTerrain)
    desc = "You stand before an industrial heat lamp. It's probably being used in the construction of the new arena."


class WinterMochaBarrel(ghwaypoints.Waypoint):
    name = 'Barrel'
    TILE = pbge.scenes.Tile(None, None, ghterrain.WinterMochaBarrelTerrain)
    desc = "You stand before a big container of fuel."


class WinterMochaShovel(ghwaypoints.Waypoint):
    name = 'Broken Shovel'
    TILE = pbge.scenes.Tile(None, None, ghterrain.WinterMochaBrokenShovel)
    desc = "You stand before a broken shovel."


class WinterMochaDomeTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 3
    blocks = (Walking, Skimming, Rolling)


class WinterMochaDome(ghwaypoints.Waypoint):
    name = 'Dome'
    TILE = pbge.scenes.Tile(None, None, WinterMochaDomeTerrain)
    desc = "You stand before a half buried dome. No idea what its function is."


class WinterMochaBlowerTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 8
    blocks = (Walking, Skimming, Rolling)


class WinterMochaBlower(ghwaypoints.Waypoint):
    name = 'Industrial Blower'
    TILE = pbge.scenes.Tile(None, None, WinterMochaBlowerTerrain)
    desc = "You stand before an industrial air blower. It's probably being used in the construction of the new arena."


class WinterMochaPavement(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_pavement.png'


class WinterMochaTruckTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha_mission.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling)


class WinterMochaTruck(ghwaypoints.Waypoint):
    name = 'Wrecked Truck'
    TILE = pbge.scenes.Tile(None, None, WinterMochaTruckTerrain)
    desc = "You stand before one of the trucks from the convoy that was attacked."


class WinterMochaClaymoreTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha_mission.png'
    frame = 1


class WinterMochaClaymore(ghwaypoints.Waypoint):
    name = 'Wrecked Claymore'
    TILE = pbge.scenes.Tile(None, None, WinterMochaClaymoreTerrain)
    desc = "You stand before a totalled mecha."


class WinterMochaFortressRoom(pbge.randmaps.rooms.Room):
    def build(self, gb, archi):
        gb.fill(self.area.inflate(2, 2), floor=archi.floor_terrain, wall=None)
        width = self.area.w - 2
        for x in range(width // 2 - 1):
            gb.set_wall(x + 1 + self.area.left, self.area.top + 1, ghterrain.FortressWall)
            gb.set_wall(self.area.right - x - 1, self.area.top + 1, ghterrain.FortressWall)
            gb.set_wall(x + 1 + self.area.left, self.area.bottom - 1, ghterrain.FortressWall)
            gb.set_wall(self.area.right - x - 1, self.area.bottom - 1, ghterrain.FortressWall)
        height = self.area.h - 2
        for y in range(height // 2 - 1):
            gb.set_wall(self.area.left + 1, y + 1 + self.area.top, ghterrain.FortressWall)
            gb.set_wall(self.area.left + 1, self.area.bottom - y - 1, ghterrain.FortressWall)
            gb.set_wall(self.area.right - 1, y + 1 + self.area.top, ghterrain.FortressWall)
            gb.set_wall(self.area.right - 1, self.area.bottom - y - 1, ghterrain.FortressWall)


# **************************
# ***   UTILITY  STUFF   ***
# **************************

class Snowflake(object):
    def __init__(self, dest, y=0):
        self.dest = dest
        self.x = dest.left + random.randint(1, dest.w)
        self.y = dest.top - 12 + y
        self.dx = random.randint(1, 6) - random.randint(1, 3)
        self.dy = random.randint(2, 4)
        self.frame = random.randint(0, 24)

    def update(self):
        # Return True if this flake should be deleted.
        self.x += self.dx
        self.y += self.dy
        if self.y > self.dest.bottom:
            return True


class SnowField(object):
    def __init__(self):
        self.snow = pbge.image.Image("sys_wm_snow.png", 24, 24)
        self.flakes = list()
        dest = pbge.my_state.screen.get_rect()
        for t in range(random.randint(200,500)):
            self.flakes.append(Snowflake(dest, y=random.randint(1,dest.h)))

    def add_snow(self, dest):
        for t in range(min(random.randint(1, 3), random.randint(1, 3))):
            self.flakes.append(Snowflake(dest))

    def __call__(self):
        dest = pbge.my_state.screen.get_rect()
        self.add_snow(dest)
        for sf in list(self.flakes):
            if sf.update():
                self.flakes.remove(sf)
            else:
                self.snow.render((sf.x, sf.y), sf.frame)


# *****************
# ***   PLOTS   ***
# *****************

class MochaStub(Plot):
    LABEL = "SCENARIO_MOCHA"

    # Creates a Winter Mocha adventure.
    # - Play starts in Mauna, near Vikki and Hyolee.
    #   - The good mecha are snowed into the hangar.
    #   - The bad mecha are in the parking lot.
    # - Head out to battle some raiders.
    # - Win or lose, the end.

    ADVENTURE_MODULE_DATA = AdventureModuleData(
        "Winter Mocha",
        "Several months after the Typhon Incident, you are invited to a charity mecha tournament at the newly built Mauna Arena.",
        (157, 12, 23), "VHS_WinterMocha.png",
    )

    def custom_init(self, nart):
        """Create the world + starting scene."""
        self.ADVENTURE_MODULE_DATA.apply(nart.camp)

        w: gears.GearHeadCampaign = nart.camp
        self.register_element("WORLD", w)
        self.adv = Adventure(world=w)
        self.add_first_locale_sub_plot(nart, locale_type="MOCHA_MAUNA")
        w.convoborder = "sys_wintermocha_convoborder.png"

        return True

MOVAR_CHEAPMEKS = "MOVAR_CHEAPMEKS"
MOVAR_FOUGHTBLITZEN = "MOVAR_FOUGHTBLITZEN"
MOVAR_LANCEMATE = "MOVAR_LANCEMATE"

class FrozenHotSpringCity(Plot):
    # Mauna in winter. There was a heavy snowfall last night, and the mecha
    # hangar is blocked.
    LABEL = "MOCHA_MAUNA"
    active = True
    scope = True

    def custom_init(self, nart):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(60, 60, "Mauna", player_team=team1, scale=gears.scale.HumanScale)
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        myfilter = pbge.randmaps.converter.BasicConverter(WinterMochaSnowdrift)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.SmallSnow, myfilter, mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, myarchi)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        myroom = self.register_element("ROOM", pbge.randmaps.rooms.NoWallRoom(10, 10))

        myent = self.register_element("ENTRANCE", WinterMochaBurningBarrel(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)

        vikki = nart.camp.get_major_npc("Vikki Shingo")
        myroom.contents.append(vikki)
        vikki.portrait='card_f_wintervikki.png'
        self.register_element("VIKKI", vikki)

        myscenegen.contents.append(myroom)

        hangar_gate = self.register_element("HANGAR_GATE", ghwaypoints.Waypoint(name="Hangar Door", plot_locked=True,
                                                                                desc="This is the door of the mecha hangar."))
        snow_drift = self.register_element("SNOW_DRIFT", ghwaypoints.Waypoint(name="Snowdrift",
                                                                              desc="The snow has blocked the entrance to the mecha hangar. You're going to have to take one of the backup mecha from the storage yard."))
        myroom2 = pbge.randmaps.rooms.NoWallRoom(15, 15)
        myroom3 = WinterMochaHangar(parent=myroom2, waypoints={"DOOR": hangar_gate, "DRIFT": snow_drift})
        myscenegen.contents.append(myroom2)

        fence_gate = self.register_element("FENCE_GATE", ghwaypoints.Waypoint(name="Storage Yard", plot_locked=True,
                                                                              desc="This is the gate of the mecha storage yard."))

        myroom4 = self.register_element("FENCE_GATE_ROOM",
                                        pbge.randmaps.rooms.OpenRoom(6, 5, anchor=pbge.randmaps.anchors.northwest,
                                                                      parent=myscenegen))
        myroom5 = WinterMochaFence(parent=myroom4, anchor=pbge.randmaps.anchors.west, border=0, waypoints={'DOOR': fence_gate})

        # I don't know why I added a broken shovel. Just thought it was funny.
        myroom6 = pbge.randmaps.rooms.NoWallRoom(3, 3, parent=myscenegen)
        if random.randint(1, 3) != 1:
            myroom6.contents.append(WinterMochaShovel(anchor=pbge.randmaps.anchors.middle))
        else:
            myroom6.contents.append(WinterMochaDome(anchor=pbge.randmaps.anchors.middle))

        sp = self.add_sub_plot(nart, "MOCHA_HYOLEE")
        self.elements["HYOLEE"] = sp.elements["HYOLEE"]
        sp = self.add_sub_plot(nart, "MOCHA_CARTER")
        self.elements["CARTER"] = sp.elements["CARTER"]

        #self.add_sub_plot(nart, "MOCHA_ONAWA")

        # Add the puzzle to get through the snowdrift.
        #
        # Bibliography for procedural puzzle generation:
        # Isaac Dart, Mark J. Nelson (2012). Smart terrain causality chains for adventure-game puzzle generation. In Proceedings of the IEEE Conference on Computational Intelligence and Games, pp. 328-334.
        # Clara Fernandez-Vara and Alec Thomson. 2012. Procedural Generation of Narrative Puzzles in Adventure Games: The Puzzle-Dice System. In Proceedings of the The third workshop on Procedural Content Generation in Games (PCG '12).
        self.add_sub_plot(nart, "MELT", PlotState(elements={"TARGET": snow_drift}).based_on(self))

        self.add_sub_plot(nart, "MOCHA_MISSION", PlotState(elements={"CITY": myscene}).based_on(self), ident="COMBAT")

        self.add_sub_plot(nart, "MOCHA_CHALET", ident="CHALET")

        self.did_opening_sequence = False
        self.got_vikki_history = False
        self.got_vikki_mission = False
        self.mission_started = False

        return True

    def SNOW_DRIFT_MELT(self, camp):
        scene = self.elements["LOCALE"]
        drift = self.elements["SNOW_DRIFT"]
        scene._map[drift.pos[0]][drift.pos[1]].wall = None
        scene._map[drift.pos[0] - 1][drift.pos[1]].wall = None
        scene._map[drift.pos[0] + 1][drift.pos[1]].wall = None

    def FENCE_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item('Board a mecha and start mission', self._give_bad_mecha)
        thingmenu.add_item("Don't start mission yet", None)

    def HANGAR_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item('Board a mecha and start mission', self._give_good_mecha)
        thingmenu.add_item("Don't start mission yet", None)

    def _give_bad_mecha(self, camp: gears.GearHeadCampaign):
        # Give the PC some cheapass mecha.
        mygearlist = [
            gears.selector.get_design_by_full_name("SAN-X9 Buru Buru"),
            gears.selector.get_design_by_full_name("SAN-X9c Urban Buru Buru"),
            gears.selector.get_design_by_full_name("ITM-01 Claymore"),
            gears.selector.get_design_by_full_name("A7800 Joust"),
            gears.selector.get_design_by_full_name("TR-93 XS Razer")
        ]
        mek1, mek2 = random.sample(mygearlist, 2)
        mek1.colors = gears.random_mecha_colors()
        mek2.colors = self.elements["VIKKI"].mecha_colors
        camp.party.append(mek1)
        camp.assign_pilot_to_mecha(camp.pc, mek1)
        if self.elements["VIKKI"] in camp.party:
            camp.party.append(mek2)
            camp.assign_pilot_to_mecha(self.elements["VIKKI"], mek2)

        camp.campdata[MOVAR_CHEAPMEKS] = True

        self._go_to_mission(camp)

    def _give_good_mecha(self, camp: gears.GearHeadCampaign):
        mek1 = gears.selector.get_design_by_full_name("Z45-60 Zerosaiko")
        mek2 = gears.selector.get_design_by_full_name("THD-35 Thorshammer")
        mek1.colors = gears.random_mecha_colors()
        mek2.colors = self.elements["VIKKI"].mecha_colors
        camp.party.append(mek1)
        camp.assign_pilot_to_mecha(camp.pc, mek1)
        if self.elements["VIKKI"] in camp.party:
            camp.party.append(mek2)
            camp.assign_pilot_to_mecha(self.elements["VIKKI"], mek2)

        self._go_to_mission(camp)

    def _go_to_mission(self, camp):
        self.mission_started = True
        self.subplots["COMBAT"].enter_combat(camp)

    def _get_dialogue_grammar(self, npc, camp):
        if npc is self.elements["VIKKI"]:
            # Return the IP_ grammar.
            mygram = dict()
            mygram["[IP_STATUS]"] = ["A lot has happened this year."]
            mygram["[IP_Business]"] = ["I'm working for the Defense Force nearly full time now",
                                       "I did a search and rescue mission near the Ziggurat a few weeks back"]
            mygram["[IP_Pleasure]"] = ["I've been helping to organize the first big tournament at Mauna Arena"]
            mygram["[IP_GoodNews]"] = ["I did some work on the old Thorshammer", "I've been promoted to captain"]
            mygram["[IP_BadNews]"] = ["I'm still heartbroken over losing my Ovaknight to Typhon"]
            mygram["[IP_Hope]"] = ["I hope Hyolee can figure out how to fight biomonsters before the next one shows up"]
            mygram["[IP_Worry]"] = ["I'm worried about what's going to happen between the Federation and Aegis next"]
            return mygram

    def VIKKI_offers(self, camp: gears.GearHeadCampaign):
        # Return list of dialogue offers.
        mylist = list()
        relationship = camp.get_relationship(self.elements["VIKKI"])

        if not self.mission_started:
            if camp.pc.has_badge(gears.oldghloader.TYPHON_SLAYER.name) or relationship.met_before:
                mylist.append(Offer(
                    "[LONGTIMENOSEE] It's me, Vikki Shingo, from Hogye. Did they pull you out of bed for this mission too?",
                    context=ContextTag([self]),
                    replies=[
                        Reply("What mission? What's going on?", destination=Cue(ContextTag([context.INFO, context.MISSION]))),
                        Reply("Vikki! How's life been treating you?",
                              destination=Cue(ContextTag([context.INFO, context.PERSONAL])))
                        ]))
            else:
                mylist.append(Offer(
                    "Good morning... I guess I'm not the only pilot they hauled out of bed for this mission. The name's Vikki Shingo; I think we met briefly yesterday.",
                    context=ContextTag([self]),
                    replies=[
                        Reply("What mission? What's going on?",
                              destination=Cue(ContextTag([context.INFO, context.MISSION])))
                    ]))

            if not self.got_vikki_mission:
                mylist.append(Offer(
                    "Some bandits are attacking a convoy down on the Gyori Highway. Because of the blizzard last night, the Guardians are tied up with disaster relief. Even worse, the hangar where my and probably your mecha are stored is snowed under.",
                    context=ContextTag([context.INFO, context.MISSION]), data={"subject": "the mission", },
                    replies=[
                        Reply("[DOTHEYHAVEITEM]",
                              destination=Offer(
                                  "Yeah, they do have snow clearing equipment... it's in the same hangar as our mecha. Not to worry, though- the junker meks we used in the charity game are in the storage yard, so we can use them.",
                                  context=ContextTag([context.MISSION, context.PROBLEM]),
                                  data={"item": "snow clearing equipment", })
                              ),
                        Reply("[IWILLDOMISSION]",
                              destination=Offer("[GOODLUCK] I'm going back to bed.",
                                                context=ContextTag([context.ACCEPT, context.MISSION]),
                                                data={"mission": "fight the bandits"})
                              ),
                    ], effect=self._get_vikki_mission, no_repeats=True
                    ))
            else:
                mylist.append(Offer(
                    "You should have had a cup of coffee. There are bandits on the Gyori Highway, you can get a mecha to use from the storage yard up north.",
                    context=ContextTag([context.INFO, context.MISSION]), data={'subject': 'the bandits'}, no_repeats=True))

            if not self.got_vikki_history:
                mylist.append(Offer("[INFO_PERSONAL]",
                                    context=ContextTag([context.INFO, context.PERSONAL]),
                                    data={'subject': 'the past six months'}, effect=self._ask_vikki_history,
                                    no_repeats=True))

            if self.elements["VIKKI"] not in camp.party:
                if camp.get_active_lancemates():
                    mylist.append(Offer("Nah, you look like you have this covered. I'm going back to bed.",
                                        context=ContextTag([context.JOIN])))
                else:
                    mylist.append(Offer("Alright, I'll go with you. Between the two of us this should be no problem.",
                                        context=ContextTag([context.JOIN]), effect=self._vikki_join))

        return mylist

    def _get_vikki_mission(self, camp):
        self.got_vikki_mission = True

    def _ask_vikki_history(self, camp):
        self.got_vikki_history = True

    def _vikki_join(self, camp):
        camp.party.append(self.elements["VIKKI"])
        camp.campdata[MOVAR_LANCEMATE] = "VIKKI"
        self.elements["VIKKI"].relationship.tags.add(gears.relationships.RT_LANCEMATE)

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.did_opening_sequence:
            pbge.alert("December 23, NT157. It's been an awful year for the Federated Territories of Earth.")
            if camp.pc.has_badge(gears.oldghloader.TYPHON_SLAYER.name):
                pbge.alert(
                    "An ancient bioweapon named Typhon was awakened from stasis and rampaged through several cities. Fortunately, a team of cavaliers was able to destroy it before it reached Snake Lake. You were there.")
                pbge.alert(
                    "Now, six months later, you are meeting with several of your former lancemates for a charity mecha tournament in the recently constructed Mauna Arena.")
            else:
                pbge.alert(
                    "An ancient bioweapon named Typhon was awakened from stasis and rampaged through several cities. You watched the destruction unfold on vidnet, and saw the final battle when a team of cavaliers brought the beast down just outside of Snake Lake City."
                )
                pbge.alert(
                    "Now, six months later, you have been invited to a charity mecha tournament at Mauna Arena. The funds raised will be donated to reconstruction efforts in Wujung."
                )
            pbge.alert("At 5AM, alarms go off through the hotel. You rush outside to see what's going on.")

            npc = self.elements["VIKKI"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=Cue(ContextTag([self])))

            # Also at this time: We need to lock away any spare mecha the PC might have, since this adventure
            # relies upon the PC not having access to said mecha. Don't worry; we'll give everything back at
            # the end.
            camp.campdata["PC_STUFF"] = list()
            for mek in list(camp.party):
                if not isinstance(mek, gears.base.Being):
                    camp.party.remove(mek)
                    camp.campdata["PC_STUFF"].append(mek)
                    if hasattr(mek, "pilot"):
                        mek.pilot = None
            self.did_opening_sequence = True

    def t_START(self, camp: gears.GearHeadCampaign):
        if gears.tags.SCENE_BUILDING not in camp.scene.attributes:
            pbge.my_state.view.postfx = SnowField()

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        # Winter Mocha is a simple scenario, so instead of using the EnterTownLanceRecovery from plotutility
        # we'll just deal with casualties manually.
        pc: gears.base.Character = camp.pc.get_root()
        if not pc.is_operational():
            while camp.incapacitated_party:
                lm = camp.incapacitated_party.pop()
                camp.party.append(lm)
            while camp.dead_party:
                lm = camp.dead_party.pop()
                camp.party.append(lm)
            for lm in camp.party:
                lm.restore_all()
            camp.check_trigger("MOCHADEFEAT")

    def t_MOCHAVICTORY(self, camp: gears.GearHeadCampaign):
        self.subplots["CHALET"].start_victory(camp)

    def t_MOCHADEFEAT(self, camp: gears.GearHeadCampaign):
        self.subplots["CHALET"].start_defeat(camp)


class WinterMochaChaletForEnding(Plot):
    LABEL = "MOCHA_CHALET"
    active = False
    scope = True

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = self.register_element("FOYER_TEAM", teams.Team(name="Civilian Team"))
        intscene = gears.GearHeadScene(
            50, 35, "Mauna Chalet", player_team=team1, civilian_team=team2,
            attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_MEETING),
            scale=gears.scale.HumanScale,
            exploration_music='Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg',
        )

        intscenegen = pbge.randmaps.PackedBuildingGenerator(
            intscene, gharchitecture.ResidentialBuilding(wall_terrain=ghterrain.WoodenWall)
        )
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE")

        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(width=random.randint(10,15),
                                                                                 height=random.randint(6,8),
                                                                                 anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.BreakRoomDecor()),
                                      dident="LOCALE")
        foyer.contents.append(team2)

        self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_introom")
        self.register_element("POSTER", ghwaypoints.MechaPoster(name="Poster", desc="A promotional poster for the charity mecha tournament.", plot_locked=True), dident="_introom")

        self.register_element("EXIT",
                              ghwaypoints.Exit(name="Exit", anchor=pbge.randmaps.anchors.south, plot_locked=True), dident="_introom")

        self.did_prep = False
        self.did_intro = False
        self.won_mission = True
        self.can_get_blitzen = False

        return True

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.did_intro:
            if self.won_mission:
                pbge.alert("You return to the Mauna Chalet Resort in victory. The sun is just beginning to rise as you reach the lounge.")
            else:
                pbge.alert("You return to the Mauna Chalet Resort cold, wet, and utterly defeated. The sun is just beginning to rise as you reach the lounge.")
            camp.dole_xp(300)
            self.can_get_blitzen = self.won_mission and (camp.campdata.get(MOVAR_CHEAPMEKS)
                                                         or not camp.campdata.get(MOVAR_LANCEMATE)) and camp.campdata.get(MOVAR_FOUGHTBLITZEN)
            self.did_intro = True

    def EXIT_menu(self, camp, thingmenu):
        thingmenu.desc = "Do you want to end the game or keep playing for a while more?"
        thingmenu.add_item('End the game', self._end_the_game)
        thingmenu.add_item('Stay here for a bit longer', None)

    def _end_the_game(self, camp: gears.GearHeadCampaign):
        for pc in camp.party:
            pc.restore_all()
        camp.eject()

    def start_victory(self, camp: gears.GearHeadCampaign):
        self._prepare_for_conclusion(camp)
        # In this case, the PC gets to keep the mecha ze piloted during the mission.
        # Give the PC back their original stuff.
        camp.party += camp.campdata["PC_STUFF"]
        self._go_to_chalet(camp)

    def start_defeat(self, camp):
        self._prepare_for_conclusion(camp)
        self.won_mission = False
        # Remove all the mecha from the party; the PC doesn't get to keep it.
        for npc in list(camp.party):
            if npc is not camp.pc:
                camp.party.remove(npc)
        # Give the PC back their original stuff.
        camp.party += camp.campdata["PC_STUFF"]
        self._go_to_chalet(camp)

    def _go_to_chalet(self, camp):
        self.activate(camp)
        camp.go(self.elements["ENTRANCE"])

    NPC_LIST = ("VIKKI","HYOLEE","CARTER")
    def _prepare_for_conclusion(self, camp):
        if not self.did_prep:
            myscene = self.elements["LOCALE"]
            # Move all the needed NPCs to the chalet. Make sure they're alright.
            for npcid in self.NPC_LIST:
                npc = self.elements[npcid]
                npc.restore_all()
                myscene.deploy_actor(npc)
            # Remove all the NPCs and their mecha from the party.
            for npc in list(camp.party):
                if isinstance(npc, gears.base.Being) and npc is not camp.pc:
                    camp.party.remove(npc)
                elif isinstance(npc, gears.base.Mecha):
                    if npc.pilot is not camp.pc:
                        camp.party.remove(npc)
                elif npc is not camp.pc:
                    camp.party.remove(npc)
            self.did_prep = True

    def _get_blitzen(self, camp):
        self.can_get_blitzen = False
        camp.party.append(gears.selector.get_design_by_full_name("WM Custom Blitzen"))

    def _refuse_blitzen(self, camp):
        self.can_get_blitzen = False

    def VIKKI_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if self.won_mission and camp.campdata.get(MOVAR_LANCEMATE) == "VIKKI":
            if self.can_get_blitzen:
                mylist.append(Offer(
                    "Hey, you know that weird reindeer mecha we fought out there? We got it as salvage! You can have it if you want.",
                    ContextTag((context.HELLO,)),
                ))
                mylist.append(Offer(
                    "I'm sure you will. Now to go drown my sorrows in coffee before the match I have at ten.",
                    ContextTag((context.CUSTOM,)), effect=self._get_blitzen, data={"reply": "Thanks, I'll put it to good use!"}
                ))
                mylist.append(Offer(
                    "Yeah, I don't really want it either... maybe Mecha Sporch in Hogye can use it as their new loaner mek.",
                    ContextTag((context.CUSTOM,)), effect=self._refuse_blitzen, data={"reply": "No thanks, you can keep it."}
                ))
            else:
                mylist.append(Offer(
                    "We were victorious! Good work, [audience]. I'd feel a lot better about this mission if I didn't have an arena match coming up at ten... time to see how much coffee I can drink before then.",
                    ContextTag((context.HELLO,)),
                ))
        else:
            mylist.append(Offer(
                "Welp, this was an exciting night for everyone. I'd go back to bed if I didn't have an arena match coming up in a couple of hours.",
                ContextTag((context.HELLO,)),
            ))

        return mylist

    def HYOLEE_offers(self, camp):
        mylist = list()
        if self.won_mission and self.can_get_blitzen and not camp.campdata.get(MOVAR_LANCEMATE):
            mylist.append(Offer(
                "Welcome back [audience]; I didn't want to go back to sleep until seeing you got back okay. I hear you picked up some good salvage out there!",
                ContextTag((context.HELLO,)),
            ))
            mylist.append(Offer(
                "(Hyolee shows you the CavNet app on her phone) See right here, it says you can claim this 'WM Custom Blitzen', whatever that is. Must be a new model.",
                ContextTag((context.CUSTOM,)), effect=self._get_blitzen, data={"reply": "What? I didn't hear about any salvage."}
            ))
        else:
            mylist.append(Offer(
                "I promised Vikki that I'd stay up for her next match, but I'm not sure that's going to happen... If I fall asleep right after the match starts then technically I've kept the promise.",
                ContextTag((context.HELLO,)),
            ))

        return mylist

    def CARTER_offers(self, camp):
        mylist = list()
        if self.won_mission and camp.campdata.get(MOVAR_LANCEMATE) == "CARTER":
            if self.can_get_blitzen:
                mylist.append(Offer(
                    "Hey [audience], we got some salvage from that mission- the Blitzen mecha their leader was riding. You want it?",
                    ContextTag((context.HELLO,)),
                ))
                mylist.append(Offer(
                    "It's definitely a unique mek, I'll give it that. I'm gonna go get cleaned up and then head the rest of the way to Gyori. I'll see you around sometime.",
                    ContextTag((context.CUSTOM,)), effect=self._get_blitzen, data={"reply": "Of course! That mek is awesome."}
                ))
                mylist.append(Offer(
                    "In that case I'll save it for some time when I need a backup mek. You can never have too many mecha, you know.",
                    ContextTag((context.CUSTOM,)), effect=self._refuse_blitzen, data={"reply": "Not really. You can keep it."}
                ))
            else:
                mylist.append(Offer(
                    "Nice going, [audience]. If I ever need backup for a tough convoy run I'll keep your name in mind.",
                    ContextTag((context.HELLO,)),
                ))
        else:
            mylist.append(Offer(
                "I'm gonna have a bit of a rest, and then I can finish bringing my convoy to Gyori when the roads get cleared. Good night... or morning, whatever time it is.",
                ContextTag((context.HELLO,)),
            ))

        return mylist


class WinterMochaOnawa(Plot):
    LABEL = "MOCHA_ONAWA"
    active = True
    scope = "LOCALE"

    did_greeting = False

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        hyolee = nart.camp.get_major_npc("Onawa GH1")
        hyolee.mmode = pbge.scenes.movement.Walking
        self.register_element("NPC", hyolee, dident="ROOM")
        self.asked_join = False
        return True

    def NPC_offers(self, camp):
        # Return list of dialogue offers.
        mylist = list()
        mylist.append(Offer("Centuries of technological development and nobody has found a better use for computers than turn based gaming. They have played us for fools...",
                            context=ContextTag([context.CUSTOM]), data={'reply': 'Say the line, please.'},
                            effect=None, no_repeats=True, dead_end=True))

        return mylist


class WinterMochaHyolee(Plot):
    LABEL = "MOCHA_HYOLEE"
    active = True
    scope = "LOCALE"

    did_greeting = False

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        hyolee = nart.camp.get_major_npc("Hyolee GH1")
        hyolee.mmode = pbge.scenes.movement.Walking
        self.register_element("HYOLEE", hyolee, dident="ROOM")
        self.asked_join = False
        return True

    def _get_dialogue_grammar(self, npc, camp):
        if npc is self.elements["HYOLEE"]:
            # Return the IP_ grammar.
            mygram = dict()
            mygram["[IP_STATUS]"] = ["It's been interesting."]
            mygram["[IP_Business]"] = [
                "they're upgrading the security at my lab, as if fifteen velociraptors isn't enough", ]
            mygram["[IP_Pleasure]"] = ["I came here with Vikki to cheer Team Hogye in the tournament"]
            mygram["[IP_GoodNews]"] = ["Calmegie Lab has been selected to analyze part of Typhon's corpse",
                                       "Fluffy has laid eggs"]
            # mygram["[IP_BadNews]"] = [""]
            mygram["[IP_Hope]"] = ["I hope I can get some new insights into the biology of synthetics"]
            # mygram["[IP_Worry]"] = [""]
            return mygram

    def _ask_to_join(self, camp):
        self.asked_join = True

    def HYOLEE_offers(self, camp):
        # Return list of dialogue offers.
        mylist = list()
        relationship = camp.get_relationship(self.elements["HYOLEE"])

        if not self.did_greeting:
            if relationship.met_before:
                mylist.append(Offer(
                    "Well, well, well, if it isn't [audience]. It's been a while. How have you been doing? I can't wait to catch up.",
                    context=ContextTag([context.HELLO,]), effect=self._do_greeting, allow_generics=False
                ))
            else:
                mylist.append(Offer(
                    "[HELLO] I came with Vikki to support Team Hogye, which is just Vikki, but she needs all the support she can get.",
                    context=ContextTag([context.HELLO,]), effect=self._do_greeting, allow_generics=False
                ))

        mylist.append(Offer("[INFO_PERSONAL]",
                            context=ContextTag([context.CUSTOM]), data={'reply': 'So what have you been doing lately?'},
                            effect=None, no_repeats=True))
        if not self.asked_join:
            mylist.append(Offer("[HAGOODONE] I tried piloting a mecha once, and that's quite enough for me.",
                                context=ContextTag([context.JOIN]), effect=self._ask_to_join))
        return mylist

    def _do_greeting(self, camp):
        self.did_greeting = True


class WinterMochaCarter(Plot):
    LABEL = "MOCHA_CARTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        carter = nart.camp.get_major_npc("Carter GH1")
        self.register_element("CARTER", carter, dident="FENCE_GATE_ROOM")
        return True

    def _get_dialogue_grammar(self, npc, camp):
        if npc is self.elements["CARTER"]:
            # Return the IP_ grammar.
            mygram = dict()
            mygram["[IP_Business]"] = ["my convoy got in from Wujung just before they closed the highway"]
            # mygram["[IP_Pleasure]"] = [""]
            # mygram["[IP_GoodNews]"] = [""]
            mygram["[IP_BadNews]"] = ["I won't be getting to Gyori tonight"]
            mygram["[IP_Hope]"] = ["I'm thinking of joining the tournament next time they hold one of these things"]
            mygram["[IP_Worry]"] = ["this storm is bad news- there's something out there"]
            return mygram

    def _carter_join(self, camp: gears.GearHeadCampaign):
        camp.party.append(self.elements["CARTER"])
        mek1 = gears.selector.get_design_by_full_name("SDH-22 Corsair")
        camp.party.append(mek1)
        camp.assign_pilot_to_mecha(self.elements["CARTER"], mek1)
        mek1.colors = self.elements["CARTER"].mecha_colors
        self.elements["CARTER"].relationship.tags.add(gears.relationships.RT_LANCEMATE)
        camp.campdata[MOVAR_LANCEMATE] = "CARTER"

    def CARTER_offers(self, camp):
        # Return list of dialogue offers.
        mylist = list()
        mylist.append(Offer("[INFO_PERSONAL]",
                            context=ContextTag([context.INFO, context.PERSONAL]), data={'subject': 'tonight'},
                            effect=None, no_repeats=True))
        if self.elements["CARTER"] not in camp.party:
            if camp.get_active_lancemates():
                mylist.append(Offer("No thanks, I've been mucking through this pea soup enough for one night.",
                                    context=ContextTag([context.JOIN])))
            else:
                mylist.append(Offer(
                    "Okay, I can do that. My corsair's right here in the storage yard. If we need any repairs during the mission, I'm half decent at that.",
                    context=ContextTag([context.JOIN]), effect=self._carter_join))

        return mylist


# Mocha Mission Construction.
#
# The Mocha mission is going to use a miniature version of the GH1 core story
# generator plus a branching conclusion. One of the brilliant things about
# defining content in Python is that I don't need to hardcode the story
# generator; instead, the plots involved can define their own rules. Yay!
#
# Here's how the story generator works. There are at least three story state
# variables- in this case they will be Enemy, Complication, and Stakes.
# Each story
# component is keyed to two of the state variables and alters one of them.
# If 4 variables each have ten possible states, that means there are 10000
# possible story states but only 400 story components are needed to ensure
# four possible outcomes for each state.
#
# In practice, far fewer components should be needed since not every state
# will be reachable and each state really only needs one possible outcome.
# Plus, many components will have broad requirements- instead of only applying
# to a single two-variable state, it may apply to multiple states involving
# those two variables.
#


class WinterHighwaySceneGen(pbge.randmaps.SceneGenerator):
    DO_DIRECT_CONNECTIONS = True

    def connect_contents(self, gb, archi):
        # Generate list of rooms.
        unconnected = [r for r in self.contents if hasattr(r, "area")]
        random.shuffle(unconnected)
        connected = list()
        connected.append(unconnected.pop())
        unconnected.sort(key=lambda r: gb.distance(r.area.center, connected[0].area.center))

        room = connected[0]
        if room.anchor:
            mydest = pygame.Rect(0, 0, 3, 3)
            room.anchor(self.area, mydest)
            self.draw_direct_connection(gb, room.area.centerx, room.area.centery, mydest.centerx, mydest.centery, archi)

        # Process them
        for room in list(unconnected):
            unconnected.remove(room)
            dest = min(connected, key=lambda r: gb.distance(r.area.center, room.area.center))
            self.draw_direct_connection(gb, room.area.centerx, room.area.centery, dest.area.centerx, dest.area.centery,
                                        archi)
            connected.append(room)
            if room.anchor:
                mydest = pygame.Rect(0, 0, 3, 3)
                room.anchor(self.area, mydest)
                self.draw_direct_connection(gb, room.area.centerx, room.area.centery, mydest.centerx, mydest.centery,
                                            archi)

    def draw_direct_connection(self, gb, x1, y1, x2, y2, archi):
        path = pbge.scenes.animobs.get_line(x1, y1, x2, y2)
        for p in path:
            gb.fill(pygame.Rect(p[0] - 1, p[1] - 1, 3, 3), floor=WinterMochaPavement, wall=None)


class MochaMissionBattleBuilder(Plot):
    # Go fight mecha near Mauna.
    LABEL = "MOCHA_MISSION"
    active = True
    scope = True

    def custom_init(self, nart):
        """The mission leadup will be two highway scenes with an intro, two
           encounters, a recharge, and two choices at the end. The choices
           will handle their own scenes."""
        team1 = teams.Team(name="Player Team")
        myscene1 = gears.GearHeadScene(30, 60, "Near Mauna", player_team=team1, scale=gears.scale.MechaScale)

        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow, myfilter, mutate=mymutate)
        myscenegen1 = WinterHighwaySceneGen(myscene1, myarchi)

        myscene2 = gears.GearHeadScene(30, 60, "Gyori Highway", player_team=team1, scale=gears.scale.MechaScale)
        myscenegen2 = WinterHighwaySceneGen(myscene2, myarchi)

        self.register_scene(nart, myscene1, myscenegen1, ident="FIRST_PART")
        self.register_scene(nart, myscene2, myscenegen2, ident="SECOND_PART")

        myscene1.exploration_music = 'Lines.ogg'
        myscene1.combat_music = 'Late.ogg'
        myscene2.exploration_music = 'Lines.ogg'
        myscene2.combat_music = 'Late.ogg'

        myroom = self.register_element("FIRST_ENTRANCE_ROOM", pbge.randmaps.rooms.NoWallRoom(5, 5, parent=myscene1,
                                                                                            anchor=pbge.randmaps.anchors.south))
        myent = self.register_element("FIRST_ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)

        myroom2 = pbge.randmaps.rooms.NoWallRoom(5, 5, parent=myscene2, anchor=pbge.randmaps.anchors.south)
        myent2 = self.register_element("SECOND_ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom2.contents.append(myent2)

        mygoal = pbge.randmaps.rooms.NoWallRoom(5, 5, parent=myscene1, anchor=pbge.randmaps.anchors.north)
        myexit = ghwaypoints.Exit(dest_wp=myent2, name="Continue Onward", anchor=pbge.randmaps.anchors.north)
        mygoal.contents.append(myexit)

        # Create a boss mecha, but don't place it yet. It may be claimed by one
        # of the subplots.
        boss_mecha = self.register_element("BOSS", gears.selector.get_design_by_full_name("WM Custom Blitzen"))
        boss_pilot = self.register_element("BOSS_PILOT", gears.selector.random_pilot(50))
        boss_mecha.load_pilot(boss_pilot)
        # Also set the enemy team color.
        self.register_element("ENEMY_FACTION", UnkEneFaction)

        sp = self.add_sub_plot(nart, "MOCHA_MINTRO",
                               PlotState(elements={"LOCALE": myscene1, "LOCALE2": myscene2}).based_on(self))

        # Try to load a debugging encounter.
        self.add_sub_plot(nart, "MOCHA_DEBUGENCOUNTER", PlotState(elements={"LOCALE": myscene1}).based_on(self),
                          necessary=False)
        self.add_sub_plot(nart, "MOCHA_FB_DEBUGSTUB", PlotState(elements={"LOCALE": myscene1}).based_on(self),
                          necessary=False)

        return True

    def enter_combat(self, camp):
        camp.go(self.elements["FIRST_ENTRANCE"])



#  **************************************
#  ***   Random  Story  Descriptors   ***
#  **************************************

ENEMY = 'MENCOUNTER_ENEMY'
NO_ENEMY, BANDITS, MERCENARY, PIRATES, AEGIS = list(range(5))
ENEMY_NOUN = ('the raiders', 'the bandits', 'the raiders', 'the pirates', 'Aegis Overlord')

COMPLICATION = 'MENCOUNTER_COMPLICATION'
NO_COMPLICATION, CONTRABAND_CARGO, FERAL_SYNTHS, PROFESSIONAL_OPERATION, AEGIS_SCOUTS = list(range(5))

STAKES = 'MENCOUNTER_STAKES'
NO_STAKES, STOLEN_TOYS, GET_THE_LEADER, PROTOTYPE_MECHA = list(range(4))


class MercFaction(gears.factions.Faction):
    mecha_colors = gears.random_mecha_colors()


class ConvoyFaction(gears.factions.Faction):
    mecha_colors = (color.Jade, color.CeramicColor, color.FlourescentGreen, color.Black, color.MassiveGreen)


class UnkEneFaction(gears.factions.Faction):
    mecha_colors = (color.CometRed, color.DimGrey, color.GreenYellow, color.Black, color.BlackRose)


#  ******************
#  ***   Intros   ***
#  ******************

class Intro_GetTheLeader(Plot):
    LABEL = "MOCHA_MINTRO"
    active = True
    scope = "LOCALE"
    # Info for the plot checker...
    CHANGES = {STAKES: GET_THE_LEADER, ENEMY: BANDITS}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(ENEMY, BANDITS)
        self.register_element(STAKES, GET_THE_LEADER)
        self.register_element("ENEMY_FACTION", gears.factions.BoneDevils)
        self.did_intro = False
        self.add_sub_plot(nart, "MOCHA_MENCOUNTER", PlotState(elements={"ENCOUNTER_NUMBER": 1}).based_on(self))
        return True

    def t_START(self, camp):
        if not self.did_intro:
            mycutscene = pbge.cutscene.Cutscene(library={'pc': camp.pc},
                                                beats=(
                                                    pbge.cutscene.Beat(pbge.cutscene.AlertDisplay(
                                                        "According to the mission offer you received, you just need to defeat the boss of the bandits.")),
                                                    pbge.cutscene.Beat(game.content.ghcutscene.MonologueDisplay(
                                                        "According to the mission offer, all we have to do is catch the boss of the bandits.",
                                                        'npc'), prep=game.content.ghcutscene.LancematePrep('npc')),
                                                    pbge.cutscene.Beat(game.content.ghcutscene.MonologueDisplay(
                                                        "I've heard about this bandit we're going up against, {0}. If we can defeat him then his troops should scatter.".format(
                                                            self.elements["BOSS_PILOT"]), 'npc'),
                                                                       prep=game.content.ghcutscene.LancematePrep(
                                                                           'npc')),
                                                )
                                                )
            mycutscene(camp)
            self.did_intro = True


class Intro_ToyBandits(Plot):
    LABEL = "MOCHA_MINTRO"
    active = True
    scope = "LOCALE"
    # Info for the plot checker...
    CHANGES = {STAKES: STOLEN_TOYS}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(STAKES, STOLEN_TOYS)
        self.register_element("_TRUCK", WinterMochaTruck(desc="A ransacked toy delivery truck."),
                              dident="FIRST_ENTRANCE_ROOM")
        self.did_intro = False
        self.add_sub_plot(nart, "MOCHA_MENCOUNTER", PlotState(elements={"ENCOUNTER_NUMBER": 1}).based_on(self))
        return True

    def t_START(self, camp):
        if not self.did_intro:
            mycutscene = pbge.cutscene.Cutscene(library={'pc': camp.pc},
                                                beats=(
                                                    pbge.cutscene.Beat(pbge.cutscene.AlertDisplay(
                                                        "You come across one of the trucks from the convoy that was attacked. Its cargo of toys, bound for the orphanage in Wujung, has been stolen."),
                                                                       children=[
                                                                           pbge.cutscene.Beat(
                                                                               game.content.ghcutscene.MonologueDisplay(
                                                                                   "What kind of meanie would steal a truckload of orphan's toys, and right before the solstice to boot?",
                                                                                   'npc'),
                                                                               prep=game.content.ghcutscene.LancematePrep(
                                                                                   'npc', personality_traits=(
                                                                                   personality.Cheerful,), )),
                                                                           pbge.cutscene.Beat(
                                                                               game.content.ghcutscene.MonologueDisplay(
                                                                                   "This is worse than a crime, it's a travesty! The villains who stole these toys must be brought to justice.",
                                                                                   'npc'),
                                                                               prep=game.content.ghcutscene.LancematePrep(
                                                                                   'npc', personality_traits=(
                                                                                   personality.Justice,), )),
                                                                           pbge.cutscene.Beat(
                                                                               game.content.ghcutscene.MonologueDisplay(
                                                                                   "Toy thieves, huh? Let's catch them so I can go back to bed.",
                                                                                   'npc'),
                                                                               prep=game.content.ghcutscene.LancematePrep(
                                                                                   'npc', personality_traits=(
                                                                                   personality.Shy,), )),
                                                                           pbge.cutscene.Beat(
                                                                               game.content.ghcutscene.MonologueDisplay(
                                                                                   "Who steals a truckload of toys in the middle of a blizzard? Do you think they planned this heist or were they expecting something else?",
                                                                                   'npc'),
                                                                               prep=game.content.ghcutscene.LancematePrep(
                                                                                   'npc', personality_traits=(
                                                                                   personality.Easygoing,), )),
                                                                       ], ),
                                                )
                                                )
            mycutscene(camp)
            self.did_intro = True


class Intro_MysteriousMecha(Plot):
    LABEL = "MOCHA_MINTRO"
    active = True
    scope = "LOCALE"
    # Info for the plot checker...
    CHANGES = {COMPLICATION: AEGIS_SCOUTS, }

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(STAKES, STOLEN_TOYS)
        self.did_intro = False
        self.add_sub_plot(nart, "MOCHA_MENCOUNTER", PlotState(elements={"ENCOUNTER_NUMBER": 1}).based_on(self))
        return True

    def t_START(self, camp):
        if not self.did_intro:
            mycutscene = pbge.cutscene.Cutscene(
                library={'pc': camp.pc},
                beats=(
                    pbge.cutscene.Beat(pbge.cutscene.AlertDisplay(
                        "You find the tracks in the snow where the bandits met the convoy. However, there is a second set of tracks just off the road, following the others at a distance."),
                        children=[
                            pbge.cutscene.Beat(
                                game.content.ghcutscene.MonologueDisplay(
                                    "I recognize these tread marks from the battle of Snake Lake... Those are Aegis mecha. This mission just got a whole lot more serious.",
                                    'npc'),
                                prep=game.content.ghcutscene.LancematePrep(
                                    'npc', personality_traits=(
                                        personality.Grim,), )),
                            pbge.cutscene.Beat(
                                game.content.ghcutscene.MonologueDisplay(
                                    "These tracks belong to a Chameleon; that's an Aegis mecha. We better be careful from here on out.",
                                    'npc'),
                                prep=game.content.ghcutscene.LancematePrep(
                                    'npc', stats=(stats.Scouting,), )),
                            pbge.cutscene.Beat(
                                pbge.cutscene.AlertDisplay(
                                    "You recognize the third set of tracks as belonging to an Aegis patrol. Looks like you'll have more than bandits to worry about.")),
                            pbge.cutscene.Beat(
                                game.content.ghcutscene.MonologueDisplay(
                                    "These tire marks don't belong to any bandit; they're Aegis mecha! I'd stake my reputation on that.",
                                    'npc'),
                                prep=game.content.ghcutscene.LancematePrep(
                                    'npc', stats=(stats.Repair,), )),

                        ], ),
                )
            )
            mycutscene(camp)
            self.did_intro = True


#  **********************
#  ***   Encounters   ***
#  **********************

class Encounter_StealthTest(Plot):
    # This will be the prototype for all MOCHA_MENCOUNTER
    LABEL = "zMOCHA_DEBUGENCOUNTER"
    active = True
    scope = "LOCALE"
    # Info for the matches method and the plot checker...
    REQUIRES = {ENEMY: NO_ENEMY, COMPLICATION: NO_COMPLICATION}
    CHANGES = {ENEMY: BANDITS}

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        # Note that the lack of an ENCOUNTER_NUMBER implies that this
        # plot is being loaded as a debug encounter.
        return "ENCOUNTER_NUMBER" not in pstate.elements or all(
            pstate.elements.get(k, 0) == self.REQUIRES[k] for k in self.REQUIRES.keys())

    def load_next(self, nart):
        self.elements.update(self.CHANGES)
        enc_num = self.elements.get("ENCOUNTER_NUMBER", 0)
        if enc_num == 1:
            # Load the second encounter.
            self.add_sub_plot(nart, "MOCHA_MENCOUNTER",
                              PlotState(elements={"LOCALE": self.elements["LOCALE2"], "ENCOUNTER_NUMBER": 2}).based_on(
                                  self))
        elif enc_num == 2:
            mc = self.add_sub_plot(nart, "MOCHA_MHOICE",
                                   PlotState(elements={"MHOICE_ANCHOR": pbge.randmaps.anchors.west}).based_on(self))
            self.add_sub_plot(nart, "MOCHA_MHOICE",
                              PlotState(elements={"MHOICE_ANCHOR": pbge.randmaps.anchors.east}).based_on(mc))

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(10, 16, anchor=pbge.randmaps.anchors.southeast),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        self.register_element("ENEMY_FACTION", gears.factions.BoneDevils)
        meks = gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"], myscene.environment).mecha_list
        for m in meks:
            p = m.get_pilot()
            p.statline[stats.Stealth] = 5
        team2.contents += meks
        self.load_next(nart)
        return True


class Encounter_BasicBandits(Plot):
    # This will be the prototype for all MOCHA_MENCOUNTER
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    # Info for the matches method and the plot checker...
    REQUIRES = {ENEMY: NO_ENEMY, COMPLICATION: NO_COMPLICATION}
    CHANGES = {ENEMY: BANDITS}

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        # Note that the lack of an ENCOUNTER_NUMBER implies that this
        # plot is being loaded as a debug encounter.
        return "ENCOUNTER_NUMBER" not in pstate.elements or all(
            pstate.elements.get(k, 0) == self.REQUIRES[k] for k in self.REQUIRES.keys())

    def load_next(self, nart):
        self.elements.update(self.CHANGES)
        enc_num = self.elements.get("ENCOUNTER_NUMBER", 0)
        if enc_num == 1:
            # Load the second encounter.
            self.add_sub_plot(nart, "MOCHA_MENCOUNTER",
                              PlotState(elements={"LOCALE": self.elements["LOCALE2"], "ENCOUNTER_NUMBER": 2}).based_on(
                                  self))
        elif enc_num == 2:
            mc = self.add_sub_plot(nart, "MOCHA_MHOICE",
                                   PlotState(elements={"MHOICE_ANCHOR": pbge.randmaps.anchors.west}).based_on(self))
            self.add_sub_plot(nart, "MOCHA_MHOICE",
                              PlotState(elements={"MHOICE_ANCHOR": pbge.randmaps.anchors.east}).based_on(mc))

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(10, 16, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        self.register_element("ENEMY_FACTION", gears.factions.BoneDevils)
        meks = gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"], myscene.environment).mecha_list
        team2.contents += meks
        self.load_next(nart)
        return True


class Encounter_SilentMercenaries(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: NO_ENEMY, COMPLICATION: FERAL_SYNTHS}
    CHANGES = {ENEMY: MERCENARY}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        self.register_element("ENEMY_FACTION", MercFaction)
        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list
        self.load_next(nart)
        return True


class Encounter_InstantKarma(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {STAKES: STOLEN_TOYS, COMPLICATION: NO_COMPLICATION}
    CHANGES = {COMPLICATION: FERAL_SYNTHS}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(10, 16, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        myroom.contents.append(WinterMochaClaymore())
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        meks = gears.selector.RandomMonsterUnit(25, 50, myscene.environment, ("SYNTH", "HUNTER-X"), myscene.scale)
        team2.contents += meks.contents
        self.combat_entered = False
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True
            mycutscene = pbge.cutscene.Cutscene(library={'pc': camp.pc},
                                                beats=(
                                                    pbge.cutscene.Beat(game.content.ghcutscene.MonologueDisplay(
                                                        "Ashes... it's hunter synths! {} must have wandered into a nest of them. Serves them right for stealing toys from orphans.".format(
                                                            ENEMY_NOUN[self.elements.get(ENEMY, 0)]), 'npc'),
                                                                       prep=game.content.ghcutscene.LancematePrep(
                                                                           'npc')),
                                                )
                                                )
            mycutscene(camp)
            self.combat_entered = False


class Encounter_WeBroughtThisFightHere(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: PIRATES, COMPLICATION: NO_COMPLICATION}
    CHANGES = {COMPLICATION: AEGIS_SCOUTS}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("_ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list

        team3 = self.register_element("_AEGISTEAM", teams.Team(enemies=(myscene.player_team, team2)), dident="_room")
        team3.contents += gears.selector.RandomMechaUnit(25, 50, gears.factions.AegisOverlord,
                                                         myscene.environment).mecha_list
        bossmek = random.choice(team3.contents)
        self.register_element("_MIDBOSS", bossmek.get_pilot())

        self.intro_ready = True
        self.load_next(nart)
        return True

    def _ETEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            oteam = self.elements["_AEGISTEAM"]
            for npc in oteam.get_members_in_play(camp):
                if npc not in camp.fight.active:
                    camp.fight.active.append(npc)
            camp.fight.roll_initiative()
            self.do_intro(camp)

    def _AEGISTEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            oteam = self.elements["_ETEAM"]
            for npc in oteam.get_members_in_play(camp):
                if npc not in camp.fight.active:
                    camp.fight.active.append(npc)
            camp.fight.roll_initiative()
            self.do_intro(camp)

    def do_intro(self, camp):
        npc = self.elements["_MIDBOSS"]
        ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
        self.intro_ready = False

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer("Leave this place, Terran. This business is between Aegis Overlord Luna and these pirates.",
                            context=ContextTag([context.ATTACK, ]),
                            replies=[
                                Reply("Your presence makes it my business.",
                                      destination=Cue(ContextTag([context.CHALLENGE])),
                                      ), ], ))
        return mylist


class Encounter_TheDreadPirateOtaku(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: PIRATES, STAKES: STOLEN_TOYS}
    CHANGES = {STAKES: GET_THE_LEADER}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list
        bossmek = random.choice(team2.contents)
        self.register_element("_MIDBOSS", bossmek.get_pilot())

        self.intro_ready = True
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_MIDBOSS"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "Arr, I heard that someone was out here getting in our way. You don't seem to realize that you're messing with the crew of the dread captain {}!".format(
                str(self.elements["BOSS_PILOT"])),
            context=ContextTag([context.ATTACK, ]),
            replies=[
                Reply("Who is {}?".format(str(self.elements["BOSS_PILOT"])),
                      destination=Cue(ContextTag([context.COMBAT_INFO])),
                      ), ], ))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ]), ))
        mylist.append(Offer(
            "A fabulous collector of priceless treasures from across the solar system, and the deadliest captain who's ever paid my salary... [LETSFIGHT]",
            context=ContextTag([context.COMBAT_INFO, ]), data={"subject": "the toys"}))
        return mylist


class Encounter_MyLittleCabbageFunkoBeaniePogs(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: NO_ENEMY, STAKES: STOLEN_TOYS}
    CHANGES = {ENEMY: PIRATES}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        self.register_element("ENEMY_FACTION", gears.factions.BladesOfCrihna)
        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list
        bossmek = max(team2.contents, key=lambda m: m.cost)
        self.register_element("_MIDBOSS", bossmek.get_pilot())
        self.intro_ready = True
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_MIDBOSS"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "Greetings, prisoners of gravity! This is [speaker] of the Blades of Crihna. We're just having a short plunder trip on your world. [LETSFIGHT]",
            context=ContextTag([context.ATTACK, ]),
            replies=[
                Reply("Why are you stealing toys, though?",
                      destination=Cue(ContextTag([context.COMBAT_INFO])),
                      ), ], ))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ]), ))
        mylist.append(Offer(
            "Are you serious? That truck was loaded with fresh first edition NerpsEpic figurines. You can sell those for a fortune in Emerald Spinner.",
            context=ContextTag([context.COMBAT_INFO, ]), data={"subject": "the toys"}))
        return mylist


class Encounter_FunnyLookingPrize(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {COMPLICATION: PROFESSIONAL_OPERATION, STAKES: GET_THE_LEADER}
    CHANGES = {STAKES: PROTOTYPE_MECHA}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")

        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list
        bossmek = max(team2.contents, key=lambda m: m.cost)
        self.register_element("_MIDBOSS", bossmek.get_pilot())

        self.register_element("_TRUCK", WinterMochaTruck(
            desc="A mecha transport vehicle. The mecha it was transporting is gone."), dident="_room")
        self.intro_ready = True
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_MIDBOSS"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "You're too late, cavaliers. Our leader {} has already escaped with the prototype mecha. [LETSFIGHT]".format(
                str(self.elements["BOSS_PILOT"])),
            context=ContextTag([context.ATTACK, ]), ))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ]), ))
        mylist.append(Offer(
            "It's called the Blitzen. Frankly speaking it looks ridiculous, but the boss seems to think it's worth this trouble.",
            context=ContextTag([context.COMBAT_INFO, ]), data={"subject": "the prototype"}))
        return mylist


class Encounter_LastBanditStanding(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: BANDITS, COMPLICATION: CONTRABAND_CARGO}
    CHANGES = {COMPLICATION: AEGIS_SCOUTS}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        meks = (
            gears.selector.get_design_by_full_name("SAN-X9 Buru Buru"),
            gears.selector.get_design_by_full_name("SAN-X9c Urban Buru Buru"),
            gears.selector.get_design_by_full_name("ITM-01 Claymore"),
        )
        mek1 = random.choice(meks)
        mek1.colors = self.elements["ENEMY_FACTION"].mecha_colors
        mypilot = self.register_element("_MIDBOSS", gears.selector.random_pilot(15))
        mek1.load_pilot(mypilot)
        team2.contents.append(mek1)

        self.intro_ready = True
        self.combat_entered = False
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True
            npc = self.elements["_MIDBOSS"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)

    def _run_away(self, camp):
        # The bandits will run away.
        pbge.alert("{} withdraws.".format(str(self.elements["_MIDBOSS"])))
        self.elements["ETEAM"].retreat(camp)
        self.t_ENDCOMBAT(camp)

    def t_ENDCOMBAT(self, camp):
        if self.combat_entered and self.intro_ready and camp.first_active_pc():
            self.intro_ready = False
            myscene = self.elements["LOCALE"]
            pos = self.elements["_room"].area.center
            meks = gears.selector.RandomMechaUnit(25, 50, gears.factions.AegisOverlord, myscene.environment).mecha_list
            for mek in meks:
                myscene.place_actor(mek, pos[0], pos[1], self.elements["ETEAM"])
            pbge.alert("Suddenly, a group of Aegis mecha emerge from the forest.")

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "Am I ever glad to see you... I was out here with my gang, hard at work y'know, when out of the corner of my eye I notice we're being trailed by these Aegis mecha. They opened fire and I got separated from the group but I know those moon-men are up to something.",
            context=ContextTag([context.ATTACK, ]),
            replies=[
                Reply("You must be one of the bandits we're looking for.",
                      destination=Cue(ContextTag([context.CHALLENGE])),
                      ), ], ))
        mylist.append(Offer(
            "Yeah, so what? You really want to pester a nobody like me when this could be the start of a Lunar invasion? Alright, then. [THREATEN]",
            context=ContextTag([context.CHALLENGE, ]), ))
        mylist.append(Offer("Really? Thanks! Watch out for those Aegis creeps...",
                            context=ContextTag([context.MERCY, ]), effect=self._run_away))
        return mylist


class Encounter_MovingOnUp(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: BANDITS, STAKES: PROTOTYPE_MECHA}
    CHANGES = {ENEMY: PIRATES}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        self.register_element("ENEMY_FACTION", gears.factions.BladesOfCrihna)
        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list
        bossmek = max(team2.contents, key=lambda m: m.cost)
        self.register_element("_MIDBOSS", bossmek.get_pilot())
        bossmek.colors = gears.factions.BladesOfCrihna.mecha_colors
        self.register_element("ENEMY_FACTION", gears.factions.BladesOfCrihna)
        self.intro_ready = True
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_MIDBOSS"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "This lot has done mighty nice, mighty nice indeed. We said if they could get us that Blitzen mecha we'd let them join the Blades. And now here you are, so we can seal the deal with a good old fashioned fight.",
            context=ContextTag([context.ATTACK, ]), ))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ]), ))
        mylist.append(Offer(
            "You don't know about the Blades?! The Blades of Crihna? We're only the biggest and most powerful pirate fleet in all of space! [LETSFIGHT]",
            context=ContextTag([context.COMBAT_INFO, ]), data={"subject": "the Blades"}))
        return mylist


class Encounter_TheEnemyOfMyEnemy(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: BANDITS, COMPLICATION: NO_COMPLICATION}
    CHANGES = {COMPLICATION: CONTRABAND_CARGO}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        meks = [
            gears.selector.get_design_by_full_name("SAN-X9 Buru Buru"),
            gears.selector.get_design_by_full_name("SAN-X9c Urban Buru Buru"),
            gears.selector.get_design_by_full_name("ITM-01 Claymore"),
        ]
        random.shuffle(meks)
        # Mek1 gets deployed right away, with the standard enemy colors.
        mek1 = meks.pop()
        mek1.colors = self.elements["ENEMY_FACTION"].mecha_colors
        mek1.load_pilot(gears.selector.random_pilot(25))
        team2.contents.append(mek1)

        # Mek2 gets held behind until the first fight is over.
        mek2 = self.register_element("_MIDMEK", meks.pop())
        mek2.colors = ConvoyFaction.mecha_colors
        mypilot = self.register_element("_MIDBOSS", gears.selector.random_pilot(35))
        mek2.load_pilot(mypilot)

        self.register_element("_TRUCK", WinterMochaTruck(plot_locked=True), dident="_room")

        self.intro_ready = True
        self.combat_entered = False
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        if self.combat_entered and self.intro_ready and camp.first_active_pc():
            self.intro_ready = False
            myscene = self.elements["LOCALE"]
            boss = self.elements["_MIDMEK"]
            pos = self.elements["_room"].area.center
            myscene.place_actor(boss, pos[0], pos[1], self.elements["ETEAM"])
            pbge.alert("As you finish fighting the bandit, one of the convoy guards emerges from the woods.")
            npc = self.elements["_MIDBOSS"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "Normally I'd thank you for defeating one of the bandits who attacked our convoy, but given the cargo we're hauling I don't think I should risk leaving any witnesses.",
            context=ContextTag([context.ATTACK, ]), ))
        mylist.append(Offer("Oh, so you didn't even take a peek inside the truck? No matter. [LETSFIGHT]",
                            context=ContextTag([context.COMBAT_INFO, ]), data={"subject": "the cargo"}))
        return mylist

    def _TRUCK_menu(self, camp, thingmenu):
        thingmenu.desc = "This is one of the trucks from the convoy that was attacked. Inside, you see a number of biotank storage units. No idea what they're transporting but it can't be good news."
        thingmenu.add_item('[Continue]', None)


class Encounter_AdvancedMecha(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {STAKES: PROTOTYPE_MECHA, COMPLICATION: NO_COMPLICATION}
    CHANGES = {COMPLICATION: PROFESSIONAL_OPERATION}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(10, 16, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        meks = (
            gears.selector.get_design_by_full_name("SAN-D1 Daum"),
            gears.selector.get_design_by_full_name("CHA-02b Sniper Chameleon"),
            gears.selector.get_design_by_full_name("TD-4B Musketeer"),
        )
        mymecha = random.choice(meks)
        mymecha.colors = self.elements["ENEMY_FACTION"].mecha_colors
        mymecha.load_pilot(gears.selector.random_pilot(25))
        team2.contents.append(mymecha)
        self.combat_entered = False
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        if self.combat_entered and camp.first_active_pc():
            mycutscene = pbge.cutscene.Cutscene(library={'pc': camp.pc},
                                                beats=(
                                                    pbge.cutscene.Beat(game.content.ghcutscene.MonologueDisplay(
                                                        "That was some high end equipment for a bandit... Better not underestimate this gang.",
                                                        'npc'), prep=game.content.ghcutscene.LancematePrep('npc')),
                                                )
                                                )
            mycutscene(camp)
            self.combat_entered = False


class Encounter_WeHaveBlitzen(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: BANDITS, STAKES: GET_THE_LEADER}
    CHANGES = {STAKES: PROTOTYPE_MECHA}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list
        bossmek = max(team2.contents, key=lambda m: m.cost)
        self.register_element("_MIDBOSS", bossmek.get_pilot())

        self.intro_ready = True
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_MIDBOSS"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _run_away(self, camp):
        # The bandits will run away.
        pbge.alert("The bandits withdraw.")
        for npc in list(camp.scene.contents):
            if camp.scene.local_teams.get(npc, None) == self.elements["ETEAM"]:
                camp.scene.contents.remove(npc)

    def _MIDBOSS_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "Halt! With the Blitzen mecha that our boss {} stole, the Bone Devil Gang will be unbeatable! [LETSFIGHT]".format(
                str(self.elements["BOSS_PILOT"])),
            context=ContextTag([context.ATTACK, ]), ))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ]), ))
        ci = Offer(
            "The Blitzen is a one of a kind, bleeding edge combat battroid. It's got a laser cannon and swarm missiles and power antlers!",
            context=ContextTag([context.COMBAT_INFO, ]), data={"subject": "Blitzen"})
        if camp.get_party_skill(stats.Charm, stats.Negotiation) >= 50:
            ci.replies.append(Reply("I see that the Blitzen isn't here.",
                                    destination=Offer(
                                        "Uh, yeah... but if it was here, we'd definitely [threat]! We'll just go away now, let you get back to work.",
                                        effect=self._run_away, context=ContextTag([context.RETREAT, ]))
                                    )
                              )
        mylist.append(ci)
        return mylist


class Encounter_WaitingAmbush(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    # Info for the plot checker...
    REQUIRES = {STAKES: GET_THE_LEADER, COMPLICATION: NO_COMPLICATION}
    CHANGES = {COMPLICATION: PROFESSIONAL_OPERATION}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(10, 16, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        mytrap = self.register_element("TRAP", pbge.randmaps.rooms.NoWallRoom(10, 1, anchor=pbge.randmaps.anchors.south),
                                       dident="_room")
        myscene.script_rooms.append(mytrap)
        myencounter = self.register_element("_mekroom",
                                            pbge.randmaps.rooms.NoWallRoom(10, 3, anchor=pbge.randmaps.anchors.north),
                                            dident="_room")

        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_mekroom")
        boss_mecha = self.register_element("ENEMY", gears.selector.generate_ace(25, self.elements["ENEMY_FACTION"],
                                                                                myscene.environment))
        team2.contents.append(boss_mecha)
        self.combat_entered = False
        self.trap_ready = True
        self.did_intro = False
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        if self.combat_entered and camp.first_active_pc():
            mycutscene = pbge.cutscene.Cutscene(library={'pc': camp.pc},
                                                beats=(
                                                    pbge.cutscene.Beat(pbge.cutscene.AlertDisplay(
                                                        "You get the feeling that these aren't ordinary bandits. Better be careful from this point on.")),
                                                    pbge.cutscene.Beat(game.content.ghcutscene.MonologueDisplay(
                                                        "This sentry was waiting for us. Whoever these raiders are, they're obviously pros.",
                                                        'npc'), prep=game.content.ghcutscene.LancematePrep('npc')),
                                                )
                                                )
            mycutscene(camp)
            self.combat_entered = False

    def TRAP_ENTER(self, camp):
        if self.trap_ready:
            mycutscene = game.content.ghcutscene.SkillRollCutscene(stats.Perception, stats.Scouting, 50,
                                                                   library={'pc': camp.pc},
                                                                   on_success=(
                                                                       pbge.cutscene.Beat(
                                                                           game.content.ghcutscene.MonologueDisplay(
                                                                               "Watch out, [pc]- there are proximity mines under the snow. Seems like someone is expecting us.",
                                                                               'npc'),
                                                                           prep=game.content.ghcutscene.LancematePrep(
                                                                               'npc', stats=(stats.Scouting,))),
                                                                       pbge.cutscene.Beat(pbge.cutscene.AlertDisplay(
                                                                           "Your sensors detect some proximity mines just underneath the snow. It's a good thing you were paying attention, or you could have walked right into them.")),
                                                                   ),
                                                                   on_failure=(
                                                                       pbge.cutscene.Beat(pbge.cutscene.AlertDisplay(
                                                                           "Without warning, a proximity mine goes off at your feet."),
                                                                                          children=(
                                                                                              pbge.cutscene.Beat(
                                                                                                  game.content.ghcutscene.ExplosionDisplay(),
                                                                                                  children=(
                                                                                                      pbge.cutscene.Beat(
                                                                                                          game.content.ghcutscene.MonologueDisplay(
                                                                                                              "Tough luck. It's too bad we didn't have a scout in the lance... they might have been able to detect the mines.",
                                                                                                              'npc'),
                                                                                                          prep=game.content.ghcutscene.LancematePrep(
                                                                                                              'npc')),
                                                                                                      pbge.cutscene.Beat(
                                                                                                          game.content.ghcutscene.MonologueDisplay(
                                                                                                              "Sorry, I didn't spot the mines on the sensor feed. Guess I need to practice scouting more. Watch out... it looks like somebody is expecting us.",
                                                                                                              'npc'),
                                                                                                          prep=game.content.ghcutscene.LancematePrep(
                                                                                                              'npc',
                                                                                                              stats=(
                                                                                                              stats.Scouting,))),
                                                                                                  )),
                                                                                          )),
                                                                   )
                                                                   )
            mycutscene(camp)
            self.trap_ready = False


class Encounter_CovertAegis(Encounter_BasicBandits):
    LABEL = "MOCHA_MENCOUNTER"
    active = True
    scope = "LOCALE"
    REQUIRES = {ENEMY: BANDITS, COMPLICATION: PROFESSIONAL_OPERATION}
    CHANGES = {ENEMY: AEGIS}

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(10, 16, anchor=pbge.randmaps.anchors.middle),
                                       dident="LOCALE")
        self.register_element("ENEMY_FACTION", gears.factions.AegisOverlord)
        team2 = self.register_element("ETEAM", teams.Team(enemies=(myscene.player_team,)), dident="_room")
        team2.contents += gears.selector.RandomMechaUnit(25, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list
        self.intro_ready = True
        self.load_next(nart)
        return True

    def ETEAM_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            mycutscene = pbge.cutscene.Cutscene(library={'pc': camp.pc},
                                                beats=(
                                                    pbge.cutscene.Beat(game.content.ghcutscene.MonologueDisplay(
                                                        "These bandits we're fighting? I'm not entirely sure that they're bandits... Those look like Aegis colors.",
                                                        'npc'), prep=game.content.ghcutscene.LancematePrep('npc')),
                                                )
                                                )
            mycutscene(camp)
            self.intro_ready = False


#  *****************
#  ***  CHOICES  ***
#  *****************
#
# Each choice will set elements telling what virtue it's based on
# and what story state var it involves, so the second choice won't
# duplicate the first in form or spirit.

VIRTUE = "MHOICE_VIRTUE"
SSTATE = "MHOICE_STORY_STATE"

ONE_WAY_WARNING = "\n\nThe blizzard is getting thicker. You will only be able to follow one of these leads before the trail is lost completely. It's your call."

class Choice_BringJusticeToScumHive(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {ENEMY: PIRATES}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(ENEMY, 0) == PIRATES and pstate.elements.get(VIRTUE,
                                                                                0) != personality.Justice and pstate.elements.get(
            SSTATE, 0) != ENEMY

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Justice)
        self.register_element(SSTATE, ENEMY)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_BASEBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "Pirates don't normally operate in this area; they must have established a smuggling camp to expand their territory. This appears to be the direction they came from." + ONE_WAY_WARNING
        thingmenu.add_item('Bring them to justice', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_PeaceAgainstSynths(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {COMPLICATION: FERAL_SYNTHS}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(COMPLICATION, 0) == FERAL_SYNTHS and pstate.elements.get(VIRTUE,
                                                                                            0) != personality.Peace and pstate.elements.get(
            SSTATE, 0) != COMPLICATION

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Peace)
        self.register_element(SSTATE, COMPLICATION)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_SYNTHBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "It seems that the hunter synths came from this direction. Left unchecked, they could be a much bigger threat to Mauna than {}.".format(
            ENEMY_NOUN[self.elements.get(ENEMY, 0)]) + ONE_WAY_WARNING
        thingmenu.add_item('Protect Mauna by exterminating the synths', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)

    def t_MOCHAVICTORY(self, camp):
        if not self.chose_this_route:
            pbge.alert("You have won the battle. On the way back to Mauna, you radio the Guardians to warn people about the synths in the area.")


class Choice_FellowshipToDefendAgainstSynths(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {COMPLICATION: FERAL_SYNTHS}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(COMPLICATION, 0) == FERAL_SYNTHS and pstate.elements.get(VIRTUE,
                                                                                            0) != personality.Fellowship and pstate.elements.get(
            SSTATE, 0) != COMPLICATION

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Fellowship)
        self.register_element(SSTATE, COMPLICATION)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_SYNTHBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "From the marks in the snow, you see that the hunter synths pursued {} in this direction.".format(
            ENEMY_NOUN[self.elements.get(ENEMY, 0)]) + ONE_WAY_WARNING
        thingmenu.add_item('Show fellowship and rescue them', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)

    def t_MOCHAVICTORY(self, camp):
        if not self.chose_this_route:
            pbge.alert("You have won the battle. On the way back to Mauna, you radio the Guardians to warn people about the synths in the area.")


class Choice_BringJusticeToMercenaries(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {ENEMY: MERCENARY}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(ENEMY, 0) == MERCENARY and pstate.elements.get(VIRTUE,
                                                                                  0) != personality.Justice and pstate.elements.get(
            SSTATE, 0) != ENEMY

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Justice)
        self.register_element(SSTATE, ENEMY)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_WILDBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "You still don't know who hired the mercenaries you fought earlier. This could be an opportunity to trail them to their leader and find out who they work for." + ONE_WAY_WARNING
        thingmenu.add_item('For great justice', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_DutyToFightPirates(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {ENEMY: PIRATES}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(ENEMY, 0) == PIRATES and pstate.elements.get(VIRTUE,
                                                                                0) != personality.Duty and pstate.elements.get(
            SSTATE, 0) != ENEMY

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Duty)
        self.register_element(SSTATE, ENEMY)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_WILDBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "The pirates seem to be having trouble navigating on Earth. They've left the road and headed into the forest. It should be no problem to catch up with them there." + ONE_WAY_WARNING
        thingmenu.add_item('Do your duty', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_FellowshipWithSmugglers(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {COMPLICATION: CONTRABAND_CARGO}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(COMPLICATION, 0) == CONTRABAND_CARGO and pstate.elements.get(VIRTUE,
                                                                                                0) != personality.Fellowship and pstate.elements.get(
            SSTATE, 0) != COMPLICATION

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Fellowship)
        self.register_element(SSTATE, COMPLICATION)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_TRUCKBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "Marks in the snow indicate that the smugglers are still being pursued by {}. It seems cruel to leave them to their fate... You can defend the convoy and let the Guardians figure out what to do about the contraband later.".format(
            ENEMY_NOUN[self.elements.get(ENEMY, 0)]) + ONE_WAY_WARNING
        thingmenu.add_item('Show your fellowship', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_BringJusticeToSmugglers(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {COMPLICATION: CONTRABAND_CARGO}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(COMPLICATION, 0) == CONTRABAND_CARGO and pstate.elements.get(VIRTUE,
                                                                                                0) != personality.Justice and pstate.elements.get(
            SSTATE, 0) != COMPLICATION

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Justice)
        self.register_element(SSTATE, COMPLICATION)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        # Set a new boss for the final scene.
        boss_mecha = gears.selector.generate_ace(50, ConvoyFaction, myscene.environment)
        self.add_sub_plot(nart, "MOCHA_FB_TRUCKBATTLE", PlotState(
            elements={"BOSS": boss_mecha, "BOSS_PILOT": boss_mecha.get_pilot(),
                      "ENEMY_FACTION": ConvoyFaction, }).based_on(self), ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "The smugglers who got away from {} seem to have gone in this direction. Their actions tonight have endangered a great number of lives, and they shouldn't get away with it.".format(
            ENEMY_NOUN[self.elements.get(ENEMY, 0)]) + ONE_WAY_WARNING
        thingmenu.add_item('For great justice', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_JusticeForWujungOrphans(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {STAKES: STOLEN_TOYS}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(STAKES, 0) == STOLEN_TOYS and pstate.elements.get(VIRTUE,
                                                                                     0) != personality.Justice and pstate.elements.get(
            SSTATE, 0) != STAKES

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Justice)
        self.register_element(SSTATE, STAKES)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_TRUCKBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = 'From the tracks in the snow, you think this is the way the thieves brought the stolen toys. If you hurry you may still be able to catch them and return the toys to the children of Wujung.' + ONE_WAY_WARNING
        thingmenu.add_item('For great justice', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_GloryByDestroyingBigBase(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {COMPLICATION: PROFESSIONAL_OPERATION}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(COMPLICATION, 0) == PROFESSIONAL_OPERATION and pstate.elements.get(VIRTUE,
                                                                                                      0) != personality.Glory and pstate.elements.get(
            SSTATE, 0) != COMPLICATION

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Glory)
        self.register_element(SSTATE, COMPLICATION)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_BASEBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "In order to pull off an operation like this, {} must have a base nearby. This seems to be the direction from which they came.".format(
            ENEMY_NOUN[self.elements.get(ENEMY, 0)]) + ONE_WAY_WARNING
        thingmenu.add_item('Go for glory', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_GloryByDestroyingBanditBase(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {ENEMY: BANDITS}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(ENEMY, 0) == BANDITS and pstate.elements.get(VIRTUE,
                                                                                0) != personality.Glory and pstate.elements.get(
            SSTATE, 0) != ENEMY

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Glory)
        self.register_element(SSTATE, ENEMY)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_BASEBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = 'The tracks in the snow indicate that the bandits came from this direction. If you follow the tracks back to their base, you may be able to put an end to their crime spree once and for all.' + ONE_WAY_WARNING
        thingmenu.add_item('Go for glory', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_PeaceByDefeatingAegis(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {COMPLICATION: AEGIS_SCOUTS}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(COMPLICATION, 0) == AEGIS_SCOUTS and pstate.elements.get(VIRTUE,
                                                                                            0) != personality.Peace and pstate.elements.get(
            SSTATE, 0) != COMPLICATION

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Peace)
        self.register_element(SSTATE, COMPLICATION)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_BASEBATTLE",
                          PlotState(elements={"ENEMY_FACTION": gears.factions.AegisOverlord, }).based_on(self),
                          ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = 'The tracks in the snow indicate that this is the direction the Aegis scouts came from. Stopping them may be far more important than {} you were sent to fight.'.format(
            ENEMY_NOUN[self.elements.get(ENEMY, 0)]) + ONE_WAY_WARNING
        thingmenu.add_item('Protect the Earth', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)

    def t_MOCHAVICTORY(self, camp):
        if not self.chose_this_route:
            pbge.alert("You have won the battle. On the way back to Mauna, you radio the Defense Force to let them know there are Aegis infiltrators in the area.")


class Choice_GloryByFightingTheLeader(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {STAKES: GET_THE_LEADER}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(STAKES, 0) == GET_THE_LEADER and pstate.elements.get(VIRTUE,
                                                                                        0) != personality.Glory and pstate.elements.get(
            SSTATE, 0) != STAKES

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Glory)
        self.register_element(SSTATE, STAKES)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_WILDBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = "This seems to be the way that the raider leader went. It's time to finish this." + ONE_WAY_WARNING
        thingmenu.add_item('Go for glory', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_DutyToCatchTheLeader(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {STAKES: GET_THE_LEADER}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(STAKES, 0) == GET_THE_LEADER and pstate.elements.get(VIRTUE,
                                                                                        0) != personality.Duty and pstate.elements.get(
            SSTATE, 0) != STAKES

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Duty)
        self.register_element(SSTATE, STAKES)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_BOSSBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = 'This seems to be the way that the raider leader went. Do you want to try to capture them?' + ONE_WAY_WARNING
        thingmenu.add_item('Do your duty', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class Choice_PeaceToDisableThePrototype(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {STAKES: PROTOTYPE_MECHA}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(STAKES, 0) == PROTOTYPE_MECHA and pstate.elements.get(VIRTUE,
                                                                                         0) != personality.Peace and pstate.elements.get(
            SSTATE, 0) != STAKES

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Peace)
        self.register_element(SSTATE, STAKES)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_WILDBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = 'This seems to be the direction that the prototype mecha was taken. A weapon that powerful should not fall into the wrong hands.' + ONE_WAY_WARNING
        thingmenu.add_item('Fight for peace', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)

    def t_MOCHAVICTORY(self, camp):
        if not self.chose_this_route and not camp.campdata.get(MOVAR_FOUGHTBLITZEN, False):
            pbge.alert("You have won the battle. On the way back to Mauna, you radio the Guardians to let them know the missing prototype is still out there.")


class Choice_DutyToStopThePrototype(Plot):
    LABEL = "MOCHA_MHOICE"
    active = True
    scope = True
    # Info for the plot checker...
    REQUIRES = {STAKES: PROTOTYPE_MECHA}
    chose_this_route = False

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return pstate.elements.get(STAKES, 0) == PROTOTYPE_MECHA and pstate.elements.get(VIRTUE,
                                                                                         0) != personality.Duty and pstate.elements.get(
            SSTATE, 0) != STAKES

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element(VIRTUE, personality.Duty)
        self.register_element(SSTATE, STAKES)
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Continue Onward",
                                                                     anchor=self.elements["MHOICE_ANCHOR"]),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_BOSSBATTLE", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)
        camp.campdata[MOVAR_FOUGHTBLITZEN] = True
        self.chose_this_route = True

    def t_MOCHAVICTORY(self, camp):
        if not self.chose_this_route and not camp.campdata.get(MOVAR_FOUGHTBLITZEN, False):
            pbge.alert("You have won the battle. On the way back to Mauna, you radio the Guardians to let them know the missing prototype is still out there.")

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = 'This seems to be the way that the raider leader went. Do you want to try to recover the stolen prototype?' + ONE_WAY_WARNING
        thingmenu.add_item('Do your duty', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


#  *************************
#  ***   FINAL  BATTLE   ***
#  *************************
#
# The final battle will usually be composed of two subplots: One holding
# the battle itself, and one holding the enemy leader's conversation bits.
#

class FinalBattleDebug(Plot):
    LABEL = "MOCHA_FB_DEBUGSTUB"
    active = True
    scope = True

    # Info for the plot checker...
    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        mygoal = self.register_element("_room",
                                       pbge.randmaps.rooms.NoWallRoom(5, 5, anchor=pbge.randmaps.anchors.southwest),
                                       dident="LOCALE")
        myexit = self.register_element("_waypoint", ghwaypoints.Exit(plot_locked=True, name="Debug Ending",
                                                                     anchor=pbge.randmaps.anchors.middle),
                                       dident="_room")
        self.add_sub_plot(nart, "MOCHA_FB_DEBUG", ident="FINAL_ENCOUNTER")
        return True

    def start_mission(self, camp):
        self.subplots["FINAL_ENCOUNTER"].start_battle(camp)

    def _waypoint_menu(self, camp, thingmenu):
        thingmenu.desc = 'This seems to be a final battle in need of debugging.'
        thingmenu.add_item('Do your duty', self.start_mission)
        thingmenu.add_item('Examine the other options first', None)


class FinalBattleAgainstSynths(Plot):
    LABEL = "MOCHA_FB_SYNTHBATTLE"
    # LABEL = "MOCHA_FB_DEBUG"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(30, 30, "Boss Battle", player_team=team1, scale=gears.scale.MechaScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow, myfilter, mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, myarchi)
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'
        myroom = pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene, anchor=pbge.randmaps.anchors.south)
        myent = self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)
        mygoal = self.register_element("_goalroom", pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene,
                                                                                  anchor=pbge.randmaps.anchors.middle))
        team2 = self.register_element("_eteam", teams.Team(enemies=(team1,)), dident="_goalroom")
        meks = gears.selector.RandomMonsterUnit(25, 100, myscene.environment, ("SYNTH", "HUNTER-X"), myscene.scale)
        team2.contents += meks.contents

        return True

    def start_battle(self, camp):
        myscene = self.elements["LOCALE"]
        camp.go(self.elements["ENTRANCE"])

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if not myteam.get_members_in_play(camp):
            camp.check_trigger('MOCHAVICTORY')


class FinalBattleAgainstBase(Plot):
    LABEL = "MOCHA_FB_BASEBATTLE"
    # LABEL = "MOCHA_FB_DEBUG"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(30, 30, "Boss Battle", player_team=team1, scale=gears.scale.MechaScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow, myfilter, mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, myarchi)
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'
        myroom = pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene, anchor=pbge.randmaps.anchors.south)
        myent = self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)
        mygoal = self.register_element("_goalroom", WinterMochaFortressRoom(10, 10, parent=myscene,
                                                                            anchor=pbge.randmaps.anchors.middle))
        team2 = self.register_element("_eteam", teams.Team(enemies=(team1,)), dident="_goalroom")
        team2.contents += gears.selector.RandomMechaUnit(35, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list

        mybuilding = gears.selector.get_design_by_full_name("Bunker")
        team2.contents.append(mybuilding)
        self.register_element("BOSS", mybuilding)
        return True

    def start_battle(self, camp):
        myscene = self.elements["LOCALE"]
        camp.go(self.elements["ENTRANCE"])

    def t_ENDCOMBAT(self, camp):
        myboss = self.elements["BOSS"]
        if not myboss.is_operational():
            camp.check_trigger('MOCHAVICTORY')


class FinalBattleAgainstTrucks(Plot):
    LABEL = "MOCHA_FB_TRUCKBATTLE"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(30, 30, "Boss Battle", player_team=team1, scale=gears.scale.MechaScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow, myfilter, mutate=mymutate)
        myscenegen = WinterHighwaySceneGen(myscene, myarchi)
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'
        myroom = pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene, anchor=pbge.randmaps.anchors.south)
        myent = self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)
        boringroom = pbge.randmaps.rooms.NoWallRoom(5, 5, parent=myscene, anchor=pbge.randmaps.anchors.north)
        mygoal = self.register_element("_goalroom", pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene,
                                                                                  anchor=pbge.randmaps.anchors.middle))
        mygoal.contents.append(WinterMochaTruckTerrain)
        mygoal.contents.append(WinterMochaTruckTerrain)
        team2 = self.register_element("_eteam", teams.Team(enemies=(team1,)), dident="_goalroom")
        team2.contents += gears.selector.RandomMechaUnit(35, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list

        self.add_sub_plot(nart, "MOCHA_FB_BOSSTALK")
        return True

    def start_battle(self, camp):
        myscene = self.elements["LOCALE"]
        camp.go(self.elements["ENTRANCE"])
        boss = self.elements["BOSS"]
        pos = self.elements["_goalroom"].area.center
        myscene.place_actor(boss, pos[0], pos[1], self.elements["_eteam"])

    def t_ENDCOMBAT(self, camp):
        myboss = self.elements["BOSS"]
        if not myboss.is_operational():
            camp.check_trigger('MOCHAVICTORY')


class FinalBattleAgainstBoss(Plot):
    LABEL = "MOCHA_FB_BOSSBATTLE"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(30, 30, "Boss Battle", player_team=team1, scale=gears.scale.MechaScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow, myfilter, mutate=mymutate)
        myscenegen = WinterHighwaySceneGen(myscene, myarchi)
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'
        myroom = pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene, anchor=pbge.randmaps.anchors.south)
        myent = self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)
        boringroom = pbge.randmaps.rooms.NoWallRoom(5, 5, parent=myscene, anchor=pbge.randmaps.anchors.north)
        mygoal = self.register_element("_goalroom", pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene,
                                                                                  anchor=pbge.randmaps.anchors.middle))
        team2 = self.register_element("_eteam", teams.Team(enemies=(team1,)), dident="_goalroom")
        team2.contents += gears.selector.RandomMechaUnit(35, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list

        self.add_sub_plot(nart, "MOCHA_FB_BOSSTALK")
        return True

    def start_battle(self, camp):
        myscene = self.elements["LOCALE"]
        camp.go(self.elements["ENTRANCE"])
        boss = self.elements["BOSS"]
        pos = self.elements["_goalroom"].area.center
        myscene.place_actor(boss, pos[0], pos[1], self.elements["_eteam"])

    def t_ENDCOMBAT(self, camp):
        myboss = self.elements["BOSS"]
        if not myboss.is_operational():
            camp.check_trigger('MOCHAVICTORY')


class FinalBattleAgainstBossInWoods(Plot):
    LABEL = "MOCHA_FB_WILDBATTLE"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(30, 30, "Boss Battle", player_team=team1, scale=gears.scale.MechaScale)
        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow, myfilter, mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, myarchi)
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'
        myroom = pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene, anchor=pbge.randmaps.anchors.south)
        myent = self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)
        mygoal = self.register_element("_goalroom", pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene,
                                                                                  anchor=pbge.randmaps.anchors.middle))
        team2 = self.register_element("_eteam", teams.Team(enemies=(team1,)), dident="_goalroom")
        team2.contents += gears.selector.RandomMechaUnit(35, 50, self.elements["ENEMY_FACTION"],
                                                         myscene.environment).mecha_list

        self.add_sub_plot(nart, "MOCHA_FB_BOSSTALK")
        return True

    def start_battle(self, camp):
        myscene = self.elements["LOCALE"]
        camp.go(self.elements["ENTRANCE"])
        boss = self.elements["BOSS"]
        pos = self.elements["_goalroom"].area.center
        myscene.place_actor(boss, pos[0], pos[1], self.elements["_eteam"])

    def t_ENDCOMBAT(self, camp):
        myboss = self.elements["BOSS"]
        if not myboss.is_operational():
            camp.check_trigger('MOCHAVICTORY')


#  ********************
#  ***   BOSSTALK   ***
#  ********************
#
# The conversation with the boss is separated from the encounter itself
# so we don't have to repeat the encounter mechanics for identical
# battles with different setups.
#

class BossyTrashTalk(Plot):
    LABEL = "MOCHA_FB_BOSSTALK"
    active = True
    scope = "LOCALE"

    def BOSS_ACTIVATE(self, camp):
        ghdialogue.start_conversation(camp, camp.pc, self.elements["BOSS_PILOT"], cue=ghdialogue.ATTACK_STARTER)


# Old stuff.

class WinterBattle(Plot):
    # Go fight mecha near Mauna.
    LABEL = "OLD_MOCHA_MISSION"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        """The mission leadup will be two highway scenes with an intro, two
           encounters, a recharge, and two choices at the end. The choices
           will handle their own scenes."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(60, 60, "Near Mauna", player_team=team1, scale=gears.scale.MechaScale)

        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow, myfilter, mutate=mymutate)
        myscenegen = WinterHighwaySceneGen(myscene, myarchi)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'

        myroom = pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene, anchor=pbge.randmaps.anchors.south)
        myent = self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(myent)

        boringroom = pbge.randmaps.rooms.NoWallRoom(5, 5, parent=myscene)

        mygoal = pbge.randmaps.rooms.NoWallRoom(10, 10, parent=myscene, anchor=pbge.randmaps.anchors.north)
        team2 = teams.Team(enemies=(team1,))
        boss_mecha = gears.selector.get_design_by_full_name("WM Custom Blitzen")
        boss_mecha.load_pilot(gears.selector.random_pilot(50))
        mygoal.contents.append(boss_mecha)
        myscene.local_teams[boss_mecha] = team2

        return True

    def t_ENDCOMBAT(self, camp):
        myboss = self.elements["BOSS"]
        if not myboss.is_operational():
            pbge.alert("Victory! Thank you for trying GearHead Caramel. Keep watching for more updates.")
        elif not camp.first_active_pc():
            pbge.alert("Game over. Better luck next time.")

    def t_START(self, camp):
        pass

    def enter_combat(self, camp):
        camp.go(self.elements["ENTRANCE"])


#  ************************
#  ***   PUZZLE  BITS   ***
#  ************************
#
# A PuzzleBit subplot takes a "TARGET" element and does some kind of thing
# to it. When the action is successfully done, it sends a trigger back to
# the plot that generated it.

class MeltWithHeat(Plot):
    # Heat should be able to melt a snowdrift. This MELT plot request just
    # branches the request to either a HEAT or a WIND plot, which is kind of a
    # kludgey way to handle things but I wanted to make this division explicit
    # so you can see clearly how the puzzle generator works from this
    # not-much-content example.
    LABEL = "MELT"
    active = True
    scope = True

    def custom_init(self, nart):
        self.add_sub_plot(nart, "HEAT")
        return True

    def TARGET_HEAT(self, camp):
        camp.check_trigger("MELT", self.elements["TARGET"])
        self.active = False


class MeltWithWind(Plot):
    # See above.
    LABEL = "MELT"
    active = True
    scope = True

    def custom_init(self, nart):
        self.add_sub_plot(nart, "WIND")
        return True

    def TARGET_WIND(self, camp):
        camp.check_trigger("MELT", self.elements["TARGET"])
        self.active = False


class BurnTheBarrels(Plot):
    # Burn down the malls! Burn down the malls!
    LABEL = "HEAT"
    active = True
    scope = True

    def custom_init(self, nart):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM", pbge.randmaps.rooms.NoWallRoom(5, 5), dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",
                                            WinterMochaBarrel(plot_locked=True, anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot(nart, "IGNITE", PlotState(elements={"TARGET": puzzle_item}).based_on(self))
        return True

    SPRITE_OFF = [(0, 0), (-14, 0), (-6, 12), (6, 9), (14, 0), (6, -12), (-6, -12)]

    def PUZZITEM_IGNITE(self, camp):
        pbge.alert("The barrel of fuel fires up, melting some of the nearby snow.")
        scene = self.elements["LOCALE"]
        barrel = self.elements["PUZZITEM"]

        random.shuffle(self.SPRITE_OFF)
        for t in range(5):
            pbge.my_state.view.anim_list.append(
                gears.geffects.BigBoom(pos=barrel.pos, x_off=self.SPRITE_OFF[t][0], y_off=self.SPRITE_OFF[t][1],
                                       delay=t * 5))
        pbge.my_state.view.handle_anim_sequence()

        scene._map[barrel.pos[0]][barrel.pos[1]].decor = WinterMochaBurningBarrelTerrain
        camp.check_trigger("HEAT", self.elements["TARGET"])
        self.active = False


class IndustrialStrengthHeater(Plot):
    # Activate an industrial heat lamp to get rid of some snow
    LABEL = "HEAT"
    active = True
    scope = True

    def custom_init(self, nart):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM", pbge.randmaps.rooms.NoWallRoom(5, 5), dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",
                                            WinterMochaHeatLamp(plot_locked=True, anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot(nart, "ENERGIZE", PlotState(elements={"TARGET": puzzle_item}).based_on(self))
        return True

    def PUZZITEM_ENERGIZE(self, camp):
        pbge.alert("The industrial heat lamp fires up, melting some of the nearby snow.")
        camp.check_trigger("HEAT", self.elements["TARGET"])
        self.active = False


class IndustrialStrengthBlower(Plot):
    # Activate an industrial blower for an artificial chinook.
    LABEL = "WIND"
    active = True
    scope = True

    def custom_init(self, nart):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM", pbge.randmaps.rooms.NoWallRoom(5, 5), dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",
                                            WinterMochaBlower(plot_locked=True, anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot(nart, "ENERGIZE", PlotState(elements={"TARGET": puzzle_item}).based_on(self))

        return True

    def PUZZITEM_ENERGIZE(self, camp):
        pbge.alert("The industrial blower roars into action, melting some of the nearby snow.")
        camp.check_trigger("WIND", self.elements["TARGET"])
        self.active = False


class OpenGeothermalVent(Plot):
    # Open the geothermal generator, let the steam out.
    LABEL = "WIND"
    active = True
    scope = True

    def custom_init(self, nart):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM", pbge.randmaps.rooms.NoWallRoom(5, 5), dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",
                                            WinterMochaGenerator(plot_locked=True, anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot(nart, "OPEN", PlotState(elements={"TARGET": puzzle_item}).based_on(self))

        return True

    def PUZZITEM_OPEN(self, camp):
        pbge.alert("A sudden blast of steam escapes from the geothermal vent, melting some of the nearby snow.")
        camp.check_trigger("WIND", self.elements["TARGET"])
        self.active = False


class LazyassOpener(Plot):
    # You want to open this thing? Just open it.
    # Not much of a puzzle, but if I'm gonna get this demo released this week...
    LABEL = "OPEN"
    active = True
    scope = True

    def TARGET_menu(self, camp, thingmenu):
        thingmenu.add_item('Try to open it', self._try_open)

    def _try_open(self, camp):
        pbge.alert("You open it easily. Who leaves stuff like this unlocked?!")
        camp.check_trigger("OPEN", self.elements["TARGET"])
        self.active = False


class UniversalLockpick(Plot):
    # You know what opens stuff? A crowbar.
    # Since this is just a demo, we're just simulating the key items.
    LABEL = "OPEN"
    active = True
    scope = True

    def custom_init(self, nart):
        puzzle_item = self.register_element("PUZZITEM", "Crowbar")
        self.add_sub_plot(nart, "FIND", PlotState(elements={"TARGET": puzzle_item}).based_on(self), ident="FINDER")
        self.found_item = False
        return True

    def TARGET_menu(self, camp, thingmenu):
        if self.found_item:
            thingmenu.add_item('Open it with the crowbar', self._open_thing)
        else:
            thingmenu.add_item('Try to open it', self._try_open)

    def _open_thing(self, camp):
        pbge.alert("The crowbar makes short work of the lock.")
        camp.check_trigger("OPEN", self.elements["TARGET"])
        self.active = False

    def _try_open(self, camp):
        pbge.alert("It's locked.")
        self.subplots["FINDER"].activate(camp)

    def PUZZITEM_FIND(self, camp):
        self.found_item = True


class FindAbandonedToolbox(Plot):
    # The item you seek is in an abandoned toolbox.
    LABEL = "FIND"
    active = True
    scope = True

    def custom_init(self, nart):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM", pbge.randmaps.rooms.NoWallRoom(5, 5), dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",
                                            WinterMochaToolbox(plot_locked=True, anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        return True

    def get_crowbar(self, camp):
        pbge.alert("You take the {}. It might be useful for something.".format(self.elements["TARGET"]))
        camp.check_trigger("FIND", self.elements["TARGET"])
        self.active = False

    def PUZZITEM_menu(self, camp, thingmenu):
        thingmenu.desc = '{} There is a {} inside.'.format(thingmenu.desc, self.elements["TARGET"])
        thingmenu.add_item('Borrow the {}'.format(self.elements["TARGET"]), self.get_crowbar)


class BorrowAnItem(Plot):
    # The item you seek is held by an NPC.
    LABEL = "FIND"
    active = False
    scope = True

    def custom_init(self, nart):
        mynpc = self.seek_element(nart, "NPC", self._seek_npc)
        return True

    def _seek_npc(self, nart, candidate):
        return isinstance(candidate, gears.base.Character)

    def _get_item(self, camp):
        camp.check_trigger("FIND", self.elements["TARGET"])
        self.active = False

    def t_UPDATE(self, camp):
        if self.active and self.elements["NPC"] in camp.party:
            pbge.alert("{} says 'Here, you can borrow my {}'.".format(self.elements["NPC"], self.elements["TARGET"]))
            self._get_item(camp)

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(pbge.dialogue.Offer('Sure, here you go.',
                                          context=pbge.dialogue.ContextTag((ghdialogue.context.ASK_FOR_ITEM,)),
                                          data={'item': self.elements["TARGET"]}, effect=self._get_item))
        return mylist


class ExtensionCord(Plot):
    # Have you tried plugging it in?
    LABEL = "ENERGIZE"
    active = True
    scope = True

    def custom_init(self, nart):
        puzzle_item = self.register_element("PUZZITEM", "Extension Cord")
        self.add_sub_plot(nart, "FIND", PlotState(elements={"TARGET": puzzle_item}).based_on(self), ident="FINDER")
        self.found_item = False
        return True

    def TARGET_menu(self, camp, thingmenu):
        if self.found_item:
            thingmenu.add_item('Plug it in and turn it on', self._open_thing)
        else:
            thingmenu.add_item('Try to turn it on', self._try_activate)

    def _open_thing(self, camp):
        pbge.alert("You connect it to the electrical outlet and press the power button...")
        camp.check_trigger("ENERGIZE", self.elements["TARGET"])
        self.active = False

    def _try_activate(self, camp):
        pbge.alert("Nothing happens. It doesn't have any power. You notice that it isn't plugged in.")
        self.subplots["FINDER"].activate(camp)

    def PUZZITEM_FIND(self, camp):
        self.found_item = True


class CircuitBroken(Plot):
    # The generator's offline; try wiggling the switch.
    LABEL = "ENERGIZE"
    active = True
    scope = True

    def custom_init(self, nart):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM", pbge.randmaps.rooms.NoWallRoom(5, 5), dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",
                                            WinterMochaGenerator(plot_locked=True, anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        return True

    def TARGET_menu(self, camp, thingmenu):
        thingmenu.add_item('Try to turn it on', self._try_activate)

    def _try_activate(self, camp):
        pbge.alert("Nothing happens. Everything seems to be connected properly, but it isn't getting any power.")

    def PUZZITEM_menu(self, camp, thingmenu):
        thingmenu.desc = '{} The generator is currently off; the circuit breaker must have blown during the storm.'.format(
            thingmenu.desc)
        thingmenu.add_item("Turn it back on again", self._fix_generator)
        thingmenu.add_item("Leave it alone", None)

    def _fix_generator(self, camp):
        pbge.alert("You reset the controls, and the generator flickers back to life.")
        camp.check_trigger("ENERGIZE", self.elements["TARGET"])
        self.active = False


class OpenContainer(Plot):
    # Let oxygen do all the heavy lifting.
    LABEL = "IGNITE"
    active = True
    scope = True

    def custom_init(self, nart):
        self.add_sub_plot(nart, "OPEN", ident="OPENER")
        return True

    def TARGET_menu(self, camp, thingmenu):
        thingmenu.desc = '{} There is a large red warning label pasted to the front.'.format(thingmenu.desc)
        thingmenu.add_item('Read the warning label', self._try_activate)
        thingmenu.add_item('Leave it alone', None)

    def _try_activate(self, camp):
        pbge.alert(
            "Warning: Contents will react violently when exposed to oxygen. Extreme caution should be used when handling.")
        self.subplots["OPENER"].activate(camp)

    def TARGET_OPEN(self, camp):
        pbge.alert("You open it up and retreat to a safe distance as the fireworks begin.")
        camp.check_trigger("IGNITE", self.elements["TARGET"])
        self.active = False


class UseFlares(Plot):
    # Easiest way to set something on fire is to set it on fire
    LABEL = "IGNITE"
    active = True
    scope = True

    def custom_init(self, nart):
        puzzle_item = self.register_element("PUZZITEM", "Flare")
        self.add_sub_plot(nart, "FIND", PlotState(elements={"TARGET": puzzle_item}).based_on(self), ident="FINDER")
        self.found_item = False
        return True

    def TARGET_menu(self, camp, thingmenu):
        thingmenu.desc = '{} There is a large yellow warning label pasted to the front.'.format(thingmenu.desc)
        if self.found_item:
            thingmenu.add_item('Place a lit flare in the barrel', self._open_thing)
            thingmenu.add_item('Leave it alone', None)
        else:
            thingmenu.add_item('Read the warning label', self._try_activate)

    def _open_thing(self, camp):
        pbge.alert("You stick the lit flare in the barrel's spigot and retreat to a safe distance...")
        camp.check_trigger("IGNITE", self.elements["TARGET"])
        self.active = False

    def _try_activate(self, camp):
        pbge.alert("Warning: Highly flammable. Keep away from sparks and open flame.")
        self.subplots["FINDER"].activate(camp)

    def PUZZITEM_FIND(self, camp):
        self.found_item = True

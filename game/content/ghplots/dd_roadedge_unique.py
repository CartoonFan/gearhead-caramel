import random

import game.content
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints,  ghrooms,  ghcutscene
from game import teams
from game.content.ghplots import missionbuilder
from game.content.ghcutscene import SimpleMonologueDisplay
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, PlotState
from . import dd_customobjectives,  mechadungeons
from .dd_homebase import BiotechDiscovery
from .dd_roadedge import DZDREBasicPlotWithEncounterStuff, DeadZoneHighwaySceneGen
from pbge.memos import Memo


#   ***************************************
#   ***   DZD_ROADEDGE_ROADOFNORETURN   ***
#   ***************************************

class RoadOfNoReturnPlot(DZDREBasicPlotWithEncounterStuff):
    LABEL = "DZD_ROADEDGE_ROADOFNORETURN"

    active = True
    scope = True
    UNIQUE = True
    BASE_RANK = 30
    ENCOUNTER_NAME = "Mystery Ambush"
    ENCOUNTER_CHANCE = BASE_RANK + 10
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleSemiDeadzone
    ENCOUNTER_OBJECTIVES = (
        missionbuilder.BAMO_SURVIVE_THE_AMBUSH,
    )
    DEFAULT_OBJECTIVES = tuple()

    FACTION_OPTIONS = (gears.factions.AegisOverlord, gears.factions.ClanIronwind, gears.factions.BoneDevils,
                       None, None, None)

    def custom_init(self, nart):
        super().custom_init(nart)
        self.elements["FACTION"] = gears.factions.Circle(nart.camp, parent_faction=random.choice(self.FACTION_OPTIONS))
        self.elements["ENEMY_FACTION"] = self.elements["FACTION"]
        my_edge = self.elements["DZ_EDGE"]
        self.elements["GATE_A"] = my_edge.start_node.entrance
        self.elements["GATE_B"] = my_edge.end_node.entrance
        
        # Add the entry scene.
        self.elements[dungeonmaker.DG_NAME] = "The Road of No Return"
        self.elements[dungeonmaker.DG_ARCHITECTURE] = gharchitecture.MechaScaleSemiDeadzone()
        self.elements[dungeonmaker.DG_SCENE_TAGS] = (gears.tags.SCENE_OUTDOORS,  gears.personality.DeadZone)
        self.elements[dungeonmaker.DG_EXPLO_MUSIC] = "HoliznaCC0 - Lost In Space.ogg"
        self.elements[dungeonmaker.DG_COMBAT_MUSIC] = "Komiku_-_03_-_Battle_Theme.ogg" 
        self.elements[mechadungeons.MDG_DUNGEON] = mechadungeons.MechaDungeon("The Road of No Return")
        
        my_dungeon = self.add_sub_plot(nart, "DZD_RONRDUNGEON")
        self.elements["DUNGEON_ENTRANCE"] = my_dungeon.elements["ENTRANCE"]
        
        self._got_rumor = False
        return True
        
    def MDG_DUNGEON_WIN(self, camp):
        self.elements[mechadungeons.MDG_DUNGEON].status = self.elements[mechadungeons.MDG_DUNGEON].DEFEATED
        self.elements["DZ_EDGE"].style = self.elements["DZ_EDGE"].STYLE_SAFE
        self.road_cleared = True
        self.memo = None

    def GATE_A_menu(self, camp, thingmenu):
        if self._got_rumor:
            thingmenu.add_item('Search "The Road of No Return".', self.go_to_locale)

    def GATE_B_menu(self, camp, thingmenu):
        self.GATE_A_menu(camp, thingmenu)

    def go_to_locale(self, camp: gears.GearHeadCampaign):
        camp.go(self.elements["DUNGEON_ENTRANCE"])

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared and not self._got_rumor:
            # This city is on this road.
            mygram["[News]"] = ['the highway to {} is called "The Road of No Return"'.format(
                self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        myscene = camp.scene.get_root_scene()
        myedge = self.elements["DZ_EDGE"]

        if myedge.connects_to_city(myscene) and not self.road_cleared and not self._got_rumor:
            goffs.append(Offer(
                "A lot of people have disappeared without a trace while traveling the highway. Whole convoys gone, with no wreckage left behind. Some people say the road is haunted by the ghosts of a long-dead hive city.",
                ContextTag([context.INFO,]), effect=self._get_rumor, subject="The Road of No Return", 
                data={"subject": "the Road of No Return"},  no_repeats=True
            ))
        return goffs

    def _get_rumor(self, camp):
        self._got_rumor = True
        self.memo = "The highway between {} and {} is called the Road of No Return because a lot of convoys have gone missing there.".format(self.elements["DZ_EDGE"].start_node.destination, self.elements["DZ_EDGE"].end_node.destination)


class RONRDungeon(Plot):
    LABEL = "DZD_RONRDUNGEON"

    active = True
    scope = "LOCALE"

    def custom_init(self,  nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,))

        myscene = gears.GearHeadScene(50, 50, "The Road of No Return", player_team=team1, civilian_team=team2,
            scale=gears.scale.MechaScale, is_metro=False,
            attributes=(gears.personality.DeadZone, gears.tags.SCENE_OUTDOORS), 
            exploration_music=self.elements[dungeonmaker.DG_EXPLO_MUSIC], 
            combat_music=self.elements[dungeonmaker.DG_COMBAT_MUSIC]
        )   

        myscene.contents.append(ghrooms.MSRuinsRoom(5,5))
        myscene.contents.append(ghrooms.WreckageRoom(5,5))
        entry_room = pbge.randmaps.rooms.Room(5, 5,  anchor=pbge.randmaps.anchors.middle)
        myscene.contents.append(entry_room)

        my_edge = self.elements["DZ_EDGE"]
        my_entrance = pbge.scenes.waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle)
        entry_room.contents.append(my_entrance)
        self.elements["ENTRANCE"] = my_entrance
        
        entry_room.contents.append(ghwaypoints.WreckWP())
        entry_room.contents.append(ghwaypoints.WreckWP())
        entry_room.contents.append(ghwaypoints.WreckWP())

        if my_edge.start_node.pos[1] < my_edge.end_node.pos[1]:
            north_node = my_edge.start_node
            south_node = my_edge.end_node
        else:
            north_node = my_edge.end_node
            south_node = my_edge.start_node

        north_room = pbge.randmaps.rooms.FuzzyRoom(5, 5,  anchor=pbge.randmaps.anchors.north)
        north_gate = ghwaypoints.Exit(north_node.entrance, name="To {}".format(str(north_node.destination)), anchor=pbge.randmaps.anchors.middle)
        north_room.contents.append(north_gate)
        
        south_room = pbge.randmaps.rooms.FuzzyRoom(5, 5,  anchor=pbge.randmaps.anchors.south)
        south_gate = ghwaypoints.Exit(south_node.entrance, name="To {}".format(str(south_node.destination)), anchor=pbge.randmaps.anchors.middle)
        south_room.contents.append(south_gate)
        
        myscene.contents.append(north_room)
        myscene.contents.append(south_room)
 
        myscenegen = gharchitecture.VerticalHighwaySceneGen(myscene, gharchitecture.MechaScaleSemiDeadzoneRuins())
        
        self.last_update = 0
        self.intro_ready = True

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")
        
        self.add_sub_plot(nart, "MDUNGEON_ENCOUNTER",)
        
        if random.randint(1, 2) == 2:
            direction = (pbge.randmaps.anchors.east,  pbge.randmaps.anchors.west)
        else:
            direction = (pbge.randmaps.anchors.west,  pbge.randmaps.anchors.east)
            
        level_one = self.add_sub_plot(nart,  "MECHA_DUNGEON_GENERIC",  elements={dungeonmaker.DG_NAME: "Road of No Return 2",  dungeonmaker.DG_PARENT_SCENE: myscene})
        level_one_locale = level_one.elements["LOCALE"]
        plotutility.SceneConnection(nart,  self,  myscene,  level_one_locale,  anchor1=direction[0],  anchor2=direction[1])
        
        two_to_three_room = pbge.randmaps.rooms.FuzzyRoom(9, 12,  anchor=direction[0])
        level_one_locale.contents.append(two_to_three_room)

        level_two = self.add_sub_plot(nart,  "MECHA_DUNGEON_GENERIC",  elements={dungeonmaker.DG_NAME: "Road of No Return 3",  dungeonmaker.DG_PARENT_SCENE: level_one_locale})
        level_two_locale = level_two.elements["LOCALE"]
        plotutility.SceneConnection(nart,  self,  level_one_locale, level_two_locale, room1=two_to_three_room,  anchor2=direction[1])
        self.add_sub_plot(nart, "MDUNGEON_ENCOUNTER", elements={"LOCALE": level_one_locale, "ROOM": two_to_three_room,  "STRENGTH": 150})
        
        if random.randint(1, 5) == 5:
            final_anchor = direction[0]
        else:
            final_anchor = random.choice(pbge.randmaps.anchors.ADJACENT_ANCHORS[direction[0]])

        self.add_sub_plot(nart, "DZD_RONR_BOSS",  elements={"LOCALE": level_two_locale, "ANCHOR": final_anchor})
        return True
        
    def t_ENDCOMBAT(self, camp:gears.GearHeadCampaign):
        camp.bring_out_your_dead(True)
        if camp.pc not in camp.party:
            pbge.alert("Your lance retreats...")
            camp.go(camp.home_base)

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if self.intro_ready:
            pbge.alert("Wreckage litters the highway. You come across the site of a recent battle, or more likely an ambush. There is no sign of who or what might have destroyed these mecha.")
            npc = camp.do_skill_test(gears.stats.Knowledge,  gears.stats.Scouting,  self.rank)
            if npc:
                if npc.get_pilot() is camp.pc:
                    pbge.alert("Your long range sensors are giving contradictory readings. This area of the dead zone probably has radioactive interference.")
                else:
                    ghcutscene.SimpleMonologueDisplay("[BAD_NEWS] There's a strange electromagnetic signal in this area; it's blocking our long range sensors. [WE_ARE_IN_DANGER]",  npc)(camp)
            else:
                candidates = camp.get_active_lancemates()
                if candidates:
                    ghcutscene.SimpleMonologueDisplay("[BAD_NEWS] If this attack is related to the disappearances we can assume that the attackers are nearby, and it's a safe bet they know we're here too. [WE_ARE_IN_DANGER]",  random.choice(candidates))(camp)
            self.intro_ready = False

        if camp.time > self.last_update:
            dungeonmaker.dungeon_cleaner(camp.scene)
            self.last_update = camp.time


class RoadOfNoReturnConclusion(Plot):
    # Fight some random mecha. What do they want? To pad the adventure.
    LABEL = "DZD_RONR_BOSS"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart: pbge.plots.NarrativeRequest):
        myscene = self.elements["LOCALE"]
        fac = self.elements.get("ENEMY_FACTION")
        self.register_element("ROOM", ghrooms.MechaScaleFortressRoom(random.randint(8,16), random.randint(8,16),  anchor=self.elements["ANCHOR"]), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,), faction=fac), dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank, 150, fac, myscene.environment).mecha_list
        
        myfort = self.register_element("_FORT", gears.selector.generate_fortification(self.rank, fac, myscene.environment))
        team2.contents.append(myfort)
        
        self.enemy_combatants = list(team2.contents)

        self.last_update = 0
        return True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.time

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        myteam = self.elements["_eteam"]
        myguards = myteam.get_members_in_play(camp)

        if len(myguards) < 1:
            # Win the battle! 
            self.win_the_dungeon(camp)
        else:
            myscene = self.elements["LOCALE"]
            for npc in list(self.enemy_combatants):
                npc.restore_all()
                if npc.is_operational() and npc.scale is gears.scale.MechaScale:
                    if npc not in myscene.contents:
                        myscene.contents.append(npc)
                else:
                    self.enemy_combatants.remove(npc)
                
    def win_the_dungeon(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN",  self.elements[mechadungeons.MDG_DUNGEON])
        dest_node = random.choice((self.elements["DZ_EDGE"].start_node,  self.elements["DZ_EDGE"].end_node))
        pbge.alert("When the battle ends, you find the people who had disappeared from the highway: {ENEMY_FACTION} kidnapped them and forced them to work disassembling the captured vehicles to build mecha and war machines.".format(**self.elements))
        pbge.alert("Soon, rescue teams from nearby communities arrive to provide aid to the victims. You return to {}.".format(dest_node.destination))
        self.elements["DZ_EDGE"].start_node.destination.metrodat.local_reputation += 10
        self.elements["DZ_EDGE"].end_node.destination.metrodat.local_reputation += 10
        camp.dole_xp(200)
        camp.go(dest_node.entrance)
        self.end_plot(camp)



#   *********************************
#   ***   DZD_ROADEDGE_KERBEROS   ***
#   *********************************
#

class KerberosEncounterPlot(DZDREBasicPlotWithEncounterStuff):
    LABEL = "DZD_ROADEDGE_KERBEROS"

    active = True
    scope = True
    UNIQUE = True
    BASE_RANK = 40
    ENCOUNTER_CHANCE = BASE_RANK
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleDeadzone

    def custom_init(self, nart):
        super().custom_init(nart)
        myedge = self.elements["DZ_EDGE"]
        self.add_sub_plot(nart, "DZRE_KERBEROS_ATTACKS", ident="MISSION", spstate=PlotState(
            elements={"METRO": myedge.start_node.destination.metrodat, "METROSCENE": myedge.start_node.destination,
                      "MISSION_GATE": myedge.start_node.entrance}).based_on(self))
        self._got_rumor = False
        mysp = self.add_sub_plot(
            nart,"ADD_EXPERT",elements={"METRO": myedge.start_node.destination.metrodat, "METROSCENE": myedge.start_node.destination}
        )
        self.elements["NPC"] = mysp.elements["NPC"]
        self.elements["EXPERT_LOC"] = mysp.elements["LOCALE"]
        return True

    def get_enemy_encounter(self, camp, dest_node):
        start_node = self.elements["DZ_EDGE"].get_link(dest_node)
        if start_node.pos[0] < dest_node.pos[0]:
            myanchor = pbge.randmaps.anchors.west
        else:
            myanchor = pbge.randmaps.anchors.east
        myadv = missionbuilder.BuildAMissionSeed(
            camp, "Kerberos Attacks", start_node.destination, start_node.entrance,
            enemy_faction=None, rank=self.rank,
            objectives=(dd_customobjectives.DDBAMO_KERBEROS,),
            adv_type="BAM_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": dest_node.entrance, "GOAL_SCENE": dest_node.destination,
                             "ENTRANCE_ANCHOR": myanchor,
                             missionbuilder.BAME_MONSTER_TAGS: ("ZOMBOT",)},
            scenegen=DeadZoneHighwaySceneGen,
            architecture=self.ENCOUNTER_ARCHITECTURE(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            cash_reward=0,
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            exploration_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg"
        )
        return myadv

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        if self.active and camp.has_mecha_party():
            if random.randint(1, 100) <= self.ENCOUNTER_CHANCE and not self.road_cleared:
                return self.get_enemy_encounter(camp, dest_node)
            elif random.randint(1, 100) <= 15:
                return self.get_random_encounter(camp, dest_node)

    def MISSION_WIN(self, camp):
        self.elements["DZ_EDGE"].style = self.elements["DZ_EDGE"].STYLE_SAFE
        self.road_cleared = True

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["kerberos deathworms have been sighted on the road to {}".format(
                self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        myscene = camp.scene.get_root_scene()
        myedge = self.elements["DZ_EDGE"]
        if npc is not self.elements["NPC"]:
            if myedge.start_node.destination is myscene and not self.road_cleared and not self._got_rumor:
                goffs.append(Offer(
                    msg="The Kerberos has lived here forever. No-one knows if it is one monster with many heads or many monsters acting together, but we do know it cannot be killed. You ought to ask {NPC} at {EXPERT_LOC} for more info. {NPC.gender.subject_pronoun} knows more about it than anyone else alive.".format(**self.elements),
                    context=ContextTag((context.INFO,)), effect=self._get_rumor,
                    subject="kerberos", data={"subject": "the kerberos deathworm"}, no_repeats=True
                ))
            elif myedge.end_node.destination is myscene and not self.road_cleared and not self._got_rumor:
                goffs.append(Offer(
                    msg="They're big, they're dangerous, and they can swallow a mecha whole. You should ask someone from {} if you want to know more... Usually the deathworms don't come out this far.".format(myedge.start_node.destination),
                    context=ContextTag((context.INFO,)),
                    subject="kerberos", data={"subject": "the kerberos deathworm"}, no_repeats=True
                ))
        return goffs

    def _get_rumor(self, camp):
        self._got_rumor = True
        self.memo = Memo("{NPC} at {EXPERT_LOC} knows more about the Kerberos Deathworm than anyone else.".format(**self.elements),
                         self.elements["EXPERT_LOC"])

    def NPC_offers(self, camp):
        mylist = list()
        if self.road_cleared:
            if camp.campdata.get(KERBEROS_DEFEATED):
                mylist.append(Offer(
                    msg="Kerberos has left this region, and it may be many years before he returns. Let's hope that he doesn't hold a grudge.",
                    context=ContextTag((context.INFO,)),
                    data={"subject": "Kerberos."}, no_repeats=True
                ))

            else:
                mylist.append(Offer(
                    msg="Kerberos has left this region, seeking greener pastures elsewhere.",
                    context=ContextTag((context.INFO,)),
                    data={"subject": "Kerberos."}, no_repeats=True
                ))

        else:
            mylist.append(Offer(
                msg="Kerberos is one of the old gods of the deadzone. In these parts he is regarded as a force of nature, one with the ashes and the sky.",
                context=ContextTag((context.CUSTOM,)),
                subject="kerberos", subject_start=True,
                data={"reply": "I heard that you know a lot about Kerberos."}, no_repeats=True
            ))

            mylist.append(Offer(
                msg="He has been here for longer than the wastes themselves. Many see Kerberos as a deity of both creation and destruction- he destroys, but life springs anew wherever he goes.",
                context=ContextTag((context.CUSTOMREPLY,)),
                subject="kerberos",
                data={"reply": 'What do you mean "old god of the deadzone"?'}, no_repeats=True
            ))

            mylist.append(Offer(
                msg="You don't. Kerberos knows all that passes above the sand. Instead, you must allow Kerberos to find you.",
                context=ContextTag((context.CUSTOMREPLY,)),
                subject="kerberos",
                data={"reply": "How can I find Kerberos?"}, no_repeats=True
            ))

            mylist.append(Offer(
                msg="That is impossible. Kerberos is a force of nature; do you think your guns could halt a typhoon? In the past there were people who could speak to Kerberos, but that knowledge has been lost.",
                context=ContextTag((context.CUSTOMREPLY,)),
                subject="kerberos",
                data={"reply": "How do I kill Kerberos?"}, no_repeats=True
            ))

        return mylist


class KerberosAttacks(Plot):
    LABEL = "DZRE_KERBEROS_ATTACKS"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        self.kerberos_active = True

        # Add the Kerberos interior dungeon
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], "Kerberos Facility", gharchitecture.OrganicBuilding(),
            self.rank,
            monster_tags=("MUTANT", "VERMIN", "SYNTH", "CREEPY"),
            explo_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            connector=plotutility.StairsDownToStairsUpConnector,
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS,),
            decor=gharchitecture.OrganicStructureDecor()
        )
        self.register_element("DUNGEON_ENTRANCE", mydungeon.entry_level)
        d_entrance_room = self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(12, 12))
        mydungeon.entry_level.contents.append(d_entrance_room)

        myent = self.register_element(
            "ENTRANCE", game.content.ghwaypoints.StairsUp(
                anchor=pbge.randmaps.anchors.middle,
                dest_wp=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        # Add the kidnap room and kidnap room waypoint.
        d_kidnap_room = self.register_element("KIDNAP_ROOM", pbge.randmaps.rooms.OpenRoom(12, 12))
        mydungeon.entry_level.contents.append(d_kidnap_room)
        self.register_element("KIDNAP_ROOM_WP", pbge.scenes.waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="KIDNAP_ROOM")
        self.register_element("KIDNAP_TEAM", game.teams.Team(), dident="KIDNAP_ROOM")
        self.kidnapped_pilots = list()

        #d_kidnap_room.contents.append(ghwaypoints.PZHolo())

        nart.camp.campdata["KERBEROS_GRAB_FUN"] = self._get_grabbed_by_kerberos
        nart.camp.campdata["KERBEROS_DUNGEON_OPEN"] = False

        # Add the lore bits. In this case, biomachines that might reveal Kerberos's purpose.
        lore_room = pbge.randmaps.rooms.OpenRoom(5,5,parent=random.choice(mydungeon.levels))
        #lore_room = pbge.randmaps.rooms.OpenRoom(10, 10, parent=mydungeon.entry_level)
        biomachine = self.register_element(
            "BIOMACHINE", ghwaypoints.OrganicTube(
                name="Bioprocessor", plot_locked=True,
                desc="A biomechanical tube extends from the ceiling of this chamber to the floor."
            )
        )
        lore_room.contents.append(biomachine)

        # Add the boss room.
        d_boss_level = self.register_element("BOSS_LEVEL", mydungeon.goal_level)
        d_boss_room = self.register_element("BOSS_ROOM", pbge.randmaps.rooms.OpenRoom(10,10), dident="BOSS_LEVEL")
        self.add_sub_plot(nart, "DZRE_KERBEROS_BOSSFIGHT", ident="BOSSFIGHT")

        self.intro_ready = True

        return True

    def _get_grabbed_by_kerberos(self, camp: gears.GearHeadCampaign, pc):
        camp.scene.contents.remove(pc)
        pilot = pc.get_pilot()
        if pilot is camp.pc:
            camp.go(self.elements["KIDNAP_ROOM_WP"])
            camp.campdata["KERBEROS_DUNGEON_OPEN"] = True
        else:
            plotutility.AutoLeaver(pilot)(camp)
            self.elements["DUNGEON_ENTRANCE"].deploy_team([pilot,],self.elements["KIDNAP_TEAM"])
            self.kidnapped_pilots.append(pilot)

    def MISSION_GATE_menu(self, camp, thingmenu):
        if camp.campdata["KERBEROS_DUNGEON_OPEN"]:
            thingmenu.add_item("Go to the Kerberos Facility.", self.go_to_locale)

    def BIOMACHINE_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if camp.party_has_skill(gears.stats.Biotechnology) or camp.party_has_skill(gears.stats.Science):
            thingmenu.desc = "{} It seems to be a detoxification processor; perhaps Kerberos has been removing contaminants from the soil it consumes.".format(thingmenu.desc)
        else:
            thingmenu.desc = "{} It seems to be digesting something.".format(thingmenu.desc)

    def BOSSFIGHT_WIN(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)

    def go_to_locale(self, camp):
        camp.go(self.elements["ENTRANCE"])

    def t_START(self, camp):
        if self.intro_ready and camp.scene is self.elements["DUNGEON_ENTRANCE"]:
            pbge.alert("You are dropped into a deep underground chamber. You're not sure whether this is inside Kerberos or some adjoining complex.")
            self.intro_ready = False
        if self.elements["ENTRANCE"].dest_wp is not self.elements["MISSION_GATE"]:
            print("Fixing Kerberos dungeon...")
            self.elements["ENTRANCE"].dest_wp = self.elements["MISSION_GATE"]


KERBEROS_DEFEATED = "KERBEROS_DEFEATED"


class KerberosBossFight(Plot):
    LABEL = "DZRE_KERBEROS_BOSSFIGHT"
    active = True
    scope = "BOSS_LEVEL"
    UNIQUE = True

    def custom_init(self, nart):
        myscene = self.elements["BOSS_LEVEL"]
        myteam = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="BOSS_ROOM")
        mycompy = self.register_element("_core", gears.selector.get_design_by_full_name("K1 Bio-Computer"), dident="_eteam")
        serv1 = self.register_element("_serv1", gears.selector.get_design_by_full_name("Servitor"), dident="_eteam")
        serv2 = self.register_element("_serv2", gears.selector.get_design_by_full_name("Servitor"), dident="_eteam")
        serv1.colors = (gears.color.Twilight,gears.color.Black,gears.color.Black,gears.color.Black,gears.color.Black)
        serv2.colors = (gears.color.Saffron,gears.color.Black,gears.color.Black,gears.color.Black,gears.color.Black)

        self.holo_unlocked = False
        holoroom = self.register_element("_holoroom", pbge.randmaps.rooms.OpenRoom(5, 5), dident="BOSS_LEVEL")
        myholo = self.register_element("HOLO", ghwaypoints.PZHolo(name="Holodisplay", plot_locked=True, anchor=pbge.randmaps.anchors.middle, desc="You stand before a PreZero holographic display. You have no idea what information, if any, it was meant to communicate."),
                                       dident="_holoroom")

        return True

    def HOLO_BUMP(self, camp: gears.GearHeadCampaign):
        if not self.holo_unlocked:
            mypc = camp.do_skill_test(gears.stats.Knowledge, gears.stats.Biotechnology, self.rank, no_random=True)
            if mypc:
                if mypc == camp.pc:
                    pbge.alert("Your knowledge of PreZero technology allows you to recognize this machine as a PreZero computer interface. It shows this area as it existed before the Night of Fire, and traces Kerberos's route along what is now the highway.")
                else:
                    SimpleMonologueDisplay("I know what this is... it's an oldtype computer display. This hologram shows the megacity that used to exist around {METROSCENE}... Here you can see the path that Kerberos was supposed to take through the service tunnels.".format(**self.elements), mypc)(camp)
                    SimpleMonologueDisplay("Except, there are no service tunnels anymore. This area is the highway, now. Maybe we could use this computer to send Kerberos on a different path, one far away from human beings.", mypc)(camp, False)
                self.unlock_holo()
            else:
                mypc = camp.do_skill_test(gears.stats.Knowledge, gears.stats.Wildcraft, self.rank, no_random=True)
                if mypc:
                    if mypc == camp.pc:
                        pbge.alert("You quickly recognize the shifting geometric forms of this holographic display as the geological features of this area. The top layer must be the city as it existed before the Night of Fire, and the red path can only be Kerberos's route along what is now the highway.")
                    else:
                        SimpleMonologueDisplay("I don't know exactly what kind of machine this is, but I can tell you what it's showing- that's {METROSCENE}, or at least it's what {METROSCENE} was back when this was built.".format(**self.elements), mypc)(camp)
                        SimpleMonologueDisplay("I'd guess this line going through it is Kerberos's path. You see this valley? That's part of the highway now, and that's where we got attacked. Maybe we can use this to tell Kerberos where to go...", mypc)(camp, False)
                    self.unlock_holo()
                else:
                    mypc = camp.do_skill_test(gears.stats.Knowledge, gears.stats.Scouting, self.rank, difficulty=gears.stats.DIFFICULTY_HARD, no_random=True)
                    if mypc:
                        if mypc == camp.pc:
                            pbge.alert("It takes a minute before you realize that the holographic display is a map of the surrounding area. Of course, it's not the area as you know it today- this is how things were before the Night of Fire. Maybe you can use this to send Kerberos away.")
                        else:
                            SimpleMonologueDisplay("I can't believe it- this is a PreZero map of the area around {METROSCENE}! I've heard about holographic map projectors like this but this is my first time seeing one in the reals.".format(**self.elements), mypc)(camp)
                            SimpleMonologueDisplay("If I'm reading this right, this red line should be where Kerberos is going, and you can see how it intersects with where the highway passes through now. I wonder if we can use this to send Kerberos somewhere else?", mypc)(camp, False)
                        self.unlock_holo()

    def HOLO_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if self.holo_unlocked:
            thingmenu.add_item("Do nothing.", None)
            thingmenu.add_item("Redirect Kerberos.", self.redirect_monster)

    def redirect_monster(self, camp):
        camp.check_trigger("WIN", self)
        BiotechDiscovery(
            camp, "There is a huge subterranean biotech complex near {}.".format(self.elements["METROSCENE"]),
            "[THATS_INTERESTING] I'll get one of our hazmat recovery teams to check it out. Here is the {cash} you've earned.",
            self.rank
        )
        self.elements["_eteam"].make_allies(self.elements["BOSS_LEVEL"].player_team)
        pbge.alert(
            "At first, nothing happens. Slowly the red line begins to move away from the highway and you hear a low rumbling in the distance. It seems to have worked.")
        self.end_plot(camp)

    def unlock_holo(self):
        self.holo_unlocked = True
        self.elements["HOLO"].desc = "You stand before a PreZero holographic display. You can use it to send Kerberos away from the highway."
        self.elements["_eteam"].make_allies(self.elements["BOSS_LEVEL"].player_team)

    def t_COMBATROUND(self, camp: gears.GearHeadCampaign):
        mycompy: gears.base.Prop = self.elements["_core"]
        serv1: gears.base.Monster = self.elements["_serv1"]
        serv2: gears.base.Monster = self.elements["_serv2"]

        if mycompy.is_destroyed() and not (serv1.is_destroyed() and serv2.is_destroyed()):
            # If you destroy the compy before the servitors, it gets repaired.
            mycompy.restore_all()
            pbge.my_state.view.play_anims(gears.geffects.BiotechnologyAnim(pos=mycompy.pos))

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        mycompy: gears.base.Prop = self.elements["_core"]
        serv1: gears.base.Monster = self.elements["_serv1"]
        serv2: gears.base.Monster = self.elements["_serv2"]

        if mycompy.is_destroyed() and serv1.is_destroyed() and serv2.is_destroyed():
            pbge.alert("As the biocomputer dies, the chamber is shaken by a powerful rumble. The tremors last for a short time before fading into silence. Whatever just happened, you assume that Kerberos will no longer trouble travelers on the highway.")
            camp.check_trigger("WIN", self)
            BiotechDiscovery(
                camp, "There is a huge subterranean biotech complex near {}.".format(self.elements["METROSCENE"]),
                "[THATS_INTERESTING] I'll get one of our hazmat recovery teams to check it out. Here is the {cash} you've earned.",
                self.rank
            )
            camp.campdata[KERBEROS_DEFEATED] = True
            self.end_plot(camp)



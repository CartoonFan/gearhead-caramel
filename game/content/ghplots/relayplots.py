from typing import override
from pbge.plots import Plot, Rumor, PlotState, Adventure
import gears
import pbge
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from . import missionbuilder
from game import content
from game.content import gharchitecture
from pbge.memos import Memo


#   **********************
#   ***   INFO_RELAY   ***
#   **********************
#
#  METROSCENE: The next location in the relay.
#  INFO: An InfoRelayTracker object. When the last info is passed a WIN trigger is called.
#  ALLIED_FACTION: The faction providing the information. May be None.
#  ENEMY_FACTION: The faction seeking to hide the information. May be None.
#

class InfoRelayTracker:
    def __init__(self, subject, info_list):
        self.subject = subject
        self.info_list = list(info_list)

    @override
    def __str__(self) -> str:
        return str(self.subject)

    @property
    def text(self):
        if len(self.info_list) > 0:
            return str(self.info_list[0])
        else:
            return "Whoops empty info tracker; this is a bug"

    def pop(self, camp, plot):
        if len(self.info_list) > 1:
            self.info_list.pop(0)
            pstate = PlotState(adv=plot.adv, elements={"METROSCENE": plot.elements["NEXT_METROSCENE"]}, rank=plot.rank+2).based_on(plot)
            _ = content.load_dynamic_plot(camp, "INFO_RELAY", pstate)
        else:
            camp.check_trigger("WIN", self)
        plot.end_plot(camp, True)



class TalkRelay(Plot):
    LABEL = "INFO_RELAY"
    scope = True
    active = True

    @staticmethod
    def is_bad_character(plot, camp, npc):
        return bool(npc.faction and camp.are_faction_allies(npc, plot.elements.get("ENEMY_FACTION"))) or npc.scene.get_metro_scene() is not plot.elements["METROSCENE"]

    RUMOR = Rumor(
        "{NPC} knows something about {INFO}",
        offer_msg="If you want to know more, speak to {NPC} at {NPC_SCENE}.",
        offer_subject="{NPC} knows something about",
        offer_subject_data="{NPC} and {INFO}",
        memo="{NPC} at {NPC_SCENE} knows something about {INFO}.",
        prohibited_npcs=("NPC",), npc_is_prohibited_fun=is_bad_character
    )

    @override
    def custom_init(self, nart):
        self.fight_ready = bool(self.elements["ENEMY_FACTION"])
        self.memo = Memo("You should travel to {METROSCENE} to learn more about {INFO}.".format(**self.elements), self.elements["METROSCENE"])
        npc = gears.selector.random_character(
            self.rank, camp=nart.camp, faction=self.elements.get("ALLIED_FACTION")
        )
        _ = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"],
                          backup_seek_func=self._is_okay_scene)
        _ = self.register_element("NPC", npc, dident="NPC_SCENE", lock=True)

        _ = self.seek_element(nart, "NEXT_METROSCENE", self._is_best_next, backup_seek_func=self._is_okay_next)

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_MEETING in candidate.attributes)

    def _is_okay_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _is_best_next(self, nart, candidate):
        return (
            isinstance(candidate, gears.GearHeadScene) and candidate is not self.elements["METROSCENE"] and 
            hasattr(candidate, "metrodat") and 
            gears.tags.SCENE_PUBLIC in candidate.attributes and gears.tags.CITY_UNINHABITED not in candidate.attributes
            and not nart.camp.are_faction_enemies(candidate, self.elements["ALLIED_FACTION"])
            )

    def _is_okay_next(self, nart, candidate):
        return (
            isinstance(candidate, gears.GearHeadScene) and candidate is not self.elements["METROSCENE"] and 
            hasattr(candidate, "metrodat") and gears.tags.SCENE_PUBLIC in candidate.attributes
            )

    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "[HELLO] I hear you've been asking about {INFO}.".format(**self.elements),
            context=ContextTag([context.HELLO,])
        ))

        myinfo = self.elements["INFO"]
        if len(myinfo.info_list) > 1:
            mylist.append(Offer(
                "[THIS_IS_A_SECRET] {INFO.text}; you can learn more in {NEXT_METROSCENE}.".format(**self.elements),
                context=ContextTag([context.INFO,]), effect=self._get_info,
                data={"subject": str(self.elements["INFO"]), "stuff": str(self.elements["INFO"])},
                no_repeats=True
            ))

        else:
            mylist.append(Offer(
                "[I_KNOW_THINGS_ABOUT_STUFF] {INFO.text}.".format(**self.elements),
                context=ContextTag([context.INFO,]), effect=self._get_info,
                data={"subject": str(self.elements["INFO"]), "stuff": str(self.elements["INFO"])},
                no_repeats=True
            ))

        return mylist

    def _get_info(self, camp: gears.GearHeadCampaign):
        myinfo = self.elements["INFO"]
        myinfo.pop(camp, self)

    def generate_world_map_encounter(self, camp: gears.GearHeadCampaign, metroscene, return_wp, dest_scene, dest_wp,
                                     scenegen=gharchitecture.DeadZoneHighwaySceneGen,
                                     architecture=gharchitecture.MechaScaleSemiDeadzone,
                                     **kwargs):
        if self.fight_ready and dest_scene is self.elements["METROSCENE"]:
            myanchor = kwargs.get("entrance_anchor", None)
            if not myanchor:
                myanchor = pbge.randmaps.anchors.east
            myrank = self.rank
            dest_metro = dest_scene.get_metro_scene()
            myadv = missionbuilder.BuildAMissionSeed(
                camp, "{} Ambush".format(dest_scene), metroscene, return_wp,
                enemy_faction=self.elements.get("ENEMY_FACTION"), rank=myrank,
                objectives=(missionbuilder.BAMO_DEFEAT_BLOCKADE,),
                adv_type="BAM_ROAD_MISSION",
                custom_elements={"ADVENTURE_GOAL": dest_wp, "DEST_SCENE": dest_scene, "ENTRANCE_ANCHOR": myanchor},
                scenegen=scenegen,
                architecture=architecture(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
                cash_reward=0,
                mission_grammar=missionbuilder.MissionGrammar(
                    objective_ep="prevent you from investigating {INFO}".format(**self.elements),
                    objective_pp="get to {}".format(dest_scene),
                    win_pp="I got past your lance",
                    win_ep="you fought your way into {}".format(dest_scene),
                    lose_pp="you stopped me from entering {}".format(dest_scene),
                    lose_ep="I drove you away from {}".format(dest_scene)
                ), on_win=self._win_combat, make_enemies=False
            )
            myadv.priority = 55
            myadv.mandatory = True
            return myadv

    def _win_combat(self, camp):
        self.fight_ready = False

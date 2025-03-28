
import collections
import pbge
import gears
from .. import exploration

from . import ghterrain
from . import ghwaypoints
from . import ghcutscene
from . import backstory
from . import ghrooms
from . import ghchallenges
from . import megaprops


# The list of plots will be stored as a dictionary based on label.
PLOT_LIST = collections.defaultdict( list )
UNSORTED_PLOT_LIST = list()

class GHNarrativeRequest(pbge.plots.NarrativeRequest):
    def __init__(self, camp: gears.GearHeadCampaign, *args, **kwargs):
        self.challenges = camp.get_challenges_needing_plots()
        super().__init__(camp, *args, **kwargs)

from . import ghplots

from game.content.ghplots import dd_combatmission, dd_homebase, dd_main, mocha, harvest
from . import plotutility
from . import dungeonmaker

from . import adventureseed
from . import missiontext




def narrative_convenience_function( pc_egg, adv_type="SCENARIO_DEADZONEDRIFTER" ):
#def narrative_convenience_function(adv_type="SCENARIO_MOCHA"):
    # Start an adventure.
    camp = gears.GearHeadCampaign(name=str(pc_egg.pc),explo_class=exploration.Explorer,egg=pc_egg)
    init = pbge.plots.PlotState(rank=1, adv=pbge.plots.Adventure(world=camp))
    nart = GHNarrativeRequest(camp,init,adv_type,PLOT_LIST)
    if nart.story:
        nart.build()
        return nart.camp
    else:
        for e in nart.errors:
            print(e)


def load_dynamic_plot(camp: gears.GearHeadCampaign, adv_type, pstate):
    if not pstate:
        pstate = pbge.plots.PlotState(rank=1)
    nart = GHNarrativeRequest(camp,pstate,adv_type,PLOT_LIST)
    if nart.story:
        nart.build()
        camp.check_trigger("UPDATE")
        return nart.story


def test_mocha_encounters():
    frontier = list()
    possible_states = list()
    move_cost = collections.defaultdict(int)
    for p in PLOT_LIST['MOCHA_MINTRO']:
        frontier.append(p.CHANGES)

    while frontier:
        current = frontier.pop()
        possible_states.append(current)
        # Find the neighbors
        for p in PLOT_LIST['MOCHA_MENCOUNTER']:
            if all( p.REQUIRES[k] == current.get(k,0) for k in p.REQUIRES.keys() ):
                dest = current.copy()
                dest.update(p.CHANGES)
                new_cost = move_cost[repr(current)] + 1
                if new_cost <= 2 and ( repr(dest) not in move_cost or new_cost < move_cost[repr(dest)] ):
                    move_cost[repr(dest)] = new_cost
                    frontier.append(dest)
    # Finally, print an analysis.
    print("Possible States: {}".format(possible_states))
    done_stuff = set()
    for s in possible_states:
        if move_cost[repr(s)] < 2:
            ec = (mocha.ENEMY, s.get(mocha.ENEMY, 0), mocha.COMPLICATION, s.get(mocha.COMPLICATION, 0))
            EnemyComp = [p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                         if s.get(mocha.ENEMY, 0) == p.REQUIRES.get(mocha.ENEMY, 0)
                         and mocha.ENEMY in p.REQUIRES
                         and mocha.COMPLICATION in p.REQUIRES
                         and s.get(mocha.COMPLICATION, 0) == p.REQUIRES.get(mocha.COMPLICATION, 0)]
            if ec not in done_stuff and not EnemyComp:
                print("No encounter found for Enemy:{} Complication:{}".format(ec[1],ec[3]))
            done_stuff.add(ec)

            es = (mocha.ENEMY, s.get(mocha.ENEMY, 0), mocha.STAKES, s.get(mocha.STAKES, 0))
            EnemyStakes = [p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                           if s.get(mocha.ENEMY, 0) == p.REQUIRES.get(mocha.ENEMY, 0)
                           and mocha.ENEMY in p.REQUIRES
                           and mocha.STAKES in p.REQUIRES
                           and s.get(mocha.STAKES, 0) == p.REQUIRES.get(mocha.STAKES, 0)]
            if es not in done_stuff and not EnemyStakes:
                print("No encounter found for Enemy:{} Stakes:{}".format(es[1],es[3]))
            done_stuff.add(es)

            cs = (mocha.COMPLICATION, s.get(mocha.COMPLICATION, 0), mocha.STAKES, s.get(mocha.STAKES, 0))
            CompStakes = [p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                          if s.get(mocha.COMPLICATION, 0) == p.REQUIRES.get(mocha.COMPLICATION, 0)
                          and mocha.COMPLICATION in p.REQUIRES
                          and mocha.STAKES in p.REQUIRES
                          and s.get(mocha.STAKES, 0) == p.REQUIRES.get(mocha.STAKES, 0)]
            if cs not in done_stuff and not CompStakes:
                print("No encounter found for Complication:{} Stakes:{}".format(cs[1],cs[3]))
            done_stuff.add(cs)

    for s in possible_states:
        if move_cost[repr(s)] >= 2:
            choices = [ p for p in PLOT_LIST['MOCHA_MHOICE'] if all( p.REQUIRES[k] == s.get(k,0) for k in p.REQUIRES.keys() )]
            if len(choices) < 4:
                print("Only {} choices for {}".format(len(choices),s))

from . import ghplots

def test_roadedge_missions():
    frontier = list()
    possible_states = list()
    move_cost = collections.defaultdict(int)
    for p in PLOT_LIST['DZRE_InvaderProblem'] + PLOT_LIST["DZRE_BanditProblem"]:
        frontier.append({ghplots.dd_roadedge_propp.E_MOTIVE:p.STARTING_MOTIVE,
                         ghplots.dd_roadedge_propp.E_ACE:p.STARTING_ACE,
                         ghplots.dd_roadedge_propp.E_TOWN:p.STARTING_TOWN})

    while frontier:
        current = frontier.pop()
        if current not in possible_states:
            possible_states.append(current)
        # Find the neighbors
        for p in PLOT_LIST['DZRE_ACE_TOWN'] + PLOT_LIST['DZRE_MOTIVE_TOWN'] + PLOT_LIST['DZRE_MOTIVE_ACE']:
            if all( p.REQUIRES[k] == current.get(k,0) for k in p.REQUIRES.keys() ):
                dest = current.copy()
                dest.update(p.CHANGES)
                new_cost = move_cost[repr(current)] + 1
                if new_cost <= 3 and ( repr(dest) not in move_cost or new_cost < move_cost[repr(dest)] ):
                    move_cost[repr(dest)] = new_cost
                    frontier.append(dest)
    # Finally, print an analysis.
    print("Number of Possible States: {}".format(len(possible_states)))
    print("Possible States: {}".format(possible_states))
    done_stuff = set()
    for s in possible_states:
        if move_cost[repr(s)] < 3:
            num_plots_for_s = 0
            pat = [p for p in PLOT_LIST['DZRE_ACE_TOWN'] if all(p.REQUIRES[k] == s.get(k, 0) for k in p.REQUIRES.keys())]
            if not pat and (s[ghplots.dd_roadedge_propp.E_ACE], s[
                ghplots.dd_roadedge_propp.E_TOWN]) not in done_stuff:
                print("No missions for Ace: {} Town: {}".format(s[ghplots.dd_roadedge_propp.E_ACE], s[
                    ghplots.dd_roadedge_propp.E_TOWN]))
                done_stuff.add((s[ghplots.dd_roadedge_propp.E_ACE], s[
                    ghplots.dd_roadedge_propp.E_TOWN]))

            pat = [p for p in PLOT_LIST['DZRE_MOTIVE_TOWN'] if all(p.REQUIRES[k] == s.get(k, 0) for k in p.REQUIRES.keys())]
            if not pat and (s[ghplots.dd_roadedge_propp.E_MOTIVE], s[
                ghplots.dd_roadedge_propp.E_TOWN]) not in done_stuff:
                print("No missions for Motive: {} Town: {}".format(s[ghplots.dd_roadedge_propp.E_MOTIVE], s[
                    ghplots.dd_roadedge_propp.E_TOWN]))
                done_stuff.add((s[ghplots.dd_roadedge_propp.E_MOTIVE], s[
                    ghplots.dd_roadedge_propp.E_TOWN]))

            pat = [p for p in PLOT_LIST['DZRE_MOTIVE_ACE'] if all(p.REQUIRES[k] == s.get(k, 0) for k in p.REQUIRES.keys())]
            if not pat and (s[ghplots.dd_roadedge_propp.E_MOTIVE], s[
                ghplots.dd_roadedge_propp.E_ACE]) not in done_stuff:
                print("No missions for Motive: {} Ace: {}".format(s[ghplots.dd_roadedge_propp.E_MOTIVE], s[
                    ghplots.dd_roadedge_propp.E_ACE]))
                done_stuff.add((s[ghplots.dd_roadedge_propp.E_MOTIVE], s[
                    ghplots.dd_roadedge_propp.E_ACE]))


#test_roadedge_missions()
#test_mocha_encounters()

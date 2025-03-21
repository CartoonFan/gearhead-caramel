import gears
from pbge.plots import Plot, PlotState
import pbge
import random
from game.content.ghwaypoints import Exit
from game.content.plotutility import AdventureModuleData

# Room tags
ON_THE_ROAD = "ON_THE_ROAD"  # This location is connected to the highway, if appropriate.

ONAWA_FOUND_EVIDENCE = "ONAWA_FOUND_EVIDENCE"


class DeadzoneDrifterStub(Plot):
    LABEL = "SCENARIO_DEADZONEDRIFTER"
    active = True
    scope = True
    # Creates a DeadZone Drifter adventure.
    # - Start by creating the "home base" city that the player character will leave from.

    ADVENTURE_MODULE_DATA = AdventureModuleData(
        "DeadZone Drifter",
        "The village you've been defending needs a power station. Getting them a new one will require questing from one end of the deadzone to the other.",
        (158, 3, 5), "VHS_DeadZoneDrifter.png",
    )

    def custom_init(self, nart):
        """Load the features."""
        self.add_sub_plot(nart, "CF_STANDARD_LANCEMATE_HANDLER")
        self.add_sub_plot(nart, "CF_WORLD_MAP_ENCOUNTER_HANDLER")

        """Create the intro/tutorial."""
        wplot = self.add_first_locale_sub_plot(nart, locale_type="DZD_INTRO", ident="INTRO")

        self.ADVENTURE_MODULE_DATA.apply(nart.camp)

        # Copy over the sheriff and the name of the town
        self.register_element("DZ_CONTACT", wplot.elements["SHERIFF"])
        self.register_element("DZ_TOWN_NAME", wplot.elements["DZ_TOWN_NAME"])

        mymap = self.register_element("DZ_ROADMAP", RoadMap())
        mymap.initialize_plots(self, nart)

        # Add Wujung and the rest of the world.
        # self.add_sub_plot(nart,"DZD_HOME_BASE",ident="HOMEBASE")

        # Add an egg lancemate, if possible.
        # This gets called last to prevent major NPCs who are used elsewhere in the plot from showing up here.
        self.add_sub_plot(nart, "ADD_INSTANT_EGG_LANCEMATE", necessary=False)

        self.current_memo = 0

        return True

    def t_INTRO_END(self, camp):
        # Wujung should be registered as the home base, so send the player there.
        camp.go(camp.home_base)
        npc = self.elements["DZ_CONTACT"]
        npc.place(camp.campdata["DISTANT_TOWN"], team=camp.campdata["DISTANT_TEAM"])

        del self.subplots["INTRO"]

    def t_CHEATINGFUCKINGBASTARD(self, camp):
        mymap = self.elements["DZ_ROADMAP"]
        for e in mymap.edges:
            e.style = e.STYLE_SAFE

    MEMO_MESSAGES = (
        "{DZ_CONTACT} sent you to Wujung to hire a team of lancemates and find someone who can help rebuild the power station in {DZ_TOWN_NAME}. Osmund Eumann at the Bronze Horse Inn should be able to help.",
        "According to Osmund Eumann, you should be able to find someone who can rebuild the power station at Long Haul Logistics in Wujung.",
        "{DZ_CONTACT} sent you to find someone to rebuild {DZ_TOWN_NAME}'s power station. RegEx Construction in Wujung has agreed, but before they can do so you will need to clear a safe pathway through the dead zone."

    )

    def t_START(self, camp):
        camp.check_trigger("UPDATE")
        if "INITIAL_QOL" not in camp.campdata:
            total_qol = 0
            mymap = self.elements["DZ_ROADMAP"]
            for n in mymap.nodes:
                if n.destination and hasattr(n.destination, "metrodat") and n.destination.metrodat:
                    total_qol += n.destination.metrodat.get_quality_of_life_index()
            camp.campdata["INITIAL_QOL"] = total_qol

        if camp.campdata.get("next_adv_memo", 0) > self.current_memo:
            self.current_memo = camp.campdata["next_adv_memo"]
            if self.current_memo <= len(self.MEMO_MESSAGES):
                self.memo = self.MEMO_MESSAGES[self.current_memo - 1].format(**self.elements)
            else:
                # Memos are over.
                self.memo = None

    def t_UPDATE(self, camp):
        if camp.campdata.get("next_adv_memo", 0) > self.current_memo:
            self.current_memo = camp.campdata["next_adv_memo"]
            if self.current_memo <= len(self.MEMO_MESSAGES):
                self.memo = self.MEMO_MESSAGES[self.current_memo - 1].format(**self.elements)
            else:
                # Memos are over.
                self.memo = None

    def __setstate__(self, state):
        # For saves from V0.930 or earlier, make sure there's memo state info.
        super().__setstate__(state)
        if "current_memo" not in state:
            self.current_memo = 1
            self.memo = self.MEMO_MESSAGES[0].format(**self.elements)


class RoadNode(object):
    # A node in the RoadMap graph; represents a town or other visitable location.
    # The sub plot loaded by a node gets the DZ_ROADMAP and DZ_NODE elements, and must define
    # its own LOCALE and ENTRANCE elements.
    FRAME_WUJUNG = 0
    FRAME_TOWN = 1
    FRAME_VILLAGE = 2
    FRAME_DISTANT_TOWN = 3
    FRAME_MINE = 4
    FRAME_DANGER = 5

    def __init__(self, sub_plot_label, sub_plot_ident=None, pos=(0, 0), visible=False, discoverable=True, frame=1):
        self.sub_plot_label = sub_plot_label
        self.sub_plot_ident = sub_plot_ident
        self.pos = pos
        self.visible = visible
        self.discoverable = discoverable
        self.frame = frame
        self.destination = None
        self.entrance = None

    def __str__(self):
        return str(self.destination)


class RoadEdge(object):
    # The sub plot loaded by an edge gets the DZ_ROADMAP and DZ_EDGE elements.
    STYLE_SAFE = 1
    STYLE_RED = 2
    STYLE_ORANGE = 3
    STYLE_YELLOW = 4
    STYLE_BLOCKED = 5

    def __init__(self, start_node=None, end_node=None, sub_plot_label=None, sub_plot_ident=None, visible=False,
                 discoverable=True, style=1):
        self.start_node = start_node
        self.end_node = end_node
        self.sub_plot_label = sub_plot_label
        self.sub_plot_ident = sub_plot_ident
        self.visible = visible
        self.discoverable = discoverable
        self.path = list()
        self.style = style
        self.eplot = None

    def get_link(self, node_a):
        # If node_a is one of the nodes for this edge, return the other node.
        if node_a is self.start_node:
            return self.end_node
        elif node_a is self.end_node:
            return self.start_node

    def get_city_link(self, city_a):
        # If node_a is one of the nodes for this edge, return the other node.
        if city_a is self.start_node.destination:
            return self.end_node.destination
        elif city_a is self.end_node.destination:
            return self.start_node.destination

    def connects_to(self, some_node):
        return some_node is self.start_node or some_node is self.end_node

    def connects_to_city(self, some_city):
        return some_city is self.start_node.destination or some_city is self.end_node.destination

    def get_menu_fun(self, camp: gears.GearHeadCampaign, node_a):
        if self.eplot:
            myadv = self.eplot.get_road_adventure(camp, node_a)
            if myadv:
                return myadv
        if node_a is self.start_node:
            return self.go_to_start_node
        else:
            return self.go_to_end_node

    def go_to_end_node(self, camp):
        camp.go(self.end_node.entrance)

    def go_to_start_node(self, camp):
        camp.go(self.start_node.entrance)


class RoadMap(object):
    MAP_WIDTH = 20
    MAP_HEIGHT = 10

    def __init__(self, ):
        self.nodes = list()
        self.edges = list()
        self.start_node = RoadNode("DZD_DISTANT_TOWN", "GOALTOWN", visible=True, frame=RoadNode.FRAME_DISTANT_TOWN)
        self.add_node(self.start_node, random.randint(3, 4), random.randint(2, 7))

        self.end_node = RoadNode("DZD_HOME_BASE", "HOMEBASE", visible=True, frame=RoadNode.FRAME_WUJUNG)
        self.add_node(self.end_node, self.MAP_WIDTH - 1, self.MAP_HEIGHT // 2 - 1)

        north_road = list()
        north_edges = list()
        prev = self.start_node
        ys = list(range(0, 4))
        random.shuffle(ys)
        for t in range(3):
            north_road.append(RoadNode("DZD_ROADSTOP", visible=False))
            self.add_node(north_road[-1], t * 4 + random.randint(5, 7), ys[t])
            new_edge = RoadEdge()
            self.connect_nodes(prev, north_road[-1], new_edge)
            north_edges.append(new_edge)
            prev = north_road[-1]
        self.connect_nodes(prev, self.end_node, RoadEdge())

        south_road = list()
        south_edges = list()
        prev = self.start_node
        ys = list(range(5, 9))
        random.shuffle(ys)
        for t in range(3):
            south_road.append(RoadNode("DZD_ROADSTOP", visible=False))
            self.add_node(south_road[-1], t * 4 + random.randint(5, 7), ys[t])
            new_edge = RoadEdge()
            self.connect_nodes(prev, south_road[-1], new_edge)
            south_edges.append(new_edge)
            prev = south_road[-1]
        self.connect_nodes(prev, self.end_node, RoadEdge())

        cross_road = RoadEdge(sub_plot_label="DZD_ROADEDGE_ROADOFNORETURN")
        self.connect_nodes(random.choice(north_road), random.choice(south_road), cross_road)

        # At this point we have all the main locations joined. Gonna sort roads according to "westerliness"
        # and assign difficulty ratings based on that.
        sorted_edges = list(self.edges)
        random.shuffle(
            sorted_edges)  # Why shuffle before sort? So that if two edges have identical scores, one won't be favored over the other.
        sorted_edges.sort(key=lambda e: e.start_node.pos[0] + e.end_node.pos[0])
        for edg in sorted_edges:
            if sorted_edges.index(edg) < max(len(sorted_edges) // 3, 2):
                edg.style = RoadEdge.STYLE_RED
                if not edg.sub_plot_label:
                    edg.sub_plot_label = "DZD_ROADEDGE_RED"
            elif sorted_edges.index(edg) < len(sorted_edges) * 2 // 3:
                edg.style = RoadEdge.STYLE_ORANGE
                if not edg.sub_plot_label:
                    edg.sub_plot_label = "DZD_ROADEDGE_ORANGE"
            else:
                edg.style = RoadEdge.STYLE_YELLOW
                if not edg.sub_plot_label:
                    edg.sub_plot_label = "DZD_ROADEDGE_YELLOW"

        # The Kerberos plot always happens on one of the two roads leading into the goal town.
        k_edge = random.choice((north_edges[0], south_edges[0]))
        k_edge.sub_plot_label = "DZD_ROADEDGE_KERBEROS"

    def add_node(self, node_to_add, x, y):
        self.nodes.append(node_to_add)
        node_to_add.pos = (min(max(0, x), self.MAP_WIDTH - 1), min(max(0, y), self.MAP_HEIGHT - 1))

    def connect_nodes(self, start_node, end_node, edge_to_use):
        self.edges.append(edge_to_use)
        edge_to_use.start_node = start_node
        edge_to_use.end_node = end_node
        edge_to_use.path = pbge.scenes.animobs.get_line(start_node.pos[0], start_node.pos[1], end_node.pos[0],
                                                        end_node.pos[1])

    def connection_is_made(self):
        # Sooner or later.
        # Return True if there's a STYLE_SAFE connection from self.start_node to self.end_node
        visited_nodes = set()
        frontier = [edge.end_node for edge in self.edges if
                    edge.start_node is self.start_node and edge.style is edge.STYLE_SAFE]
        while frontier:
            nu_start = frontier.pop()
            visited_nodes.add(nu_start)
            for e in self.edges:
                if e.style is e.STYLE_SAFE and e.connects_to(nu_start):
                    nu_end = e.get_link(nu_start)
                    if nu_end not in visited_nodes:
                        frontier.append(nu_end)
        return self.end_node in visited_nodes

    def initialize_plots(self, plot, nart):
        """

        :type plot: Plot
        """
        ok = True
        towns = list()
        for n in self.nodes:
            if n.sub_plot_label:
                ok = plot.add_sub_plot(nart, n.sub_plot_label, ident=n.sub_plot_ident,
                                       spstate=PlotState(rank=60 - n.pos[0] * 3, elements={"DZ_NODE": n}).based_on(
                                           plot))
                if ok:
                    n.destination = ok.elements["LOCALE"]
                    n.entrance = ok.elements["ENTRANCE"]
                    if "DZ_NODE_FRAME" in ok.elements:
                        n.frame = ok.elements["DZ_NODE_FRAME"]
                    towns.append(n)
                else:
                    break
        for e in self.edges:
            if e.sub_plot_label:
                ok = plot.add_sub_plot(nart, e.sub_plot_label, ident=e.sub_plot_ident,
                                       spstate=PlotState(elements={"DZ_EDGE": e}).based_on(plot))
                if ok:
                    e.eplot = ok
                    if "DZ_EDGE_STYLE" in ok.elements:
                        e.style = ok.elements["DZ_EDGE_STYLE"]
                else:
                    break
        if towns:
            # Add the randomly-positioned content.
            # Onawa's gonna need a list of all the towns, so copy a list for her now.
            all_towns = list(towns)

            # Find a town for Ran Magnus Mecha Works. Ideally this should be far from Wujung.
            towns.sort(key=lambda x: x.pos[0])
            mytown = towns[min(random.randint(1, len(towns) - 2), random.randint(1, len(towns) - 2))]
            towns.remove(mytown)
            plot.add_sub_plot(nart, "DZD_MAGNUSMECHA",
                              elements={"METROSCENE": mytown.destination, "METRO": mytown.destination.metrodat})

            random.shuffle(towns)
            mytown = towns.pop()
            plot.add_sub_plot(
                nart, "DZD_OMEGA1004",
                elements={"METROSCENE": mytown.destination, "METRO": mytown.destination.metrodat}
            )

            mytown = towns.pop()
            random.shuffle(all_towns)
            all_towns.remove(mytown)
            plot.add_sub_plot(
                nart, "DZD_ONAWA_MYSTERY",
                elements={"METROSCENE": mytown.destination, "METRO": mytown.destination.metrodat,
                          "MISSION_GATE": mytown.entrance, "TOWNS": all_towns}
            )

        return ok

    def expand_roadmap_menu(self, camp, mymenu):
        # Determine which edges connect here.
        my_edges = [e for e in self.edges if e.get_link(mymenu.waypoint.node) and (e.visible or e.discoverable)]
        for e in my_edges:
            mydest = e.get_link(mymenu.waypoint.node)
            e.visible = True
            mydest.visible = True
            mymenu.add_item("Go to {}".format(mydest), e.get_menu_fun(camp, mydest), e)


class DZDRoadMapMenu(pbge.rpgmenu.Menu):
    WIDTH = 640
    HEIGHT = 320
    MAP_AREA = pbge.frects.Frect(-320, -210, 640, 320)
    MENU_AREA = pbge.frects.Frect(-200, 130, 400, 80)

    def __init__(self, camp, wp):
        super(DZDRoadMapMenu, self).__init__(self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h,
                                             border=None, predraw=self.pre)
        self.desc = wp.desc
        self.waypoint = wp
        self.map_sprite = pbge.image.Image("dzd_roadmap.png")
        self.legend_sprite = pbge.image.Image("dzd_roadmap_legend.png", 20, 20)
        self.road_sprite = pbge.image.Image("dzd_roadmap_roads.png", 34, 34)
        self.text_labels = dict()

    def _calc_map_x(self, x, map_rect):
        return x * 32 + 16 + map_rect.x

    def _calc_map_y(self, y, map_rect):
        return y * 32 + 16 + map_rect.y

    def _get_text_label(self, mynode):
        if mynode in self.text_labels:
            return self.text_labels[mynode]
        else:
            mylabel = pbge.SMALLFONT.render(str(mynode), True, (0, 0, 0))
            self.text_labels[mynode] = mylabel
            return mylabel

    EDGEDIR = {
        (-1, -1): 0, (0, -1): 1, (1, -1): 2,
        (-1, 0): 3, (1, 0): 4,
        (-1, 1): 5, (0, 1): 6, (1, 1): 7
    }

    def _draw_edge(self, myedge, map_rect, hilight=False):
        a = myedge.path[0]
        if hilight:
            style = 0
        else:
            style = myedge.style
        for b in myedge.path[1:]:
            center_x = (self._calc_map_x(a[0], map_rect) + self._calc_map_x(b[0], map_rect)) // 2
            center_y = (self._calc_map_y(a[1], map_rect) + self._calc_map_y(b[1], map_rect)) // 2
            frame = self.EDGEDIR.get((b[0] - a[0], b[1] - a[1]), 0) + style * 8
            self.road_sprite.render_c((center_x, center_y), frame)
            a = b

    def pre(self):
        if pbge.my_state.view:
            pbge.my_state.view()
        pbge.default_border.render(self.MENU_AREA.get_rect())
        my_map_rect = self.MAP_AREA.get_rect()
        self.map_sprite.render(my_map_rect, 0)
        active_item_edge = self.get_current_item().desc

        for myedge in self.waypoint.roadmap.edges:
            if myedge.visible and myedge is not active_item_edge:
                self._draw_edge(myedge, my_map_rect)
        if active_item_edge:
            self._draw_edge(active_item_edge, my_map_rect, True)

        for mynode in self.waypoint.roadmap.nodes:
            dest = (self._calc_map_x(mynode.pos[0], my_map_rect), self._calc_map_y(mynode.pos[1], my_map_rect))
            if mynode.visible:
                if (active_item_edge and active_item_edge.connects_to(mynode)) or (mynode.entrance is self.waypoint):
                    self.legend_sprite.render_c(dest, mynode.frame)
                else:
                    self.legend_sprite.render_c(dest, mynode.frame + 10)
                mylabel = self._get_text_label(mynode)
                texdest = mylabel.get_rect(center=(dest[0], dest[1] + 16))
                pbge.my_state.screen.blit(mylabel, texdest.clamp(my_map_rect))

        pbge.notex_border.render(self.MAP_AREA.get_rect())
        # pbge.draw_text( pbge.my_state.medium_font, self.desc, self.TEXT_RECT.get_rect(), justify = 0 )


class DZDRoadMapExit(Exit):
    MENU_CLASS = DZDRoadMapMenu

    def __init__(self, roadmap, node, **kwargs):
        self.roadmap = roadmap
        self.node = node
        super(DZDRoadMapExit, self).__init__(**kwargs)

    def unlocked_use(self, camp):
        rpm = self.MENU_CLASS(camp, self)

        # Add the roadmap menu items
        self.roadmap.expand_roadmap_menu(camp, rpm)

        # Add the plot-linked menu items
        camp.expand_puzzle_menu(self, rpm)
        rpm.add_item("[Cancel]", None)
        fx = rpm.query()
        if fx:
            camp.time += 1
            fx(camp)

    def bump(self, camp, pc):
        # Send a BUMP trigger.
        camp.check_trigger("BUMP", self)
        # This waypoint doesn't care about plot locking; it's always plot locked.
        self.unlocked_use(camp)

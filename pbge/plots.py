import random
from . import dialogue
from .memos import Memo


class PlotError(Exception):
    """Plot init will call this if initialization impossible."""
    pass


class Adventure(object):
    """ An adventure links a group of plots together."""

    def __init__(self, name="Generic Adventure", world=None):
        self.name = name
        self.world = world
        self.ended = False

    def end_adventure(self, camp):
        # WARNING: Don't end the plot while the PC is standing in one of the temp scenes!
        # Ending an adventure is best done when the PC leaves the adventure.
        for p in list(camp.all_plots()):
            if p.adv is self:
                p.end_plot(camp, total_removal=False)
        self.ended = True
        camp.check_trigger("UPDATE")
        camp.check_trigger("END", self)

    def __str__(self):
        return self.name


class PlotState(object):
    """For passing state information to subplots."""

    def __init__(self, adv=None, rank=None, elements=None):
        self.adv = adv
        self.rank = rank
        if elements:
            self.elements = elements.copy()
        else:
            self.elements = dict()

    def based_on(self, oplot, update_elements=None):
        self.adv = self.adv or oplot.adv
        self.rank = self.rank or oplot.rank
        # Only copy over the elements not marked as private.
        for k, v in oplot.elements.items():
            if isinstance(k, str) and len(k) > 0 and k[0] != "_":
                if k not in self.elements:
                    self.elements[k] = v
        if update_elements:
            self.elements.update(update_elements)
        # Why return self? Because this function will often be called straight
        # from the generator.
        return self


class RumorMemoEffect(object):
    def __init__(self, memo, plot, extra_effect=None):
        self.memo = memo
        self.plot = plot
        self.extra_effect = extra_effect

    def __call__(self, camp):
        self.plot.memo = self.memo
        self.plot._rumor_memo_delivered = True
        if self.extra_effect:
            self.extra_effect(camp)


class Rumor(object):
    """A grammar item that comes with an info offer that can set a memo."""

    def __init__(self, rumor="", grammar_tag="[News]", offer_context=dialogue.INFO,
                 offer_msg="", offer_subject="{NPC}", offer_subject_data="{NPC}", memo="",
                 memo_location="NPC_SCENE", prohibited_npcs=(), offer_effect_name="",
                 npc_is_prohibited_fun=None):
        # offer_effect_name is the name of a method from the calling plot with signature (camp). Use a regular method
        #  and that signature will be (self, camp).
        # npc_is_prohibited_fun is an optional function that will prohibit certain npcs from sharing this rumor
        #  if it returns True. The function signature is (plot, camp, npc).
        self.rumor = rumor
        self.grammar_tag = grammar_tag
        self.offer_msg = offer_msg
        self.offer_context = dialogue.ContextTag([offer_context, ])
        self.offer_subject = offer_subject
        self.offer_subject_data = offer_subject_data
        self.memo = memo
        self.memo_location = memo_location
        self.prohibited_npcs = prohibited_npcs
        self.offer_effect_name = offer_effect_name
        self.npc_is_prohibited_fun = npc_is_prohibited_fun

    def get_rumor_grammar(self, npc, camp, plot):
        mygram = dict()
        if self.npc_is_ok(npc, camp, plot) and not plot._rumor_memo_delivered:
            mygram[self.grammar_tag] = [self.rumor.format(**plot.elements), ]
        return mygram

    def get_rumor_offers(self, npc, camp, plot):
        myoffers = list()
        if self.offer_effect_name and hasattr(plot, self.offer_effect_name):
            effect = getattr(plot, self.offer_effect_name)
        else:
            effect = None
        if self.npc_is_ok(npc, camp, plot) and self.offer_msg and not plot._rumor_memo_delivered:
            myoffer = dialogue.Offer(
                self.offer_msg.format(**plot.elements),
                context=self.offer_context,
                subject=self.offer_subject.format(**plot.elements), no_repeats=True,
                data={"subject": self.offer_subject_data.format(**plot.elements)},
                effect=effect
            )
            if self.memo:
                myoffer.effect = RumorMemoEffect(
                    Memo(self.memo.format(**plot.elements), plot.elements.get(self.memo_location)), plot, effect
                )
            myoffers.append(myoffer)
        return myoffers

    def npc_is_ok(self, npc, camp, plot):
        # Return True if this NPC can tell this rumor.
        for ename in self.prohibited_npcs:
            if plot.elements.get(ename, None) is npc:
                return False
        if self.npc_is_prohibited_fun and self.npc_is_prohibited_fun(plot, camp, npc):
            return False
        return True

    def disable_rumor(self, plot):
        plot._rumor_memo_delivered = True


class TimeExpiration(object):
    def __init__(self, camp, time_limit=10):
        self.time_limit = camp.time + time_limit

    def __call__(self, camp, plot):
        return camp.time > self.time_limit


class Plot(object):
    """The building block of the adventure."""
    LABEL = ""
    UNIQUE = False
    COMMON = False
    rank = 1
    # You are free to set active manually, but it's better to use the
    # activate and deactivate functions, which trigger an UPDATE. I would set this property to private but
    # do you have any idea how much of a pain in the arse that would be? A big pain in the arse. That's how much.
    active = False

    _used = 0

    # Scope determines from where the event scripts in this plot will be called.
    # If scope is the element ID of a scene, then this plot's scripts will only
    # be triggered from within that scene.
    # If scope is True, then this plot is global, and its scripts will be
    # triggered no matter where the party happens to be.
    # If scope is None, then this plot will get thrown away after the narrative
    # gets built and its scripts will never be called.
    # Also note that self.active must be True for scripts to be triggered.
    scope = None

    RUMOR = None

    # expiration, if it exists, is a callable with signature (camp, plot) that returns True if this plot should
    # be ended.
    expiration = None

    memo = None

    def __init__(self, nart, pstate: PlotState):
        """Initialize + install this plot, or raise PlotError"""
        # nart = The Narrative object
        # pstate = The current plot state
        # New in v0.960: extensions! A list of extra bits that can add memos and other stuff.

        # Inherit the plot state.
        self.adv = pstate.adv
        self.rank = pstate.rank or self.rank
        self.elements = pstate.elements.copy()
        self.subplots = dict()
        self.extensions = list()

        # Increment the usage count, for getting info on plot numbers!
        self.__class__._used += 1

        # The move_records are stored in case this plot gets removed.
        self.move_records = list()

        # Independent plots will not get deleted if this one ends.
        self.indie_plots = list()

        # The temp_scenes list contains scenes that get removed if this plot ends.
        self._temp_scenes = list()

        # The locked elements set contains element IDs of elements this plot doesn't want other plots to touch.
        self.locked_elements = set()

        # The call_on_end list contains functions that should be called when this plot ends.
        self.call_on_end = list()

        # Record the rumor status
        self._rumor_memo_delivered = False

        # Do the custom initialization
        allok = self.custom_init(nart)

        # If failure, delete currently added subplots + raise error.
        if not allok:
            self.fail(nart)
        elif self.UNIQUE:
            nart.camp.uniques.add(self.__class__)

    def fail(self, nart):
        self.remove(nart)
        raise PlotError(str(self.__class__))

    def get_element_idents(self, ele):
        """Return list of element idents assigned to this object."""
        return [key for key, value in list(self.elements.items()) + list(self.subplots.items()) if value is ele]

    def add_sub_plot(self, nart, splabel, spstate=None, ident=None, necessary=True, elements=None, indie=False, rank=None):
        if not spstate:
            spstate = PlotState().based_on(self)
        if not ident:
            ident = "_autoident_{0}".format(len(self.subplots))
        if elements:
            spstate.elements.update(elements)
        if rank:
            spstate.rank = rank
        sp = nart.generate_sub_plot(spstate, splabel)
        if necessary and not sp:
            # print "Fail: {}".format(splabel)
            self.fail(nart)
        elif sp:
            if indie:
                self.indie_plots.append(sp)
            else:
                self.subplots[ident] = sp
        return sp

    def add_first_locale_sub_plot(self, nart, locale_type="CITY_SCENE", ident=None):
        # Utility function for a frequently used special case.
        sp = self.add_sub_plot(nart, locale_type, ident=ident)
        if sp:
            self.register_element("LOCALE", sp.elements.get("LOCALE"))
            nart.camp.go(sp.elements.get("ENTRANCE"))
        return sp

    def place_element(self, ele, dest):
        # Record when a plot places an element; if this plot is removed, the
        # element will be removed from its location as well.
        if hasattr(ele, "container") and ele.container:
            ele.container.remove(ele)
        dest.contents.append(ele)
        self.move_records.append((ele, dest.contents))

    def register_element(self, ident, ele, dident=None, lock=False):
        # dident is an element itent for this element's destination.
        if not ident:
            ident = "_autoelement_{0}_{1}".format(len(self.elements), hash(ele))
        self.elements[ident] = ele
        if dident:
            mydest = self.elements.get(dident)
            if mydest:
                self.place_element(ele, mydest)
        if lock:
            self.locked_elements.add(ident)
        return ele

    def seek_element_candidates(self, nart, seek_func, scope=None, check_subscenes=True, backup_seek_func=None):
        if not scope:
            scope = nart.camp
        candidates = list()
        bu_candidates = list()
        for e in nart.camp.all_contents(scope, check_subscenes, check_temp_scenes=False):
            if seek_func(nart, e):
                candidates.append(e)
            elif backup_seek_func and backup_seek_func(nart, e):
                bu_candidates.append(e)
        if candidates or bu_candidates:
            mylocked = nart.camp.get_all_locked_elements()
            for le in mylocked:
                if le and le in candidates:
                    candidates.remove(le)
                elif le and le in bu_candidates:
                    bu_candidates.remove(le)
        return candidates or bu_candidates

    def seek_element(self, nart, ident, seek_func, scope=None, must_find=True, check_subscenes=True, lock=False,
                     backup_seek_func=None):
        """Check scope and all children for a gear that seek_func returns True"""
        candidates = self.seek_element_candidates(nart, seek_func, scope, check_subscenes, backup_seek_func)
        if candidates:
            e = random.choice(candidates)
            self.register_element(ident, e, lock=lock)
            return e
        elif must_find:
            self.fail(nart)

    def get_locked_elements(self):
        mylist = list()
        for le in self.locked_elements:
            mylist.append(self.elements.get(le, None))
        return mylist

    def register_scene(self, nart, myscene, mygen, ident=None, dident=None, rank=None, temporary=False):
        # temporary scenes will be deleted when this plot ends. Use this feature responsibly!
        # If you create a permanent waypoint door to a temporary scene, the door's link to the scene will
        # keep that scene alive even after deletion, but the scene's contents and scripts will be gone.
        # Best bet is to link temporary scenes to the permanent parts of the campaign using something that will
        # disappear when this plot ends, such as a conversation option or a waypoint menu item.
        if not (dident and self.elements.get(dident)):
            if self.adv and self.adv.world:
                self.adv.world.contents.append(myscene)
                self.move_records.append((myscene, self.adv.world.contents))
            else:
                nart.camp.contents.append(myscene)
                self.move_records.append((myscene, nart.camp.contents))
        self.register_element(ident, myscene, dident)
        nart.generators.append(mygen)
        self.move_records.append((mygen, nart.generators))
        myscene.rank = rank or self.rank
        if temporary:
            self._temp_scenes.append(myscene)
            myscene.is_temporary = True
        return myscene

    def custom_init(self, nart):
        """Return True if everything ok, or False otherwise."""
        return True

    def remove(self, nart=None):
        """Remove this plot, including subplots and new elements, from narrative request."""
        # First, remove all subplots.
        for sp in self.subplots.values():
            sp.remove(nart)
        for sp in self.indie_plots:
            sp.remove(nart)
        # Next, remove any elements created by this plot.
        if hasattr(self, "move_records"):
            for e, d in self.move_records:
                if e in d:
                    d.remove(e)

        self.__class__._used += -1

        # Remove self from the adventure.
        if hasattr(self, "container") and self.container:
            self.container.remove(self)

        # Remove self from the uniques set, if necessary.
        if nart and self.UNIQUE and self.__class__ in nart.camp.uniques:
            nart.camp.uniques.remove(self.__class__)

    def install(self, nart):
        """Plot generation complete. Mesh plot with campaign."""
        for sp in self.subplots.values():
            sp.install(nart)
        for sp in self.indie_plots:
            sp.install(nart)
        del self.move_records
        del self.indie_plots
        if self.scope:
            dest = self.elements.get(self.scope)
            if dest and hasattr(dest, "scripts"):
                dest.scripts.append(self)
            else:
                nart.camp.scripts.append(self)

    def get_all_plots(self):
        yield self
        for sp in self.subplots.values():
            yield sp.get_all_plots()

    def display(self, lead=""):
        print(lead + str(self.__class__))
        for sp in self.subplots.values():
            sp.display(lead + " ")

    def handle_trigger(self, camp, trigger, thing=None):
        """A trigger has been tripped; make this plot react if appropriate."""
        # The trigger handler will be a method of this plot. If a thing is
        # involved, and that thing is an element, the handler's id will be

        # "[element ident]_[trigger type]". If no thing is involved, the
        # trigger handler will be "t_[trigger type]".
        # Trigger handler methods take the Exploration as a parameter.
        if thing:
            if thing is self:
                handler = getattr(self, "SELF_{0}".format(trigger), None)
                if handler:
                    handler(camp)
            idlist = self.get_element_idents(thing)
            for label in idlist:
                handler = getattr(self, "{0}_{1}".format(label, trigger), None)
                if handler:
                    handler(camp)
        else:
            handler = getattr(self, "t_{0}".format(trigger), None)
            if handler:
                handler(camp)

    def get_dialogue_offers(self, npc, camp):
        """Get any dialogue offers this plot has for npc."""
        # Method [ELEMENTID]_offers will be called. This method should return a
        # list of offers to be built into the conversation.
        ofrz = self._get_generic_offers(npc, camp)
        npc_ids = self.get_element_idents(npc)
        for i in npc_ids:
            ogen = getattr(self, "{0}_offers".format(i), None)
            if ogen:
                ofrz += ogen(camp)
        if self.RUMOR:
            ofrz += self.RUMOR.get_rumor_offers(npc, camp, self)
        return ofrz

    def modify_puzzle_menu(self, camp, thing, thingmenu):
        """Modify the thingmenu based on this plot."""
        # Method [ELEMENTID]_menu will be called with the camp, menu as parameters.
        # This method should modify the menu as needed- typically by altering
        # the "desc" property (menu caption) and adding menu items.
        thing_ids = self.get_element_idents(thing)
        for i in thing_ids:
            ogen = getattr(self, "{0}_menu".format(i), None)
            if ogen:
                ogen(camp, thingmenu)

    def modify_cutscene(self, camp, csplan):
        pass

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        return list()

    def get_dialogue_grammar(self, npc, camp):
        """Return any grammar rules appropriate to this situation."""
        # The public face of this method- will gather grammar from the rumor and custom function. Maybe even other
        # places! I dunno...
        mygram = dict()
        if self.RUMOR:
            rgram = self.RUMOR.get_rumor_grammar(npc, camp, self)
            mygram.update(rgram)
        ogram = self._get_dialogue_grammar(npc, camp)
        if ogram:
            mygram.update(ogram)
        return mygram

    def _get_dialogue_grammar(self, npc, camp):
        # The secret private function that returns custom grammar.
        return None

    @classmethod
    def matches(cls, pstate: PlotState):
        """Returns True if this plot matches the current plot state."""
        return True

    def activate(self, camp):
        was_active = self.active
        self.active = True
        if not was_active:
            camp.check_trigger('UPDATE')

    def deactivate(self, camp):
        was_active = self.active
        self.active = False
        if was_active:
            camp.check_trigger('UPDATE')

    def end_plot(self, camp, total_removal=False):
        # WARNING: Don't end the plot while the PC is standing in one of the temp scenes!
        # Ending an adventure is best done when the PC leaves the adventure.
        # NOTE: Depending on how the plot is ended, this method might be called several times.
        #  Better it be called too often than not to be called at all. Just keep it in mind.
        was_active = self.active
        self.active = False
        for sp in self.subplots.values():
            if total_removal or not sp.active:
                sp.end_plot(camp, total_removal)

        # Remove self from the adventure.
        if hasattr(self, "container") and self.container:
            self.container.remove(self)

        # Remove any temporary scenes.
        for s in self._temp_scenes:
            s.end_scene(camp)

        # Call the call-on-end functions.
        for coef in self.call_on_end:
            coef(camp)

        if was_active:
            camp.check_trigger('UPDATE')

    def update(self, camp):
        if self.expiration and self.expiration(camp, self):
            self.end_plot(camp)

    def __setstate__(self, state):
        # For saves from V0.800 or earlier, make sure there's a _rumor_memo_delivered var.
        if "_rumor_memo_delivered" not in state:
            self._rumor_memo_delivered = False
        if "extensions" not in state:
            self.extensions = list()
        self.__dict__.update(state)


class NarrativeRequest(object):
    """The builder class which constructs a story out of individual plots."""

    def __init__(self, camp, pstate=None, adv_type="ADVENTURE_STUB", plot_list={}):
        self.camp = camp
        self.generators = list()
        self.errors = list()
        self.plot_list = plot_list
        # Add the seed plot.
        if pstate:
            self.story = self.generate_sub_plot(pstate, adv_type)

    def random_choice_by_weight(self, candidates):
        wcan = list()
        for sp in candidates:
            if sp.UNIQUE:
                wcan.append(sp)
            elif sp.COMMON:
                wcan += (sp, sp, sp, sp, sp, sp)
            else:
                wcan += (sp, sp, sp)
        return random.choice(wcan)

    def generate_sub_plot(self, pstate, label):
        """Locate a plot which matches the request, init it, and return it."""
        # Create a list of potential plots.
        candidates = list()
        for sp in self.plot_list[label]:
            if sp.matches(pstate):
                if not sp.UNIQUE or sp not in self.camp.uniques:
                    candidates.append(sp)
        if candidates:
            cp = None
            while candidates and not cp:
                cpc = self.random_choice_by_weight(candidates)
                candidates.remove(cpc)
                try:
                    cp = cpc(self, pstate)
                except PlotError:
                    cp = None
            if not cp:
                self.errors.append("No plot accepted for {0}".format(label))
            return cp
        else:
            self.errors.append("No plot found for {0}".format(label))

    def get_map_generator(self, gb):
        # I thought that generators should be changed to a dict, but then I
        # noticed that the generator also gets recorded in a plot's move_records.
        # So, changing it to a dict would require a workaround for that.
        # For now I'm just going to leave this inefficiency in.
        mygen = None
        for mg in self.generators:
            if mg.gb == gb:
                mygen = mg
                break
        return mygen

    def build(self):
        """Build finished campaign from this narrative."""
        for g in self.generators:
            g.make()
        self.story.install(self)

from . import varwidgets, conditionals, statefinders, worldmapeditor
import pbge
import gears
import copy


class BaseVariableDefinition(object):
    WIDGET_TYPE = None
    DEFAULT_VAR_TYPE = "integer"

    def __init__(self, default_val=0, var_type=None, must_be_defined=False, tooltip="", **kwargs):
        # if must_be_defined is True, this scenario won't compile if the variable is undefined.
        if isinstance(default_val, dict):
            self.default_val = dict()
            self.default_val.update(default_val)
        else:
            self.default_val = default_val
        self.var_type = var_type or self.DEFAULT_VAR_TYPE
        self.must_be_defined = must_be_defined
        self.tooltip = tooltip
        self.data = kwargs.copy()

    def get_widgets(self, part, key, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(self.WIDGET_TYPE(part, key, tooltip=self.tooltip, **kwargs))
        return mylist

    def get_errors(self, part, key):
        # Return a list of strings if there are errors with this variable.
        myerrors = list()
        if self.must_be_defined:
            uvals = part.get_ultra_vars()
            if key not in uvals or not uvals[key]:
                myerrors.append("Variable {} in {} needs a value".format(key, part))
        return myerrors

    @staticmethod
    def format_for_python(value):
        return value


class StringVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "string"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget


class StringLiteralVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "literal"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget

    @staticmethod
    def format_for_python(value):
        return repr(value)


class StringIdentifierVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "identifier"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        myval = part.get_ultra_vars().get(key, "")
        if not isinstance(myval, str) or not myval.isidentifier():
            myerrors.append("Variable {} in {} is not a valid identifier".format(key, part))

        return myerrors


class IntegerVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "integer"
    WIDGET_TYPE = varwidgets.StringVarEditorWidget

    @staticmethod
    def format_for_python(value):
        try:
            return int(value)
        except ValueError:
            print("Value error: not an int")
            return 0

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        myval = part.get_ultra_vars().get(key, "")
        try:
            int(myval)
        except ValueError:
            myerrors.append("Variable {} in {} is not an integer".format(key, part))

        return myerrors


class FiniteStateVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "list"
    WIDGET_TYPE = varwidgets.FiniteStateEditorWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        my_names_and_states = statefinders.get_possible_states(part, part.brick.vars[key].var_type)
        mystates = [a[1] for a in my_names_and_states]
        mystates.append(None)
        myval = part.get_ultra_vars().get(key, "")
        if myval not in mystates:
            myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors

class InteriorDecorVariable(FiniteStateVariable):
    DEFAULT_VAR_TYPE = "interior_decor"

    def get_errors(self, part, key):
        myerrors = list()
        myval = part.raw_vars.get(key, "")
        if not statefinders.is_legal_state(part, self.DEFAULT_VAR_TYPE, myval):
            myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors

    @staticmethod
    def format_for_python(value):
        if value and value != "None":
            return "{}()".format(value)
        else:
            return "None"


class MajorNPCIDVariable(FiniteStateVariable):
    DEFAULT_VAR_TYPE = "major_npc_id"
    WIDGET_TYPE = varwidgets.FiniteStateEditorWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)

        if not myerrors:
            for bp in part.get_all_blueprints():
                if bp is not part:
                    for k,v in bp.brick.vars.items():
                        if v.var_type == self.DEFAULT_VAR_TYPE and bp.raw_vars[k] == part.raw_vars[key]:
                            myerrors.append("Error: Major NPC {} is used twice.".format(v))
                            break
        return myerrors


class DoorSignVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "door_sign"
    WIDGET_TYPE = varwidgets.FiniteStateEditorWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        my_names_and_states = statefinders.get_possible_states(part, part.brick.vars[key].var_type)
        mystates = [a[1] for a in my_names_and_states]
        mystates.append(None)
        myval = part.raw_vars.get(key, "")
        if myval not in mystates:
            myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors

    @staticmethod
    def format_for_python(value):
        if value and value != "None":
            return "(ghterrain.{0}East, ghterrain.{0}South)".format(value)
        else:
            return None



class FiniteStateListVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "list"
    WIDGET_TYPE = varwidgets.AddRemoveFSOptionsWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        if part.brick.vars[key].var_type.startswith("list:"):
            mytype = part.brick.vars[key].var_type[5:]
        else:
            mytype = part.brick.vars[key].var_type

        my_names_and_states = statefinders.get_possible_states(part, mytype)
        mystates = [a[1] for a in my_names_and_states]
        mystates.append(None)
        mylist = part.get_ultra_vars().get(key, "")
        for myval in mylist:
            if myval not in mystates:
                myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors


class SceneTagListVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "scene_tags"
    WIDGET_TYPE = varwidgets.AddRemoveFSOptionsWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        my_names_and_states = statefinders.get_possible_states(part, self.DEFAULT_VAR_TYPE)
        mystates = [a[1] for a in my_names_and_states]
        mylist = part.raw_vars.get(key, [])
        for myval in mylist:
            if myval not in mystates:
                myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors

    @staticmethod
    def format_for_python(value):
        return "[{}]".format(", ".join([str(v) for v in value]))


class PaletteVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "palette"
    WIDGET_TYPE = varwidgets.PaletteEditorWidget

    def __init__(self, default_val=0, var_type=None, must_be_defined=False, **kwargs):
        try:
            if isinstance(default_val, list) and len(default_val) == 5 and all(
                    [issubclass(p, gears.color.GHGradient) for p in default_val]):
                self._default_val = default_val
            else:
                self._default_val = None
        except TypeError:
            self._default_val = None
        self.var_type = var_type or self.DEFAULT_VAR_TYPE
        self.data = kwargs.copy()
        self.must_be_defined = must_be_defined
        self.tooltip = None

    @property
    def default_val(self):
        if self._default_val:
            return self._default_val
        else:
            return [gears.SINGLETON_REVERSE[c] for c in gears.color.random_building_colors()]

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        mylist = part.raw_vars.get(key, "")
        # mylist = part.get_ultra_vars().get(key, "")
        if not isinstance(mylist, list):
            myerrors.append("Variable {} in {} is not a color list".format(key, part))
        elif len(mylist) < 5:
            myerrors.append("Variable {} in {} has wrong number of colors for a color list".format(key, part))
        elif not all([p in gears.SINGLETON_TYPES for p in mylist]):
            myerrors.append("Variable {} in {} has unknown colors: {}".format(key, part, mylist))

        return myerrors

    @staticmethod
    def format_for_python(value):
        return "(gears.color.{}, gears.color.{}, gears.color.{}, gears.color.{}, gears.color.{})".format(*value)


class MusicVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "music"
    WIDGET_TYPE = varwidgets.MusicEditorWidget

    @classmethod
    def format_for_python(cls, value):
        if value:
            return repr(value)


class ConditionalVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "conditional"

    def get_widgets(self, part, key, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()

        mylist.append(pbge.widgets.LabelWidget(0, 0, 300, pbge.SMALLFONT.get_linesize(), key, font=pbge.SMALLFONT))

        my_conditions = part.raw_vars.get(key, list())
        for t, item in enumerate(my_conditions):
            if isinstance(item, list):
                # This is an expression.
                mylist.append(varwidgets.ConditionalExpressionEditor(part, key, t, refresh_fun))
            else:
                # This must be a boolean operator.
                mylist.append(varwidgets.BooleanOperatorEditor(part, key, t, refresh_fun))

        mylist.append(pbge.widgets.LabelWidget(
            0, 0, 100, 0, "Add Expression", draw_border=True, on_click=self.add_expression,
            data={"part": part, "key": key, "refresh_fun": refresh_fun}
        ))

        return mylist

    def add_expression(self, wid, ev):
        part = wid.data["part"]
        key = wid.data["key"]
        refresh_fun = wid.data["refresh_fun"]
        my_conditions = part.raw_vars.get(key, list())
        if not isinstance(my_conditions, list):
            my_conditions = list()
            part.raw_vars[key] = my_conditions
        if my_conditions:
            my_conditions.append(conditionals.CONDITIONAL_BOOL_OPS[0])
        my_conditions.append(conditionals.generate_new_conditional_expression(
            conditionals.CONDITIONAL_EXPRESSION_OPS[2]
        ))
        refresh_fun()

    @staticmethod
    def format_for_python(value):
        return conditionals.build_conditional(value)


class DialogueDataVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "dialogue_data"
    WIDGET_TYPE = varwidgets.DialogueOfferDataWidget


class DialogueContextVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "dialogue_context"

    def get_widgets(self, part, key, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(
            varwidgets.DialogueContextWidget(
                part, key, lambda v: statefinders.CONTEXT_INFO[v].desc,
                refresh_fun=refresh_fun
            )
        )
        return mylist


class BooleanVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "boolean"
    WIDGET_TYPE = varwidgets.BoolEditorWidget

    def get_widgets(self, part, key, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(
            self.WIDGET_TYPE(part, key, bool(part.raw_vars.get(key)))
        )
        return mylist

    @staticmethod
    def format_for_python(value):
        try:
            return bool(value)
        except ValueError:
            print("Value error: not an bool")
            return False


class CampaignVariableVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "campaign_variable"
    WIDGET_TYPE = varwidgets.CampaignVarNameWidget

    @staticmethod
    def format_for_python(value):
        return repr(value)


class TextVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "text"
    WIDGET_TYPE = varwidgets.TextVarEditorWidget

    def get_widgets(self, part, key, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(
            self.WIDGET_TYPE(part, key, str(part.raw_vars.get(key)))
        )
        return mylist

    @staticmethod
    def format_for_python(value):
        return repr(value)


class WorldMapDataVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "world_map_data"

    def __init__(self, default_val, **kwargs):
        super().__init__(default_val, **kwargs)

    def get_default_val(self):
        return {"node": {"pos": [0, 0]}, "edges": []}

    def set_default_val(self, new_value):
        pass

    default_val = property(get_default_val, set_default_val)

    def get_widgets(self, part, key, editor=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        if part.raw_vars.get("entrance_world_map"):
            mylist.append(
                pbge.widgets.LabelWidget(0, 0, 350, 0, "Open World Map Editor", font=pbge.MEDIUMFONT, draw_border=True,
                                         on_click=self._open_world_map_editor, data=(part, key, editor))
            )
        return mylist

    def _open_world_map_editor(self, wid, ev):
        part, key, editor = wid.data
        map_bp = None
        for c in editor.mytree.children:
            if c.brick.name == "New World Map" and worldmapeditor.world_map_id(c) == part.raw_vars["entrance_world_map"]:
                map_bp = c
                break
        # We now have enough information to open up the world map editor.
        worldmapeditor.WorldMapEditor.create_and_invoke(pbge.my_state.view, editor, map_bp)

    def _node_parameters_ok(self, node_dict):
        if "pos" not in node_dict:
            return False
        for k,v in node_dict.items():
            if k == "pos":
                if not(isinstance(v, (list, tuple)) and len(v) == 2 and all([isinstance(a, int) for a in v])):
                    return False
            elif k == "image_file":
                if not(isinstance(v, str) and v.endswith(".png") and v in pbge.image.glob_images("wm_legend_*.png")):
                    return False
            elif k in ("visible", "discoverable"):
                if not isinstance(v, bool):
                    return False
            elif k in ("on_frame", "off_frame"):
                if not isinstance(v, int):
                    return False
            else:
                return False
        return True

    def _edge_parameters_ok(self, edge_dict, all_connections):
        if isinstance(edge_dict, dict):
            if "end_node" not in edge_dict:
                return False
            for k, v in edge_dict.items():
                if k == "end_node" and v not in all_connections:
                    return False
                elif k in ("visible", "discoverable"):
                    if not isinstance(v, bool):
                        return False
                elif k == "scenegen" and v not in statefinders.SINGULAR_TYPES["scene_generator"]:
                    return False
                elif k == "architecture" and v not in statefinders.SINGULAR_TYPES["architecture"]:
                    return False
                elif k in ("style", "encounter_chance") and not isinstance(v, int):
                    return False
        return True

    def _check_value(self, part, value):
        if isinstance(value, dict) and "node" in value and isinstance(value["node"], dict) and "edges" in value and isinstance(value["edges"], list):
            if self._node_parameters_ok(value["node"]):
                if not value["edges"]:
                    # Empty list is ok.
                    return True
                elif part:
                    all_blueprints = list(part.get_branch(part.get_root()))
                    all_connections = worldmapeditor.get_all_connections(all_blueprints, part.raw_vars.get("entrance_world_map"))
                    return all(self._edge_parameters_ok(ed, all_connections) for ed in value["edges"])
                else:
                    return True

    def get_errors(self, part, key):
        myerrors = list()
        if not self._check_value(part, part.raw_vars.get(key)):
            myerrors.append("ERROR: world_map_data dict {} is not valid.".format(part.raw_vars.get(key)))
        return myerrors

    class WorldMapDataDict(dict):
        def __init__(self, rawdict):
            super().__init__(rawdict)

        @property
        def node_params(self):
            mylist = list()
            mydict = self["node"]
            for k, v in mydict.items():
                if k == "image_file":
                    mylist.append("image_file=\"{}\"".format(v))

                elif k in ("visible", "discoverable", "on_frame", "off_frame"):
                    mylist.append("{}={}".format(k, v))

            return ", ".join(mylist)

        @property
        def node_pos(self):
            return "{}, {}".format(*self["node"]["pos"])

        @property
        def edge_params(self):
            edges_list = list()
            for edge_dict in self["edges"]:
                my_edge = list()
                end_node_id = edge_dict["end_node"]
                my_edge.append("end_entrance=nart.camp.campdata[THE_WORLD].get({})".format(end_node_id))
                for k, v in edge_dict.items():
                    if k in ("visible", "discoverable", "style", "encounter_chance", "scenegen", "architecture"):
                        my_edge.append("{}={}".format(k, v))
                edges_list.append("dict({})".format(", ".join(my_edge)))

            return "[{}]".format(", ".join(edges_list))

    @classmethod
    def format_for_python(cls, value):
        return cls.WorldMapDataDict(value)


class StartingPointVariable(BaseVariableDefinition):
    DEFAULT_VAR_TYPE = "starting_point"
    WIDGET_TYPE = varwidgets.FiniteStateEditorWidget

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        rawval = part.raw_vars.get(key)
        myval = part.get_ultra_vars().get(key, None)
        if rawval is None:
            if not any(bp.brick.label == "STARTING_PLOT" for bp in part.get_all_blueprints()):
                myerrors.append("No starting plots or starting point defined".format(key, part, myval))
        else:
            my_names_and_states = statefinders.get_possible_states(part, part.brick.vars[key].var_type)
            mystates = [a[1] for a in my_names_and_states]
            if myval not in mystates:
                myerrors.append("Variable {} in {} has unknown value {}".format(key, part, myval))

        return myerrors

    @staticmethod
    def format_for_python(value):
        if value:
            return "nart.camp.go(nart.camp.campdata[THE_WORLD].get({}))".format(value)
        else:
            return "self.add_sub_plot(nart, \"START_PLOT_{}\".format(unique_id))"


class TagReactionVariable(BaseVariableDefinition):
    # The variable value will be a list of [tag, reaction_mod] lists.
    DEFAULT_VAR_TYPE = "tag_reaction"

    def get_widgets(self, part, key, editor=None, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        mylist.append(pbge.widgets.LabelWidget(0,0,350,0,"Tag Reactions", justify=-1))

        for trl in part.raw_vars.get(key,()):
            mylist.append(varwidgets.PersonalityTagValueEditorWidget(part, trl, refresh_fun=refresh_fun, **kwargs))

        myrow = pbge.widgets.RowWidget(0,0,350,0)
        mylist.append(myrow)

        myrow.add_left(pbge.widgets.LabelWidget(0,0,150,0,"Add Tag", draw_border=True, on_click=self._add_widget, data=(part.raw_vars[key], refresh_fun)))
        myrow.add_right(pbge.widgets.LabelWidget(0,0,150,0,"Delete Tag", draw_border=True, on_click=self._delete_widget, data=(part.raw_vars[key], refresh_fun)))

        return mylist

    def _add_widget(self, wid, ev):
        mylist, refresh_fun = wid.data
        mylist.append(["tags.Adventurer", "0"])
        refresh_fun()

    def _delete_widget(self, wid, ev):
        mylist, refresh_fun = wid.data
        mymenu = pbge.rpgmenu.PopUpMenu()
        for item in mylist:
            mymenu.add_item(item[0], item)
        mymenu.add_item("==None==", None)

        item_to_delete = mymenu.query()
        if item_to_delete:
            mylist.remove(item_to_delete)
            refresh_fun()

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        rawval = part.raw_vars.get(key)
        if isinstance(rawval, list):
            for i, tag_value in enumerate(rawval):
                if isinstance(tag_value, list) and len(tag_value) == 2:
                    if not tag_value[0] in statefinders.SINGULAR_TYPES["personal_tags"]:
                        myerrors.append("Error: Tag {} in pair {} in {} in {} is not valid.".format(tag_value[0], i, key, part))
                    else:
                        try:
                            n = int(tag_value[1])
                        except ValueError:
                            myerrors.append("Error: Value {} in pair {} in {} in {} is not an integer.".format(tag_value[1], i, key, part))
                else:
                    myerrors.append("Error: Tag/Value pair {} in {} in {} is malformed.".format(i, key, part))

        else:
            myerrors.append("Error: Variable {} in {} is not a list.".format(key,part))

        return myerrors

    @staticmethod
    def format_for_python(value: list):
        if value:
            my_params = ["({}, {})".format(k,int(v)) for k,v in value]
            return "dict([{}])".format(", ".join(my_params))


class SceneConnectionVariable(BaseVariableDefinition):
    # The variable value will be a list of [tag, reaction_mod] lists.
    DEFAULT_VAR_TYPE = "scene_connection"
    GATE_TYPES = ("Small Room", "Building", "Regular Room")

    DEFAULT_GATE_DEF = {"GATE_TYPE": 0, "ROOM_STYLE": "pbge.randmaps.rooms.OpenRoom",
                        "ANCHOR": "None", "DOOR_NAME": "Exit", "DOOR_CLASS": "ghwaypoints.Exit", "DOOR_SIGN": "None"}

    class MenuEffectWithData:
        def __init__(self, data, data_fun):
            self.data = data
            self.data_fun = data_fun
        def __call__(self, result):
            self.data_fun(self.data, result)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_val = [self.DEFAULT_GATE_DEF.copy(), self.DEFAULT_GATE_DEF.copy()]

    def get_widgets(self, part, key, editor=None, refresh_fun=None, **kwargs):
        # Return a list of widgets having to do with this variable.
        mylist = list()
        myval = part.raw_vars[key]
        for gatenum in range(2):
            mylist.append(pbge.widgets.LabelWidget(0,0,350,0,"Gate {}".format(gatenum+1), justify=-1))

            my_type_menu = pbge.widgets.ColDropdownWidget(350, "Gate Type", on_select=self.MenuEffectWithData(myval[gatenum], self._select_gate_type))
            for i, name in enumerate(self.GATE_TYPES):
                my_type_menu.add_item(name, i)
            my_type_menu.my_menu_widget.menu.set_item_by_value(myval[gatenum]["GATE_TYPE"])
            mylist.append(my_type_menu)

            my_room_menu = pbge.widgets.ColDropdownWidget(350, "Room Style", on_select=self.MenuEffectWithData(myval[gatenum], self._select_room_style))
            if myval[gatenum]["GATE_TYPE"] == 1:
                candidates = statefinders.get_possible_states(part, "building_terrset")
            else:
                candidates = statefinders.get_possible_states(part, "room")
            for k, v in candidates:
                my_room_menu.add_item(k, v)
            my_room_menu.my_menu_widget.menu.set_item_by_value(myval[gatenum]["ROOM_STYLE"])
            mylist.append(my_room_menu)

            my_anchor_menu = pbge.widgets.ColDropdownWidget(350, "Anchor", on_select=self.MenuEffectWithData(myval[gatenum], self._select_anchor))
            for k, v in statefinders.get_possible_states(part, "map_anchor"):
                my_anchor_menu.add_item(k, v)
            my_anchor_menu.my_menu_widget.menu.sort()
            my_anchor_menu.my_menu_widget.menu.set_item_by_value(myval[gatenum]["ANCHOR"])
            mylist.append(my_anchor_menu)

            mylist.append(pbge.widgets.ColTextEntryWidget(350, "Door Name", myval[gatenum].get("DOOR_NAME"), on_change=self._change_name, data=myval[gatenum]))

            my_door_menu = pbge.widgets.ColDropdownWidget(350, "Door Class", on_select=self.MenuEffectWithData(myval[gatenum], self._select_door_type))
            for k, v in statefinders.get_possible_states(part, "exit_types"):
                my_door_menu.add_item(k, v)
            my_door_menu.my_menu_widget.menu.set_item_by_value(myval[gatenum]["DOOR_CLASS"])
            mylist.append(my_door_menu)

            if myval[gatenum]["GATE_TYPE"] == 1:
                my_sign_menu = pbge.widgets.ColDropdownWidget(
                    350, "Door Sign", on_select=self.MenuEffectWithData(myval[gatenum], self._select_sign)
                )
                for k, v in statefinders.get_possible_states(part, "door_sign"):
                    my_sign_menu.add_item(k, v)
                #my_sign_menu.add_item("==None==", None)
                my_sign_menu.my_menu_widget.menu.sort()
                my_sign_menu.my_menu_widget.menu.set_item_by_value(myval[gatenum]["DOOR_SIGN"])
                mylist.append(my_sign_menu)

        self.refresh_fun = refresh_fun

        return mylist

    def _select_gate_type(self, mydict, result):
        if isinstance(result, int) and 0 <= result < len(self.GATE_TYPES):
            mydict["GATE_TYPE"] = result
            if self.refresh_fun:
                self.refresh_fun()

    def _select_room_style(self, mydict, result):
        if result:
            mydict["ROOM_STYLE"] = result
            if self.refresh_fun:
                self.refresh_fun()

    def _select_anchor(self, mydict, result):
        if result:
            mydict["ANCHOR"] = result
            if self.refresh_fun:
                self.refresh_fun()

    def _select_door_type(self, mydict, result):
        if result:
            mydict["DOOR_CLASS"] = result
            if self.refresh_fun:
                self.refresh_fun()

    def _select_sign(self, mydict, result):
        print(result)
        mydict["DOOR_SIGN"] = result
        if self.refresh_fun:
            self.refresh_fun()

    def _change_name(self, wid, ev):
        wid.data["DOOR_NAME"] = wid.text

    def get_errors(self, part, key):
        myerrors = list()
        myerrors += super().get_errors(part, key)
        rawval = part.raw_vars.get(key)
        for mygate, mydict in enumerate(rawval):
            if not ("GATE_TYPE" in mydict and isinstance(mydict["GATE_TYPE"], int) and 0 <= mydict["GATE_TYPE"] < len(self.GATE_TYPES)):
                myerrors.append("ERROR: Gate {} in {} has unknown type {}".format(mygate, part, mydict.get("GATE_TYPE")))
                break

            if mydict["GATE_TYPE"] == 1 and not statefinders.is_legal_state(part, "building_terrset", mydict.get("ROOM_STYLE")):
                myerrors.append("Error: Illegal building style {} for gate {} in {}.".format(mydict.get("ROOM_STYLE"), mygate, part))
            elif mydict["GATE_TYPE"] != 1 and not statefinders.is_legal_state(part, "room", mydict.get("ROOM_STYLE")):
                myerrors.append("Error: Illegal room style {} for gate {} in {}.".format(mydict.get("ROOM_STYLE"), mygate, part))

            if not statefinders.is_legal_state(part, "map_anchor", mydict.get("ANCHOR")):
                myerrors.append("Error: Illegal anchor {} for gate {} in {}.".format(mydict.get("ANCHOR"), mygate, part))

            if not statefinders.is_legal_state(part, "exit_types", mydict.get("DOOR_CLASS")):
                myerrors.append("Error: Illegal door class {} for gate {} in {}.".format(mydict.get("DOOR_CLASS"), mygate, part))

            if mydict.get("DOOR_SIGN"):
                if not statefinders.is_legal_state(part, "door_sign", mydict["DOOR_SIGN"]):
                    myerrors.append(
                        "Error: Illegal door sign {} for gate {} in {}.".format(mydict["DOOR_SIGN"], mygate, part)
                    )
            if not ("DOOR_NAME" in mydict and isinstance(mydict["DOOR_NAME"], str)):
                myerrors.append(
                    "Error: Illegal door name for gate {} in {}.".format(mygate, part)
                )

        return myerrors

    @staticmethod
    def format_for_python(value: list):
        # Return the room and door parameters for SCSceneConnection. I mean why not, eh?
        scsc_params = list()
        for room_num, room_dict in enumerate(value):
            room_params = list()
            door_params = list()
            if room_dict["GATE_TYPE"] == 0:
                room_params.append("width=3")
                room_params.append("height=3")
            if room_dict["GATE_TYPE"] == 1:
                room_params.append("tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM]")
                if room_dict.get("DOOR_SIGN"):
                    room_params.append("door_sign={}".format(DoorSignVariable.format_for_python(room_dict.get("DOOR_SIGN"))))
            anchor = room_dict.get("ANCHOR")
            room_params.append("anchor={}".format(anchor))

            door_params.append("name={}".format(repr(room_dict.get("DOOR_NAME", "EXIT"))))
            if anchor and anchor != "None":
                door_params.append("anchor={}".format(anchor))
            else:
                door_params.append("anchor=pbge.randmaps.anchors.middle")

            scsc_params.append("room{}={}({})".format(room_num+1, room_dict["ROOM_STYLE"], ", ".join(room_params)))
            scsc_params.append("door{}={}({})".format(room_num+1, room_dict["DOOR_CLASS"], ", ".join(door_params)))

        return ", ".join(scsc_params)


def get_variable_definition(default_val=0, var_type="integer", **kwargs):
    if var_type == "text":
        return TextVariable(default_val, **kwargs)
    elif var_type == "literal":
        return StringLiteralVariable(default_val, **kwargs)
    elif var_type == "identifier":
        return StringIdentifierVariable(default_val, **kwargs)
    elif var_type == "campaign_variable":
        return CampaignVariableVariable(default_val, **kwargs)
    elif var_type == "interior_decor":
        return InteriorDecorVariable(default_val, var_type, **kwargs)
    elif var_type in ("faction", "scene", "npc", "world_map", "job"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type in statefinders.LIST_TYPES:
        return FiniteStateListVariable(default_val, var_type, **kwargs)
    elif var_type == "scene_tags":
        return SceneTagListVariable(default_val, var_type, **kwargs)
    elif var_type == "door_sign":
        return DoorSignVariable(default_val, var_type, **kwargs)
    elif var_type in statefinders.SINGULAR_TYPES:
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type.startswith("physical:"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type.startswith("terrain:"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type.endswith(".png"):
        return FiniteStateVariable(default_val, var_type, **kwargs)
    elif var_type == "boolean":
        return BooleanVariable(default_val, **kwargs)
    elif var_type == "dialogue_context":
        return DialogueContextVariable(default_val, **kwargs)
    elif var_type == "dialogue_data":
        return DialogueDataVariable(default_val, **kwargs)
    elif var_type == "conditional":
        return ConditionalVariable(default_val, **kwargs)
    elif var_type == "music":
        return MusicVariable(default_val, **kwargs)
    elif var_type == "palette":
        return PaletteVariable(default_val, **kwargs)
    elif var_type.startswith("list:"):
        return FiniteStateListVariable(default_val, var_type, **kwargs)
    elif var_type == "integer":
        return IntegerVariable(default_val, **kwargs)
    elif var_type == "world_map_data":
        return WorldMapDataVariable(default_val, **kwargs)
    elif var_type == "starting_point":
        return StartingPointVariable(default_val, **kwargs)
    elif var_type == "major_npc_id":
        return MajorNPCIDVariable(default_val, **kwargs)
    elif var_type == "tag_reaction":
        return TagReactionVariable(default_val, **kwargs)
    elif var_type == "scene_connection":
        return SceneConnectionVariable(default_val, **kwargs)
    else:
        if var_type != "string":
            print("Unknown variable type {}; defaulting to string.".format(var_type))
        return StringVariable(default_val, var_type, **kwargs)

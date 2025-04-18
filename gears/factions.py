import collections

from pbge import Singleton
from . import color
from . import jobs
from . import tags
import random
from . import personality

FR_ENEMY = "ENEMY"


class Faction(Singleton):
    name = "Faction"
    factags = ()
    mecha_colors = (color.AceScarlet, color.CometRed, color.HotPink, color.Black, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot",),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot", "Field Medic"),
    }
    LOCATIONS = ()
    NAME_PATTERNS = ("the {number} {noun}", "the {adjective} {noun}")
    NAME_PAT_WITH_CITY = ("the {number} {noun} of {city}",)
    ADJECTIVES = ("Whatever",)
    NOUNS = ("Circle",)
    uniform_colors = (None, None, None, None, None)

    @classmethod
    def get_faction_tag(cls):
        return cls

    @classmethod
    def choose_job(cls, role):
        candidates = cls.CAREERS.get(role)
        if candidates:
            job = jobs.ALL_JOBS[random.choice(candidates)]
        else:
            job = jobs.ALL_JOBS["Mecha Pilot"]
        return job

    @classmethod
    def choose_location(cls):
        if cls.LOCATIONS:
            return random.choice(cls.LOCATIONS)

    ORDINALS = ("1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "13th")

    @classmethod
    def get_circle_name(cls, city=None):
        sub_dic = {
            "number": random.choice(cls.ORDINALS),
            "adjective": random.choice(cls.ADJECTIVES),
            "noun": random.choice(cls.NOUNS)
        }
        candidates = list(cls.NAME_PATTERNS)
        if city:
            candidates += list(cls.NAME_PAT_WITH_CITY)
            sub_dic["city"] = str(city)
        return random.choice(candidates).format(**sub_dic)


class AegisOverlord(Faction):
    name = "Aegis Overlord Luna"
    factags = (tags.Politician, tags.Military)
    mecha_colors = (color.LunarGrey, color.AegisCrimson, color.LemonYellow, color.CeramicColor, color.LunarGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Soldier"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot", "Field Medic"),
    }
    LOCATIONS = (personality.Luna,)
    ADJECTIVES = ("Expedition", "Strike Force")
    NOUNS = ("Aegis", "Lunar")
    uniform_colors = (color.LunarGrey, None, None, None, color.AegisCrimson)


class BladesOfCrihna(Faction):
    name = "the Blades of Crihna"
    factags = (tags.Criminal,)
    mecha_colors = (color.HeavyPurple, color.SeaGreen, color.PirateSunrise, color.Black, color.StarViolet)
    LOCATIONS = (personality.L5DustyRing,)
    CAREERS = {
        tags.Trooper: ("Pirate", "Thief"),
        tags.Commander: ("Pirate Captain",),
        tags.Support: ("Mecha Pilot", "Hacker"),
    }
    ADJECTIVES = ("Pirate",)
    NOUNS = ("Blades", "Fleet")
    uniform_colors = (color.HeavyPurple, None, None, None, color.SeaGreen)


class BoneDevils(Faction):
    name = "the Bone Devil Gang"
    factags = (tags.Criminal, tags.Military)
    mecha_colors = (color.Black, color.Cream, color.BrightRed, color.Avocado, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Bandit", "Thief"),
        tags.Commander: ("Commander", "Scavenger", "Crimelord", "Kingpin"),
        tags.Support: ("Mecha Pilot", "Tekno"),
    }
    LOCATIONS = (personality.DeadZone,)
    ADJECTIVES = ("Devil", "Bone", "Death")
    NOUNS = ("Gang", "Barons", "Skulls")
    uniform_colors = (color.Black, None, None, color.BrightRed, color.Terracotta)


class TreasureHunters(Faction):
    name = "the Treasure Hunter Guild"
    factags = (tags.Criminal, tags.Adventurer)
    mecha_colors = (color.Charcoal, color.Gold, color.OrangeRed, color.SlateGrey, color.DeepSeaBlue)
    CAREERS = {
        tags.Trooper: ("Mercenary", "Thief", "Explorer"),
        tags.Commander: ("Smuggler", "Kingpin", "Crimelord"),
        tags.Support: ("Hacker", "Scavenger", "Assassin"),
    }
    LOCATIONS = (personality.DeadZone, personality.GreenZone)
    ADJECTIVES = ("Treasure", "Secret", "Thieves")
    NOUNS = ("Club", "Guild")
    uniform_colors = (color.Gold, None, None, color.NobleGold, color.Cobalt)


class TerranFederation(Faction):
    name = "the Terran Federation"
    factags = (tags.Politician,)
    mecha_colors = (color.ArmyDrab, color.Olive, color.ElectricYellow, color.GullGrey, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Citizen"),
        tags.Commander: ("Bureaucrat", "Commander", "Mayor"),
        tags.Support: ("Explorer", "Firefighter", "Paramedic", "Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Terran",)
    NOUNS = ("Council",)
    uniform_colors = (color.Turquoise, None, None, None, None)


class TerranDefenseForce(Faction):
    name = "the Terran Defense Force"
    factags = (tags.Military,)
    mecha_colors = (color.ArmyDrab, color.Olive, color.ElectricYellow, color.GullGrey, color.Terracotta)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Soldier"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot", "Field Medic"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Terran",)
    NOUNS = ("Defense Team", "Militia")
    uniform_colors = (color.GriffinGreen, None, None, None, color.Khaki)


class Guardians(Faction):
    name = "the Guardians"
    factags = (tags.Police,)
    mecha_colors = (color.ShiningWhite, color.PrussianBlue, color.BrightRed, color.WarmGrey, color.Black)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Police Officer"),
        tags.Commander: ("Detective",),
        tags.Support: ("Bounty Hunter",),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Investigation", "Peacekeeping")
    NOUNS = ("Unit", "Squad")
    uniform_colors = (color.Black, None, None, None, color.FreedomBlue)


class RegExCorporation(Faction):
    name = "RegEx Corporation"
    factags = (tags.CorporateWorker,)
    mecha_colors = (color.Turquoise, color.AeroBlue, color.OrangeRed, color.FieldGrey, color.ElectricYellow)
    CAREERS = {
        tags.Trooper: ("Test Pilot", "Trucker", "Factory Worker"),
        tags.Commander: ("Corporate Executive", "Dispatcher"),
        tags.Support: ("Construction Worker", "Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("RegEx", "Corporate")
    NOUNS = ("Team", "Division")
    uniform_colors = (color.Turquoise, None, None, None, color.ElectricYellow)


class BioCorp(Faction):
    name = "BioCorp"
    factags = (tags.CorporateWorker,)
    mecha_colors = (color.RoyalPink, color.Cream, color.BrightRed, color.GothSkin, color.DeepSeaBlue)
    CAREERS = {
        tags.Trooper: ("Arena Pilot", "Test Pilot"),
        tags.Commander: ("Corporate Executive", "Scientist"),
        tags.Support: ("Field Medic", "Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("BioCorp", "Research")
    NOUNS = ("Team", "Division")
    uniform_colors = (color.Cream, None, None, None, color.RoyalPink)


class KettelIndustries(Faction):
    name = "Kettel Industries"
    factags = (tags.CorporateWorker,)
    mecha_colors = (color.KettelPurple, color.StarViolet, color.FlourescentGreen, color.Charcoal, color.SteelBlue)
    CAREERS = {
        tags.Trooper: ("Arena Pilot", "Test Pilot", "Trucker"),
        tags.Commander: ("Corporate Executive", "Mecha Designer"),
        tags.Support: ("Recon Pilot", "Construction Worker", "Researcher"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("BioCorp", "Research")
    NOUNS = ("Team", "Division")
    uniform_colors = (color.KettelPurple, None, None, None, color.StarViolet)


class DeadzoneFederation(Faction):
    name = "the Deadzone Federation"
    factags = (tags.Politician,)
    mecha_colors = (color.DarkBrown, color.AeroBlue, color.GunRed, color.DeepSeaBlue, color.DesertYellow)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Mercenary"),
        tags.Commander: ("Commander", "Aristo", "Warlord", "Mayor"),
        tags.Support: ("Recon Pilot", "Scavenger", "Tekno"),
    }
    LOCATIONS = (personality.DeadZone,)
    ADJECTIVES = ("Deadzone", "Wasteland", "Frontier")
    NOUNS = ("Council",)
    uniform_colors = (color.DesertYellow, None, None, None, color.DarkBrown)


class ClanIronwind(Faction):
    name = "Clan Ironwind"
    factags = (tags.Politician, tags.Military)
    mecha_colors = (color.CometRed, color.DimGrey, color.GreenYellow, color.Black, color.BlackRose)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Mercenary", "Bandit"),
        tags.Commander: ("Aristo", "Warlord"),
        tags.Support: ("Recon Pilot", "Scavenger", "Gladiator", "Tekno"),
    }
    LOCATIONS = (personality.DeadZone,)
    ADJECTIVES = ("Deadzone", "Wasteland", "Iron")
    NOUNS = ("Legion", "Warriors", "Warband")
    uniform_colors = (color.BlackRose, None, None, None, None)


class TheSilverKnights(Faction):
    name = "the Silver Knights"
    factags = (tags.Military,)
    mecha_colors = (color.SkyBlue, color.ShiningWhite, color.BrightRed, color.SlateGrey, color.AeroBlue)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Knight"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot", "Field Medic"),
    }
    LOCATIONS = (personality.L5Spinners,)
    ADJECTIVES = ("Silver",)
    NOUNS = ("Knights", "Order")
    uniform_colors = (color.AeroBlue, None, None, None, color.SkyBlue)


class TheSolarNavy(Faction):
    name = "the Solar Navy"
    factags = (tags.Military,)
    mecha_colors = (color.DeepSeaBlue, color.Jade, color.OrangeRed, color.GullGrey, color.GhostGrey)
    CAREERS = {
        tags.Trooper: ("Mecha Pilot", "Soldier"),
        tags.Commander: ("Commander",),
        tags.Support: ("Recon Pilot", "Field Medic"),
    }
    LOCATIONS = (personality.GreenZone,)
    ADJECTIVES = ("Terran", "Solar")
    NOUNS = ("Defense Fleet", "Wing")
    uniform_colors = (color.SkyBlue, None, None, None, color.DeepSeaBlue)


class ProDuelistAssociation(Faction):
    name = "the Pro Duelist Association"
    factags = (tags.Adventurer, tags.Media)
    mecha_colors = (color.PlasmaBlue, color.GunRed, color.Malachite, color.SteelBlue, color.FreedomBlue)
    CAREERS = {
        tags.Trooper: ("Arena Pilot",),
        tags.Commander: ("Arena Pilot",),
        tags.Support: ("Gladiator", "Singer"),
    }
    LOCATIONS = (
    personality.GreenZone, personality.DeadZone, personality.L5Spinners, personality.L5DustyRing, personality.Mars)
    ADJECTIVES = ("Duelist", "Arena", "Cavalier")
    NOUNS = ("Club", "League")


class Ravagers(Faction):
    name = "the Ravagers"
    factags = (tags.Adventurer, tags.Criminal)
    mecha_colors = (color.DesertYellow, color.Sandstone, color.FlourescentGreen, color.Ebony, color.DeepSeaBlue)
    CAREERS = {
        tags.Trooper: ("Bandit", "Scavenger", "Mercenary"),
        tags.Commander: ("Gladiator", "Assassin", "Warlord"),
        tags.Support: ("Explorer", "Technoshaman", "Neodruid"),
    }
    LOCATIONS = (personality.DeadZone,)
    ADJECTIVES = ("Ashen", "Forsaken", "Apocalypse")
    NOUNS = ("Nomads", "Survivors", "Caravan")


class Circle(object):
    def __init__(self, camp, parent_faction=None, mecha_colors=None, name="", careers=None, factags=(), locations=(),
                 uniform_colors=None, active=True, allies=(), enemies=()):
        if parent_faction and not name:
            name = parent_faction.get_circle_name()
        elif not name:
            name = Faction.get_circle_name()
        self.name = name
        self.parent_faction = parent_faction
        random_colors = color.random_mecha_colors()
        if parent_faction and not mecha_colors:
            mecha_colors = list(parent_faction.mecha_colors)
            for col_i in range(len(mecha_colors)):
                if random.randint(1, 5) == 3:
                    mecha_colors[col_i] = color.choose_color_by_tags((mecha_colors[col_i].family,))
                elif random.randint(1, 10) == 7:
                    mecha_colors[col_i] = random_colors[col_i]
        self.mecha_colors = mecha_colors or random_colors
        if parent_faction and not uniform_colors:
            uniform_colors = parent_faction.uniform_colors
        self.uniform_colors = uniform_colors or (None, None, None, None, None)
        self.careers = dict()
        if careers:
            self.careers.update(careers)
        self.factags = list(factags)
        if parent_faction and not factags:
            self.factags = list(parent_faction.factags)
        self.locations = list(locations)
        if self.parent_faction:
            self.locations += self.parent_faction.LOCATIONS
        self.active = active
        if camp:
            camp.faction_relations[self] = FactionRelations(allies=allies, enemies=enemies)

    def get_faction_tag(self):
        if self.parent_faction:
            return self.parent_faction.get_faction_tag()
        else:
            return self

    def choose_job(self, role):
        candidates = self.careers.get(role)
        job = jobs.ALL_JOBS["Mecha Pilot"]
        if candidates:
            job = jobs.ALL_JOBS[random.choice(candidates)]
        elif self.parent_faction:
            job = self.parent_faction.choose_job(role)
        return job

    def choose_location(self):
        if self.locations:
            return random.choice(self.locations)

    def __str__(self):
        return self.name

    ADJECTIVE = ("Brutal", "Cruel", "Deadly", "Frenzied", "Angry", "Golden", "Honored", "Veteran", "Ace", "Green",
               "Glorious", "Invincible", "Jolly", "Killer", "Lucky", "Larcenous", "Black", "White", "Unyielding",
               "Merciless", "Thunder", "Steel", "Mantis", "Lion", "Eagle", "Hornet", "Bear", "Cobra", "Tiger",
                 "Sacred", "Burning", "Super", "Cyber", "Fusion", "Dragon", "Laser", "Mighty", "Mercenary",
                 "Amazing", "Fantastic", "Incredible", "Uncanny", "Punk", "Foolish", "Cool", "Hot", "Fighting",
               "Unbeatable", "Vicious", "Violent", "Red", )
    NOUN = (
        "Warriors", "Demons", "Gang", "Talons", "Destroyers", "Raiders", "Legion", "Modez", "Angels", "Hearts",
        "Breakers", "Bruisers", "Crashers", "Executors", "Platoon", "Squad", "Hammers", "Spears", "Emperors",
        "Queens", "Princes", "Ladies", "Barons", "Raptors", "Titans", "Unicorns", "Hawks", "Sharks", "Guild",
        "Scouts", "League", "Wing", "Aces", "Champions" )

    @classmethod
    def _generate_random_name(cls):
        return "the {} {}".format(random.choice(cls.ADJECTIVE), random.choice(cls.NOUN))

    @classmethod
    def random_circle(cls, camp, allies=(), enemies=()):
        return cls(
            camp, mecha_colors=color.random_mecha_colors(), name=cls._generate_random_name(), careers={
                tags.Trooper: ("Mecha Pilot", "Soldier"),
                tags.Commander: ("Commander",),
                tags.Support: ("Recon Pilot", "Field Medic"),
            }, factags=(tags.Adventurer, tags.Military), allies=allies, enemies=enemies
        )


def is_a_faction(maybe_fac):
    return hasattr(maybe_fac, "get_faction_tag")


class FactionRelations(object):
    ALLY = 1
    NEUTRAL = 0
    ENEMY = -1

    def __init__(self, allies=(), enemies=(), leader=None):
        self.relations = collections.defaultdict(int)
        for a in allies:
            self.relations[a] = self.ALLY
        for e in enemies:
            self.relations[e] = self.ENEMY
        self.pc_relation = self.NEUTRAL
        self.leader = leader

    @property
    def allies(self):
        return [a for a in self.relations.keys() if self.relations[a] == self.ALLY]

    @property
    def enemies(self):
        return [e for e in self.relations.keys() if self.relations[e] == self.ENEMY]

    def set_faction_ally(self, other_faction):
        self.relations[other_faction] = self.ALLY

    def set_faction_neutral(self, other_faction):
        self.relations[other_faction] = self.NEUTRAL

    def set_faction_enemy(self, other_faction):
        self.relations[other_faction] = self.ENEMY

    def set_pc_ally(self):
        self.pc_relation = self.ALLY

    def set_pc_neutral(self):
        self.pc_relation = self.NEUTRAL

    def set_pc_enemy(self):
        self.pc_relation = self.ENEMY

    def __setstate__(self, state):
        # For saves from V0.925 or earlier, make sure there's a leader defined.
        self.__dict__.update(state)
        if "leader" not in state:
            self.leader = None


DEFAULT_FACTION_DICT_NT158 = {
    AegisOverlord: FactionRelations(
        allies=(),
        enemies=(TerranFederation, DeadzoneFederation, BladesOfCrihna, TheSilverKnights, TheSolarNavy)
    ),
    BladesOfCrihna: FactionRelations(
        allies=(),
        enemies=(AegisOverlord, Guardians, TheSilverKnights, TheSolarNavy)
    ),
    BoneDevils: FactionRelations(
        allies=(),
        enemies=(TerranDefenseForce, Guardians, BioCorp, KettelIndustries, RegExCorporation)
    ),
    TerranFederation: FactionRelations(
        allies=(TerranDefenseForce, Guardians, TheSolarNavy),
        enemies=(AegisOverlord,)
    ),
    TerranDefenseForce: FactionRelations(
        allies=(TerranFederation, TheSolarNavy),
        enemies=(AegisOverlord, BoneDevils, ClanIronwind)
    ),
    Guardians: FactionRelations(
        allies=(TerranFederation, DeadzoneFederation),
        enemies=(BoneDevils, BladesOfCrihna, Ravagers)
    ),
    DeadzoneFederation: FactionRelations(
        allies=(Guardians, TerranFederation),
        enemies=(BoneDevils, ClanIronwind, Ravagers),
    ),
    ClanIronwind: FactionRelations(
        allies=(),
        enemies=(TerranFederation, TerranDefenseForce, DeadzoneFederation, Ravagers)
    ),
    TheSilverKnights: FactionRelations(
        allies=(TheSolarNavy,),
        enemies=(AegisOverlord, BladesOfCrihna)
    ),
    TheSolarNavy: FactionRelations(
        allies=(TerranFederation, TerranDefenseForce, TheSilverKnights),
        enemies=(AegisOverlord, BladesOfCrihna)
    ),
    ProDuelistAssociation: FactionRelations(),
    TreasureHunters: FactionRelations(
        allies=(BladesOfCrihna, BoneDevils),
        enemies=(Guardians,)
    ),
    KettelIndustries: FactionRelations(
        enemies=(RegExCorporation, BioCorp, BoneDevils, Ravagers, BladesOfCrihna),
        allies=(Guardians,)
    ),
    BioCorp: FactionRelations(
        enemies=(RegExCorporation, KettelIndustries, BoneDevils, Ravagers, TreasureHunters),
        allies=(Guardians,)
    ),
    RegExCorporation: FactionRelations(
        enemies=(KettelIndustries, BioCorp, BoneDevils, Ravagers, ClanIronwind),
        allies=(Guardians,)
    ),
    Ravagers: FactionRelations(
        enemies=(DeadzoneFederation, ClanIronwind, BoneDevils, KettelIndustries, BioCorp, RegExCorporation),
        allies=()
    )


}

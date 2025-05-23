from pbge import Singleton
from . import geffects, stats
import pbge


# Utility Functions
def replace_attack_roll(base):
    # Replace the old attack roll used by this attack with a basic AttackRoll.
    old_fx = base.fx
    if hasattr(old_fx, "can_crit"):
        can_crit = old_fx.can_crit
    else:
        can_crit = True
    base.fx = geffects.AttackRoll(
        att_stat=old_fx.att_stat,
        att_skill=old_fx.att_skill,
        children=old_fx.children,
        anim=old_fx.anim,
        accuracy=old_fx.accuracy,
        penetration=old_fx.penetration,
        modifiers=old_fx.modifiers,
        defenses=old_fx.defenses,
        can_crit=can_crit,
        terrain_effects=old_fx.terrain_effects
    )


class Accurate(Singleton):
    # This weapon has an Aim action that gives +20 bonus to hit for 4MP.
    # An accurate attack fires just once.
    name = "Accurate"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.2
    POWER_MODIFIER = 1.0

    ADJECTIVES = ("Smart", "Guided")
    TARGETS = ("evasive targets",)

    @classmethod
    def get_attacks(cls, weapon):
        base = weapon.get_basic_attack(name='Aim +20', attack_icon=12)
        base.price.append(geffects.MentalPrice(4))
        base.data.thrill_power = base.data.thrill_power + 10
        replace_attack_roll(base)
        base.fx.modifiers.append(geffects.GenericBonus('Aim', 20))
        return [base]


class Agonize(Singleton):
    name = "Agonize"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 1.0

    ADJECTIVES = ("Pain",)
    TARGETS = ("enemy commanders",)
    CAPABILITIES = ("quickly wear down opponents",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        attack.fx.children[0].children.append(
            geffects.DoDrainStamina(1, 6)
        )


class Automatic(Singleton):
    # This weapon has two extra modes: x5 ammo for 2 shots, or x10 ammo for 3 shots
    name = "Automatic"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.2
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks(cls, weapon):
        return [weapon.get_basic_attack(name='2 shots, x5 ammo', targets=2, ammo_cost=5, attack_icon=3),
                weapon.get_basic_attack(name='3 shots, x10 ammo', targets=3, ammo_cost=10, attack_icon=6)]


class Blast1(Singleton):
    name = "Blast 1"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 2.0
    BLAST_RADIUS = 1

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Change the area to blast.
        if hasattr(attack.area, "reach"):
            reach = attack.area.reach
        else:
            reach = weapon.reach
        attack.area = pbge.scenes.targetarea.Blast(radius=cls.BLAST_RADIUS, reach=reach, delay_from=1)
        attack.fx.anim = weapon.get_area_anim()
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()
        attack.fx.children[0].scatter = True
        attack.fx.can_crit = False


class Blast2(Blast1):
    name = "Blast 2"
    MASS_MODIFIER = 2.0
    VOLUME_MODIFIER = 3.0
    COST_MODIFIER = 3.5
    POWER_MODIFIER = 3.0
    BLAST_RADIUS = 2


class BonusStrike1(Singleton):
    # Default attack action scores 1 to 2 hits by default.
    name = "Bonus Strike 1"
    MASS_MODIFIER = 1.3
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.2
    STRIKE_NUMBER = 1

    FAMILY = "BonusStrike"
    ADJECTIVES = ("Double",)
    CAPABILITIES = ("strike multiple times",)

    @classmethod
    def replace_primary_attack(cls, weapon):
        base = weapon.get_basic_attack(name='Bonus Strike +{}'.format(cls.STRIKE_NUMBER),
                                       attack_icon=9, bonus_strike=cls.STRIKE_NUMBER)
        base.data.thrill_power = base.data.thrill_power + 5 * cls.STRIKE_NUMBER
        return [base, ]


class BonusStrike2(BonusStrike1):
    # Default attack action scores 1 to 3 hits by default.
    name = "Bonus Strike 2"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 1.5
    STRIKE_NUMBER = 2

    FAMILY = "BonusStrike"
    ADJECTIVES = ("Triple",)


class BurnAttack(Singleton):
    name = "Burn"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.5

    ADJECTIVES = ("Flaming",)
    TARGETS = ("durable opponents",)
    CAPABILITIES = ("set targets on fire",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add a burn status to the children.
        attack.fx.children.append(geffects.AddEnchantment(geffects.Burning, ))


class Brutal(Singleton):
    name = "Brutal"
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    ADJECTIVES = ("Brutal",)
    CAPABILITIES = ("quickly break through armor",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add brutality to the damage.
        attack.fx.children[0].is_brutal = True


class BurstFire2(Singleton):
    # Default fire action fires multiple bullets.
    name = "Burst Fire 2"
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.0
    BURST_VALUE = 2

    @classmethod
    def replace_primary_attack(cls, weapon):
        base = weapon.get_basic_attack(name='Burst x{}'.format(cls.BURST_VALUE), ammo_cost=cls.BURST_VALUE,
                                       attack_icon=9)
        old_fx = base.fx
        base.shot_anim = geffects.BulletFactory(cls.BURST_VALUE, base.shot_anim)
        base.fx = geffects.MultiAttackRoll(
            att_stat=old_fx.att_stat,
            att_skill=old_fx.att_skill,
            num_attacks=cls.BURST_VALUE,
            children=old_fx.children,
            anim=old_fx.anim,
            accuracy=old_fx.accuracy + cls.BURST_VALUE * 3,
            penetration=old_fx.penetration - 10,
            modifiers=old_fx.modifiers,
            defenses=old_fx.defenses,
            apply_hit_modifier=False,
            terrain_effects=old_fx.terrain_effects
        )
        base.data.thrill_power = base.data.thrill_power + 3 * cls.BURST_VALUE
        return [base, ]


class BurstFire3(BurstFire2):
    # Default fire action fires multiple bullets.
    name = "Burst Fire 3"
    MASS_MODIFIER = 1.3
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0
    BURST_VALUE = 3


class BurstFire4(BurstFire2):
    # Default fire action fires multiple bullets.
    name = "Burst Fire 4"
    MASS_MODIFIER = 1.4
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0
    BURST_VALUE = 4


class BurstFire5(BurstFire2):
    # Default fire action fires multiple bullets.
    name = "Burst Fire 5"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.1
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 1.0
    BURST_VALUE = 5


class ChargeAttack(Singleton):
    # This weapon has a charge attack
    name = "Charge Attack"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.5
    COST_MODIFIER = 2.2
    POWER_MODIFIER = 1.0

    # Treat weapons with this modifier as having at least reach 3.
    COST_EFFECTIVE_REACH_MIN = 3

    @classmethod
    def get_attacks(cls, weapon):
        aa = weapon.get_basic_attack(name='Charge', attack_icon=15)
        replace_attack_roll(aa)
        aa.fx.modifiers.append(geffects.GenericBonus('Charge', 10))
        aa.fx.children[0].damage_d = round(aa.fx.children[0].damage_d * 5 / 3)
        aa.area = geffects.DashTarget(weapon.get_root())
        aa.data.thrill_power = aa.data.thrill_power + 15
        aa.shot_anim = geffects.DashFactory(weapon.get_root())
        return [aa]


class ConeAttack(Singleton):
    name = "Cone Area"
    MASS_MODIFIER = 2.0
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 4.0
    POWER_MODIFIER = 3.0

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Change the area to cone.
        attack.area = pbge.scenes.targetarea.Cone(reach=weapon.reach * 2, delay_from=-1)
        attack.shot_anim = None
        attack.fx.anim = weapon.get_area_anim()
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()
        attack.fx.children[0].scatter = True
        attack.fx.can_crit = False

    @classmethod
    def get_reach_str(cls, weapon):
        return '{}-{} cone'.format(weapon.reach, weapon.reach * 2)


class Defender(Singleton):
    name = "Defender"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.0
    PARRY_BONUS = 20

    ADJECTIVES = ("Bastion", )
    CAPABILITIES = ("parry enemy attacks",)


class Designator(Singleton):
    name = "Designator"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.3
    POWER_MODIFIER = 1.0

    ADJECTIVES = ("Lock-On", )
    CAPABILITIES = ("mark an enemy for targeting",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add a Sensor Lock status to the children.
        attack.fx.children[0].children.append(
            geffects.IfEnchantmentOK(
                geffects.SensorLock,
                on_success=(
                    geffects.OpposedSkillRoll(
                        stats.Ego, weapon.get_attack_skill(), stats.Ego, stats.Computers, roll_mod=25,
                        min_chance=10,
                        on_success=(
                        geffects.AddEnchantment(geffects.SensorLock, dur_n=3, dur_d=3, anim=geffects.SensorLockAnim),)
                    ),
                ),
            )
        )


class DisintegrateAttack(Singleton):
    name = "Disintegrate"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 2.0

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add a disintegration status to the children.
        attack.fx.children[0].children.append(
            geffects.IfEnchantmentOK(
                geffects.Disintegration,
                on_success=(
                    geffects.ResistanceRoll(stats.Ego, stats.Ego, roll_mod=25, min_chance=5,
                                            on_success=(
                                            geffects.AddEnchantment(geffects.Disintegration, dur_n=1, dur_d=6,
                                                                    anim=geffects.InflictDisintegrationAnim),)
                                            ),
                ),
            )
        )


class FastAttack(Singleton):
    # Extra fire action can hit twice.
    name = "Fast Attack"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 2.0
    BURST_VALUE = 2

    ADJECTIVES = ("Rapid", )
    CAPABILITIES = ("attack multiple enemies at once",)

    @classmethod
    def get_attacks(cls, weapon):
        aa: pbge.effects.Invocation = weapon.get_basic_attack(name='{} attacks', attack_icon=9)
        aa.targets = max(aa.targets + 1, 2)
        aa.name = aa.name.format(aa.targets)
        aa.price.append(geffects.MentalPrice(3))
        aa.data.thrill_power += 2
        return [aa]


class Flail(Singleton):
    name = "Flail"
    MASS_MODIFIER = 2.0
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 5.0
    POWER_MODIFIER = 1.0
    NO_PARRY = True

    CAPABILITIES = ("bypass shields and other defenses",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Flails cannot be blocked or parried.
        attack.fx.defenses[geffects.PARRY] = None
        attack.fx.defenses[geffects.BLOCK] = None


class HaywireAttack(Singleton):
    name = "Haywire"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 2.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    ADJECTIVES = ("Pulse", )
    TARGETS = ("priority targets",)
    CAPABILITIES = ("scramble an opponent's control gear",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add a burn status to the children.
        attack.fx.children[0].children.append(
            geffects.IfEnchantmentOK(
                geffects.HaywireStatus,
                on_success=(
                    geffects.ResistanceRoll(stats.Knowledge, stats.Ego, roll_mod=25, min_chance=25,
                                            on_success=(
                                            geffects.AddEnchantment(geffects.HaywireStatus, dur_n=2, dur_d=4,
                                                                    anim=geffects.InflictHaywireAnim),)
                                            ),
                ),
            )
        )


class DrainsPower(Singleton):
    name = "Drains Power"
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.2
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 0.8

    ADJECTIVES = ("Vampire", )
    CAPABILITIES = ("deplete an enemy's power",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add a drain power effect to the children.
        # Construct an invocation that is invoked after damage is dealt,
        # otherwise the -100Pw caption will overlap with the damage caption.
        attack.fx.children[0].children.append(geffects.DoDrainPower())


class IgnitesAmmo(BurnAttack):
    # Ammo now explodes, so this attack attribute is being phased out. Should be safe to remove this entirely
    # by v1.000 or so.
    pass


class Intercept(Singleton):
    name = "Intercept"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0
    CAN_INTERCEPT = True

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        attack.data.thrill_power = attack.data.thrill_power // 2

class LineAttack(Singleton):
    name = "Line Area"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 2.0

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Change the area to cone.
        attack.area = pbge.scenes.targetarea.Line(reach=weapon.reach * 3, delay_from=-1)
        attack.shot_anim = None
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()
        attack.fx.anim = weapon.get_area_anim()
        attack.fx.children[0].scatter = True
        attack.fx.can_crit = False


class LinkedFire(Singleton):
    name = "Linked Fire"
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks(cls, weapon):
        myroot = weapon.get_root()
        weapons = cls.get_all_weapons(myroot, weapon)
        invos = [wep.get_primary_attacks()[0] for wep in weapons]
        mylist = list()
        if invos and len(invos) > 1:
            myattack = weapon.get_primary_attacks()[0]
            myattack.targets = 0
            for i in invos:
                if i.can_be_invoked(myroot, True):
                    myattack.targets += 1
                    if i.weapon is not weapon:
                        myattack.price += i.price
            if myattack.targets > 1:
                myattack.price.append(geffects.MentalPrice(max(myattack.targets, 2)))
                myattack.name = "Link {} shots".format(myattack.targets)
                myattack.data.active_frame = 18
                myattack.data.inactive_frame = 19
                myattack.data.disabled_frame = 20
                myattack.data.thrill_power = myattack.data.thrill_power + (myattack.targets + 1) * 4
                mylist.append(myattack)
        return mylist

    @classmethod
    def get_all_weapons(cls, myroot, weapon):
        mylist = list()
        for wep in myroot.ok_descendants(False):
            if cls.matches(weapon, wep) and wep.is_operational():
                mylist.append(wep)
        return mylist

    @staticmethod
    def matches(wep1, wep2):
        return (
                wep1.__class__ is wep2.__class__ and wep1.scale is wep2.scale and wep1.damage == wep2.damage and
                wep1.reach == wep2.reach and wep1.accuracy == wep2.accuracy and wep1.penetration == wep2.penetration and
                set(wep1.attributes) == set(wep2.attributes)
        )


# Like linked-fire, but more appropriately-named for melee.
class MultiWielded(LinkedFire):
    name = "Multi Wielded"

    @classmethod
    def get_attacks(cls, weapon):
        mylist = LinkedFire.get_attacks(weapon)
        if mylist:
            # Rename from "Link {} shots" to "Wield {} weapons"
            myattack = mylist[0]
            myattack.name = "Wield {} weapons".format(myattack.targets)
        return mylist


class OverloadAttack(Singleton):
    name = "Overload"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.5
    POWER_MODIFIER = 1.5

    ADJECTIVES = ("Shocking", )
    CAPABILITIES = ("overwhelm an opponent's defense routines",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add a burn status to the children.
        attack.fx.children[0].children.append(
            geffects.IfEnchantmentOK(
                geffects.OverloadStatus,
                on_success=(
                geffects.AddEnchantment(geffects.OverloadStatus, dur_n=2, dur_d=4, anim=geffects.OverloadAnim),),
            )
        )


class Plasma(Singleton):
    name = "Plasma"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.2
    POWER_MODIFIER = 1.0

    ADJECTIVES = ("Plasma", )

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Plasma scatters on a successful hit, but travels in a coherent beam. This means it's a scatter weapon
        # that can potentially critical hit. This also means it loses the ReflexSave never-miss ability.
        attack.fx.children[0].scatter = True


class PoisonAttack(Singleton):
    name = "Poison"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 2.0

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Add a disintegration status to the children.
        attack.fx.children[0].children.append(
            geffects.IfEnchantmentOK(
                geffects.Poisoned,
                on_success=(
                    geffects.ResistanceRoll(stats.Craft, stats.Ego, roll_mod=25, min_chance=15,
                                            on_success=(geffects.AddEnchantment(geffects.Poisoned, dur_n=2, dur_d=4,
                                                                                anim=geffects.InflictPoisonAnim),)
                                            ),
                ),
            )
        )


class Scatter(Singleton):
    name = "Scatter Shot"
    MASS_MODIFIER = 1.0
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 1.2
    POWER_MODIFIER = 1.0

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Change the damage type to scatter. That was easy.
        attack.fx.children[0].scatter = True
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()
        attack.fx.can_crit = False


class Smash(Scatter):
    # Mostly the same as Scatter, but better name for melee. Also if you charge with a Smash weapon you can get a
    # critical hit.
    name = "Smash"

    CAPABILITIES = ("cause damage even on a glancing hit",)

    @classmethod
    def modify_basic_attack(cls, weapon, attack):
        # Change the damage type to scatter. That was easy.
        attack.fx.children[0].scatter = True
        attack.fx.defenses[geffects.DODGE] = geffects.ReflexSaveRoll()


class SwarmFire2(Singleton):
    # Default fire action fires at multiple targets.
    name = "Swarm Fire 2"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.2
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 2.5
    SWARM_VALUE = 2

    @classmethod
    def replace_primary_attack(cls, weapon):
        base = weapon.get_basic_attack(name='Swarm x{}'.format(cls.SWARM_VALUE), ammo_cost=cls.SWARM_VALUE,
                                       targets=cls.SWARM_VALUE, attack_icon=9)
        return [base, ]


class SwarmFire3(SwarmFire2):
    # Default fire action fires at multiple targets.
    name = "Swarm Fire 3"
    MASS_MODIFIER = 2.0
    VOLUME_MODIFIER = 1.5
    COST_MODIFIER = 3.5
    POWER_MODIFIER = 3.5
    SWARM_VALUE = 3


class VariableFire2(Singleton):
    # This weapon can do Burst x2 fire in addition to single fire
    name = "Variable Fire 2"
    MASS_MODIFIER = 1.2
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.0
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks(cls, weapon):
        base = BurstFire2.replace_primary_attack(weapon)[0]
        return [base]


class VariableFire3(Singleton):
    # This weapon can do Burst x3 fire in addition to single fire
    name = "Variable Fire 3"
    MASS_MODIFIER = 1.3
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 2.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks(cls, weapon):
        base = BurstFire3.replace_primary_attack(weapon)[0]
        return [base]


class VariableFire4(Singleton):
    # This weapon can do Burst x4 fire in addition to single fire
    name = "Variable Fire 4"
    MASS_MODIFIER = 1.4
    VOLUME_MODIFIER = 1.0
    COST_MODIFIER = 3.0
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks(cls, weapon):
        base = BurstFire4.replace_primary_attack(weapon)[0]
        return [base]


class VariableFire5(Singleton):
    # This weapon can do Burst x5 fire in addition to single fire
    name = "Variable Fire 5"
    MASS_MODIFIER = 1.5
    VOLUME_MODIFIER = 1.1
    COST_MODIFIER = 3.5
    POWER_MODIFIER = 1.0

    @classmethod
    def get_attacks(cls, weapon):
        base = BurstFire5.replace_primary_attack(weapon)[0]
        return [base]

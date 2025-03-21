import random

from gears import tags
import pbge
from . import geffects
from pbge.scenes import animobs
from . import base, stats


class Damage(object):
    BOOM_SPRITES = list(range(7))

    def __init__(self, camp, hit_list, penetration, target, animlist, hot_knife=False, is_brutal=False,
                 can_be_divided=True, affected_by_armor=True, critical_hit=False):
        self.camp = camp
        self.hit_list = hit_list
        self.penetration = penetration
        self.overkill = 0
        self.damage_done = 0
        self.animlist = animlist
        self.hot_knife = hot_knife
        self.is_brutal = is_brutal
        self.can_be_divided = can_be_divided
        self.affected_by_armor = affected_by_armor
        self.critical_hit = critical_hit
        self.destroyed_parts = list()
        self.target_root = target.get_root()
        self.operational_at_start = self.target_root.is_operational()
        self.mobile_at_start = hasattr(self.target_root,
                                       "get_current_speed") and self.target_root.get_current_speed() > 0
        self.chain_reaction = list()
        self.allocate_damage(target)

    def ejection_check(self, target):
        # Record the pilot/mecha's team
        # Check if this is an honorable duel. If so, ejection almost guaranteed.
        # Search through the subcoms for characters.
        #  Each character must eject or die.
        #  Head mounted cockpits easier to eject from.
        #  Bad roll = character takes damage on eject, and may die.
        #  Terrible roll = character definitely dies.
        #  Remove the pilot and place offsides.
        # If any characters were found, set a "Number of Units" trigger. (Is this necessary? Why not do this at end of "inflict"?
        pass

    def apply_damage(self, target, dmg):
        """Function name inherited from GH2.1"""
        # First, make sure this part can be damaged.
        # Calculate overkill- damage above and beyond this part's capacity.
        # Record the damage done
        # If the part has been destroyed...
        #  * Moving up through part and its parents, set a trigger for each
        #    destroyed part.
        #  * Add this part to the list of destroyed stuff.
        # Do special effects if this part is destroyed:
        # - Modules and cockpits do an ejection check
        # - Ammo can cause an explosion
        # - Engines can suffer a critical failure, aka big boom
        ok_at_start = target.is_not_destroyed()
        dmg_capacity = target.max_health - target.hp_damage
        if dmg > dmg_capacity:
            self.overkill += dmg - dmg_capacity
            dmg = dmg_capacity
        if not isinstance(target, base.Armor):
            self.damage_done += dmg
        target.hp_damage += dmg
        if ok_at_start and target.is_destroyed():
            self.destroyed_parts.append(target)
            if hasattr(target, 'on_destruction'):
                self.chain_reaction.append(target.on_destruction)

    def _list_thwackable_subcoms(self, target):
        """Return a list of subcomponents which may take damage."""
        return [p for p in target.sub_com if p.is_not_destroyed()]

    def real_damage_gear(self, target, dmg, penetration):
        """Function name inherited from GH2.1"""
        # As long as we're not ignoring armor, check armor now.
        #    If this is the first dmg iteration and target isn't root, apply parent armor.
        #    Query the gear for its armor.
        #    Reduce damage by armor amount, armor suffers staged penetration.
        # If any damage left...
        #    Apply damage here, or split some to apply to subcoms.
        #    1/23 chance to pass all to a single subcom, or if this gear undamageable.
        #    1/3 chance to split half here, half to a functional subcom.
        #    Otherwise apply all damage here.
        if self.affected_by_armor:
            armor = target.get_armor()
            if armor and armor.is_not_destroyed():
                # Reduce penetration by the armor's rating.
                tar = armor.get_armor_rating()
                if tar:
                    penetration -= tar
                # Armor that gets used gets damaged.
                dmg = armor.reduce_damage(dmg, self)

            if penetration <= 0 and self.hot_knife and dmg > 0:
                # A hot knife attack doesn't get stopped by armor, but it does get
                # its damage reduced a fair chunk.
                denom = max(45 + penetration, 5)
                dmg = max(int(dmg * denom // 50), 1)
                penetration = 1

        if dmg > 0 and (penetration > 0 or not self.affected_by_armor):
            # A damaging strike.
            potential_next_targets = self._list_thwackable_subcoms(target)
            if not self.can_be_divided:
                # All damage to this part.
                self.apply_damage(target, dmg)
            elif random.randint(1, 23) == 1 or not target.can_be_damaged():
                # Assign all damage to a single subcom.
                if potential_next_targets:
                    self.real_damage_gear(random.choice(potential_next_targets), dmg, penetration)
            elif random.randint(1, 3) == 3 and potential_next_targets and dmg > 2:
                # Half damage here, half damage to a subcom.
                dmg1, dmg2 = dmg // 2, (dmg + 1) // 2
                self.apply_damage(target, dmg1)
                self.real_damage_gear(random.choice(potential_next_targets), dmg2, penetration)
            else:
                # All damage to this part.
                self.apply_damage(target, dmg)

    def _get_crash_damage(self):
        if hasattr(self.target_root, "mmode") and self.target_root.mmode is pbge.scenes.movement.Flying:
            return 3, 8
        else:
            return 2, 6

    def allocate_damage(self, target):
        """This damage is being inflicted against a gear."""

        # X - Initialize history variables
        # X - Check on the master and the pilot- see if they're currently OK.

        # Start doling damage depending on whether this is burst or hyper.
        #   Call the real damage routine for each burst.
        for h in self.hit_list:
            self.real_damage_gear(target, h, self.penetration)

        # Dole out concussion and overkill damage.
        if self.overkill:
            torso = None
            for m in self.target_root.sub_com:
                if isinstance(m, base.Torso) and m.is_not_destroyed():
                    torso = m
                    break
            if torso:
                self.apply_damage(torso, self.overkill)

        # A surrendered master that is damaged will un-surrender.
        # Check for engine explosions and crashing/falling here.
        # Give beings experience to vitality.
        if self.damage_done > 0 and isinstance(self.target_root, base.Being):
            self.target_root.dole_experience(self.damage_done, stats.Vitality)

        # Record the animations.
        random.shuffle(self.BOOM_SPRITES)
        if self.damage_done > 0:
            if self.damage_done > self.target_root.scale.scale_health(16, self.target_root.material):
                num_booms = 5
            elif self.damage_done > self.target_root.scale.scale_health(12, self.target_root.material):
                num_booms = 4
            elif self.damage_done > self.target_root.scale.scale_health(7, self.target_root.material):
                num_booms = 3
            elif self.damage_done > self.target_root.scale.scale_health(3, self.target_root.material):
                num_booms = 2
            else:
                num_booms = 1
            for t in range(num_booms):
                myanim = geffects.SmallBoom(sprite=self.BOOM_SPRITES[t], pos=self.target_root.pos,
                                            delay=t * 2 + 1,
                                            y_off=-self.camp.scene.model_altitude(self.target_root,
                                                                                  *self.target_root.pos))
                self.animlist.append(myanim)
            if self.critical_hit:
                self.animlist.append(animobs.Caption(
                    "Critical!", pos=self.target_root.pos,
                    y_off=-self.camp.scene.model_altitude(self.target_root, *self.target_root.pos),
                    color=pbge.TEXT_COLOR
                ))
            myanim = animobs.Caption(str(self.damage_done),
                                     pos=self.target_root.pos,
                                     y_off=-self.camp.scene.model_altitude(self.target_root, *self.target_root.pos))
            self.animlist.append(myanim)
            if self.operational_at_start and not self.target_root.is_operational():
                myanim = geffects.BigBoom(
                    pos=self.target_root.pos, delay=num_booms * 2,
                    y_off=-self.camp.scene.model_altitude(self.target_root, *self.target_root.pos),
                    sound_fx=self.target_root.material.DESTROYED_SOUND_FX or "hq-explosion-6288.ogg"
                    )
                self.animlist.append(myanim)
            else:
                # Record the destroyed parts, as appropriate.
                for dp in self.destroyed_parts:
                    if dp.REPORT_DESTRUCTION:
                        self.animlist.append(pbge.scenes.animobs.Caption(
                            "{} Destroyed!".format(dp), pos=self.target_root.pos, delay=num_booms * 2,
                            y_off=-self.camp.scene.model_altitude(self.target_root, *self.target_root.pos)
                        ))

        else:
            for t in range(2):
                myanim = geffects.NoDamageBoom(sprite=self.BOOM_SPRITES[t],
                                               pos=self.target_root.pos, delay=t * 2 + 1,
                                               y_off=-self.camp.scene.model_altitude(self.target_root,
                                                                                     *self.target_root.pos))
                self.animlist.append(myanim)

        if self.chain_reaction:
            for cr in self.chain_reaction:
                cr(self.camp, myanim.children)

        if isinstance(self.target_root,
                      base.Mecha) and self.mobile_at_start and self.target_root.get_current_speed() == 0 and self.target_root.is_operational() and self.target_root.mmode is not tags.SpaceFlight:
            # Crash time!
            myinvo = pbge.effects.Invocation(
                fx=geffects.DoCrash(
                    children=(geffects.DoDamage(*self._get_crash_damage(), scatter=True, is_brutal=True),)),
                area=pbge.scenes.targetarea.SingleTarget()
            )
            myinvo.invoke(self.camp, None, [self.target_root.pos, ], myanim.children)

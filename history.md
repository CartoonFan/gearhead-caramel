* GearHead Campaign now has method for loading major NPCs
* Memo browser is now a widget, and memos can create custom widgets
* Terrset now actually draws border
* Added new eyecatch screen by Sierra Bravo
* Fixed the map scrolling problem at the edges and corners of the map
* Fixed a longstanding bug with Architecture.draw_fuzzy_ground
* Added PartlyUrban map generator
* Random map room placement should now be more robust
* Floor borders now based on priority, not keyed to specific terrain pairs
* Changed the way custom factions are stored and accessed in Scenario Creator
* Scenario editor now does basic error checking before compiling
* Focus mode added to scenario editor physical view
* Added identifier, literal scenario creator variable types
* Justify property now works with text entry and text editor widgets
* ScenarioCreator output is pretty printed with yapf if available
* Refactored the ScenarioCreator compiler
* Text editor widget now a column of text entry widgets; cursor movement works properly
* Text entry widget now has movable cursor
* Scenario Creator has subplot loader utility which passes all element aliases
* Scenario Creator builds the world before loading subplots
* Possibly fixed the problem with pygame.quit() not really quitting
* Scenario creator variables return their own widgets; may return a list of widgets rather than a single widget
* Elements defined by BluePrints get their own unique ID
* PlotEditor renamed to ScenarioCreator
* Scenario variable types all have their own classes now
* The map focus cannot leave the bounds of the map

v0.821 March 31 2021
* Fixed the loverboy beard error
* ScrollColumn widgets may force focus
* ScrollColumn widgets act like menus when accessed by keyboard
* Widgets may provide their own keyboard handling
* Added mapcursor module; can be used to move & target invocations via the keyboard
* Holding shift with tab will select the previous widget

v0.820 March 13 2021
* Added the Ice Wind mecha family
* Added more portrait bits
* Update trigger automatically updates plots
* Trigger check during campaign construction will no longer cause crash
* Left and right keys may be used to browse memos
* Campaign now has get_memos method
* Challenges can have memos integrated into them
* Fixed so many bugs. How many bugs? Lost track. Lots and lots of bugs.
* Active Challenges are listed in GHNarrativeRequest
* Added Challenges and Resources
* Right clicking on combat radio button will bring up library menu
* Widgets may now be given an "on_right_click" property
* Radio buttons widget now takes dicts to describe the button properties
* Fixed portrait placement bug with lancemate menu item
* Phasing out IgniteAmmo attribute; to be replaced by BurnAttack attribute
* Ammo may now explode if destroyed
* Destruction of important parts will be displayed
* Added Antidote usable item and Cure Poison ability for Medicine skill
* Added Agonize, PoisonAttack attack attributes

v0.810 November 30 2021
* Gears may have individual campdata dicts which don't get exported when campaign is finished
* Noncombatants flee from combat
* Added "FAINT" trigger
* Fixed bug in which GearHeadCampaign all_plots method did not return metro plots
* Added automatic update and expiration for plots
* Added automatic rumor/info offer/memo option for plots
* You can now edit your PC's name, portrait, and gender from the FieldHQ
* Gender is now completely customizable

v0.800 September 30 2021
* Campaign save file compatibility probably broken; character save files are okay
* PlotCreator blueprints now automatically sorted
* You can start a newly compiled scenario without restarting the game
* PlotCreator updated to use campfeatures utilities
* MissionBuilder no longer needs environment parameter, since this info is included in GearHeadArchitecture subclass
* Added some hand-painted portrait bits
* Added ArenaRules scene attribute
* Character tags include the tags of that character's faction
* Lancemates will not rejoin the party if they currently dislike the PC
* Lancemate reaction score will decrease if that lancemate is incapacitated or loses their mecha
* Unfavorable NPCs limit their conversation options
* Added standardized in-town recovery/lance development loader
* Added militia defense if PC attempts to enter an unfavorable town
* Added standardized world map encounter handler
* The Terran Defense Force mission in Wujung can now be rejected, and stops being offered after 20 wins
* Fighting a mission against a faction may make that faction unfavorable to the PC
* Added is_favorable_to_pc, is_unfavorable_to_pc methods to GearHeadCampaign
* Added Campaign go method
* Singletons should return the intended str() value

v0.700 June 13 2021
* Added PlotCreator scenario editor
* Popup menu can now take custom width and height
* Colors have been added to the SINGLETON_REVERSE dict
* Fixed problems with choose lifepath display
* The map viewer now uses a per-tile message ticker
* Added "View Hotkeys" to combat popup menu
* DZD roadedge plots will stop rumors after the road is cleared
* Added "center on party" to exploration menu
* Fixed crash when prop goes haywire
* Increased threat value of hunter synths

v0.620 April 9 2021
* Added pilot suit portrait bits by LordErin
* Added some more opening scenarios
* Fixed bug when running ghcaramel from a different directory
* Combat hotkeys can be set by pressing Alt + Key when using desired action, or by editing config file
* Combat popup menu added if right mouse button clicked
* Alert will now return the event that ended the alert display
* MissionBuilder mission now checks scene environment for legal mecha
* Added a local feature to each village in DeadZone Drifter
* Increased size of standard dungeon level to 65x65
* SceneConnectors now take narrative request as first parameter
* Fixed fullscreen lockup on Linux
* Added DuckTerrain, duck_dict option for TerrainSet
* Robot NPCs from GH1 will be Metal, not Meat
* Lancemates from previous adventures may show up in DeadZone Drifter

v0.612 January 13 2021
* Added the CNA-15 Century mecha
* Fixed bug with importing GH1 characters

v0.611 January 4 2021
* Added a description to the DeadZone Drifter adventure module
* Updated the README.md file for the first time in ages
* Packaging system changed from PyInstaller to cx_Freeze, fixed Windows NumPy issue
* Added Adventure Module selection menu
* Moved faction score from a Character property to an Egg property
* Color menu will recognize identical colors now
* Reworked the way scatter damage scatters
* Added Eggzaminer to dev mode
* Fixed Egg ejection bug
* Fixed a lot of GH1 import bugs
* Fixed a problem with asynchronous IO and menus
* Lancemates and major NPCs should be imported correctly from GH1
* Cybertech skill imported correctly from GH1
* Vadel's hover jets are now bigger and integral
* Zerosaiko mass driver improved
* Changed the formula for armor damage absorption
* Reduced chemthrower chem usage
* Scene viewer may now get postfx function called after normal map rendering
* Fixed bug with LancematePrep cutscene element
* PC can bring mecha, stash with them between adventures
* Updated the Winter Mocha scenario
* Python scripts in user content folder will be loaded at startup

v0.600 December 27 2020
* DeadZone Drifter scenario now has a conclusion
* Monsters may get a different number of actions per round
* Fixed serious CharacterMover bug
* Mecha scale beings have their Mobility calculated correctly
* Burst fire bonus applied to accuracy, not to hit roll
* XP for destroying enemy is capped at 500
* Added skill trainers
* CharacterMover will not move NPC back to original scene if NPC gets moved away from dest scene to another scene first
* Haywire now correctly works on human-scale robots
* Added consumable items
* Added more cyberware from GH1, GH2
* Combatants who are out of visual range and don't know where to go next will deactivate
* Lancemates moved by CharacterMover will be removed from party and re-added if possible at end of plot
* Potential lancemates can tell you a little bit about their skills
* Most random lancemates will start with lower renown, but may have extra skills
* Added merit badges for GH1 PCs who defeated Cetus, Ladon
* Shops without a defined faction will use the faction of the town they're in

v0.560 November 29 2020
* Added Kerberos storyline to DeadZone Drifter
* Can now load same image in transparent and non-transparent versions
* Monsters can power their own weapons
* Can now flee from combat by using an exit
* Attackers will move a bit so you can tell who's attacking
* Added AttackInvocation
* Added COMBATROUND script trigger
* Added error message to gear loader if unknown command encountered
* Activated the BioCorp biotech hunting mission
* Added missing formatting for many tarot memos
* Nerf Charge Attack, which was incorrectly not rescaled during the previous health and damage scale adjustment in 0.542.

v0.551 October 20 2020
* Added auto_save default to data/config_defaults.cfg
* Reduced Corsair's heavy rocket pod to 4 rockets, but bigger ones

v0.550 October 15 2020
* Added Ran Magnus Mecha Works
* Added stretchy_screen config file option
* Added Pro Duelist Association faction
* Missile salvos drain target's stamina faster than other attacks
* Removed redundant (and outdated) are_ally_factions, are_enemy_factions methods from GearHeadCampaign
* Improve success rate and casting cost of LISTEN TO MY SONG.
* Fill out Mecha Graveyard adventure.
* Highlight the tile where we completely consume one action point when showing the trail of a move or move-attack.
* Fix the missing Haywire attack on Phoenix L-Cannon
* Added unique EWar system, Necromatix. Start doing those sidequests for a chance to get it!
* Fix bug that would prevent deadzone town plot from advancing if you do "Recon by Force" mission.
* Fix bug where we mistakenly give odds for hitting a dead mecha when its ally is standing on top of it.
* Some particular unique shops might now sell parts of, or even complete, champion mecha.
* Fix bug where mechas you own suddenly disappear after you take out their engines or torso in the mecha engineering terminal.
* More body options.
* Implement 'Create New Mecha' in out-of-game mecha editor.
* Add batteries to Musketeer.
* Champions that upgrade their missiles now make sure it fits in the largest Launcher.
* Memos now include location information as appropriate.
* Made missiles more accurate, cheaper, and not shield-blockable (now only interception and dodge work against missiles), and increase missile quantities on almost every mecha.
* Intercept weapons are now much less effective, but you can now stack several to improve your interception chances.
* Added some dungeon decor
* Destroyed mecha will be announced at end of combat
* Slightly increased and curved damage
* Missions change your faction score for both enemy and allied factions
* Only one LMDEV plot can be active at once
* Added GET trigger when an item is picked up

v0.542 August 18 2020
* Added Mecha Graveyard adventure
* Adjusted mass, health, and damage scaling
* Added crates and other item-storage waypoints
* Mecha melee damage bonus also toned down
* Melee attack multiple hits toned down
* Added Treasure gear type
* Dropped items may be picked up by clicking on tile where PC is standing
* Lancemates may now trade personal inventory items
* Monsters use a different target selection routine
* Got rid of annoying short hallways from PackedBuilding map generator
* Melee weapons can have the Multi Wielded attribute, which lets you attack with multiple instances of that weapon.
* Personal scale combat gives more direct XP than mecha scale combat
* Added dungeon generator
* Random NPCs should get a faction-appropriate job
* Standardized the lancemate hiring cost
* Tooltips may be several lines of text, if needed

v0.541 August 10 2020
* Added Phoenix and Secutor mecha
* Modified some mecha designs
* Added Brutal attack attribute that causes extra damage to armor
* Melee attacks have a chance to cause multiple hits
* Fixed autosave config menu option
* Melee weapons can have the Ignites Ammo attributes, which replaces Burn for melee weapons, and reduces armor of enemy mecha, preventing them from using ballistic and missile weapons.
* Melee weapons can have the Drains Power attribute, which greatly reduces the power supplies of enemy mecha, preventing them from using energy and beam weapons.
* Heavy actuators provide melee damage bonus to the module they're installed in
* Melee attacks now get a damage bonus
* Attacking a model will activate it
* When combat starts, all nearby teams are activated
* Added advanced EW programs
* Added the Solar Navy faction
* Vikki now gives a brief tutorial about mecha and pilot stats
* Combat AI for enemies updated; target choice is no longer random or permanent
* Random NPCs should now have consistent mecha colors
* Tarot cards marked as UNIQUE should now be unique (unless generated during play)
* Enemy factions in missions may bring in allies iff all faction members are busy
* DZD town threat rank increases as you move deeper into the dead zone
* Fixed FactionComputer password bug

v0.540 July 31 2020
* All towns now have a tarot scenario
* Added Quality of Life indicator to all towns
* Highway encounters won't clutter the road with trees or other obstacles. It's supposed to be a road.
* Fixed the disappearing enemy commander bug
* One on One Champion Fight now uses faction leader if possible
* Town prosperity now affects shop items
* Larger movement systems are now lighter (two size-3 Wheels is heavier than a size-6 Wheels) but more expensive.
* Slasher champions upgrade their plain shields to beam shields.
* Raider champions upgrade their sensors (to take advantage of their weapon increased range) and may also gain Overchargers.
* Tone down EnergyWeapon prices.
* Add Explodium champion. Boom!
* Major NPCs now always get customized mecha
* Dungeons will clean out their dead daily
* Combatant NPCs get starting equipment
* Added Monster gear type
* Improved visibility of Green Boarding Chute
* Added storage scene to GearHeadCampaign
* Tarot card transformation now passes on default elements from alpha card.
* Add Overchargers.
* Champion mecha are special, so they should be easier to salvage.
* Increase Charge cost even more: treat it like a ranged weapon.
* Added Daum, Vadel mecha
* Melee weapons blocked by energy weapons or beam shields take damage
* Added beam shields
* Added indie plots
* Renamed the tarot card modules
* More variety in road stop garages.
* In combat, default to the fastest movemode of your mecha.

v0.530 June 8 2020
* Revamped shop interface
* Style rules may be turned on or off in the portrait editor
* Added style, nostyle properties to PortraitBits
* Adjusted mecha cost, random mecha unit generation
* Modified the volume of missiles
* Added Razer, Petrach, Wolfram mecha
* Character creator allows selection of local mecha for green zone, dead zone
* Extremely high Mobility scores toned down
* Fixed crash when pygame.mixer fails to load
* Fixed some mission problems
* Added Memory records to Relationships
* Random NPCs start with a narrower range of stat points

v0.520 May 16 2020
* Mechanical Tarot scenario generator improved and expanded
* Can't enter a mecha combat mission if you have no mecha
* No reason for Gyroscopes to not be integral by default, so now they are integral by default
* Fixed lake room map generator crash
* You can no longer install characters into mecha cockpits, which can lead to broken savefiles.
* You might now occassionally come across specially-named mecha on some mission objectives. If you're lucky you might even salvage them and their special modified equipment.
* Party removed to a safe location when plot controlling temporary scene ends
* Added longform mecha info panel
* Invocations now consistently show their casting costs.
* Can now remove all modules from a mecha without crashing the game.
* Show more info on items in Field HQ and Shop.
* Improved Haiho slightly.
* More movement systems for sale.
* Cyberware!
* Argh. Maybe now wall decor will stop blocking doors?
* Fixed json files not loading in Python 3.7+

v0.511 May 1 2020
* May scroll up/down or use up/down keys to page through all combat modes
* EWSystems now show their programs, Engines now show their ratings in their info panels when buying or choosing parts to install
* Added SkillBasedPartyReply and TagBasedPartyReply
* Add Take Cover action to Stealth and Spot Behind Cover to Scouting
* Spot Weakness is now a Science skill
* Negotiation now lets you recover lancemate Mental by spending your own Stamina
* Performance now gives weaponized singing in combat.  LISTEN TO MY SONG
* SensorLock negates the SensorRange attack modifier
* Added StatValuePrice effect price
* GearHeadCampaign now has make_skill_roll method
* Added extra cost factor for high Accuracy, Penetration weapons
* Increased Charge cost modifier to 2.5
* Hopefully prevented rooms from being completely blocked off
* Add an AI Assistant program, and a C99 AI Assistant EW System
* Fixed a bug in lance "friendly duel" challenge
* Armor, Sensors, Wheels, Hover Jets, Heavy Actuators now show their size, material, and integral-ness in their displayed name
* Enchantments can now modify to-hit based on cover
* Enchantments can be dispelled by application of other enchantments
* Added Wujung Tires
* Solitary walls will be correctly displayed
* Wall decor should not be placed on same tile as a door
* Added Musketeer, Ultari, Haiho mecha
* Mecha missions now feature a variety of room types
* Enchantments can be dispelled on movement
* Added tidy_enchantments method to GearHeadScene
* Added LinkedFire attack attribute
* Many non-weapon gears can now be integral (which makes them non-removable in-game, but gives volume reduction and possible cost and mass reduction).
* Integral weapons can no longer be removed in-game, and are also shown as integral.
* Field of view will be updated after charge attacks
* Cannot give stash items to mecha that don't belong to you

v0.510 April 19 2020
* Range attack modifier will now display "Too Far" or "Too Close"
* Gauss Cannons now use Perception rather than Reflexes
* Added HostilityStatusBlock
* Fixed ORPH_SOCIABLE lifepath node
* Added Kojedo mecha
* No experience award for missions you don't even attempt
* Owner indicated for all items in FHQ
* Cannot access inventory of mecha that don't belong to you
* Fixed crash from TargetIsDamaged AI targeter
* Added disable_audio_entirely troubleshooting config option
* Game still loads if audio device fails
* Fixed recovery plot when lancemate dies
* Fixed weird PFOV bug (at least one, hopefully two)
* Repaired the Repair skill
* Fixed crash from targeting with Flail weapons
* Exhaustion happens sooner in combat, has bigger penalties
* Adjusted renown rewards
* Fixed random NPCs always combatants bug
* Changed "Dominate Animal" skill to "Wildcraft"

v0.500 April 12 2020
* Reduced weapon volume
* Added mecha editor, mecha browser
* Added Haywire, Overload attack attributes
* Effects, combat now grant experience, skill experience
* Switched to Python3
* Added restore method which refreshes gears, returns repair/reload cost (gears/base.py)
* Immobility modifier separated from speed modifier (gears/geffects.py)
* Added reflexive pronoun to gender
* Randmaps plasma now scales to be close to map size
* Reworked the menu unit for better mouse support
* Conversation border is now set by campaign
* You can now ask lancemates to leave the party
* Added road map to DeadZone Drifter
* Fixed bug with Alert, AlertDisplay locking
* NPCs move during exploration
* Added dev_mode_on config option (main.py)
* Fixed bug with random NPCs getting wrong job skills (gears/selector.py)
* Added training interface (game/fieldhq/training.py)
* Moved all plot-defining units to game/content/ghplots
* Pilot attacks no longer included in mecha attack list (gears/base.py)
* Invocations UI now responds to mousewheel scroll, key commands (game/invoker.py)
* Attack UI will remember the last weapon used (game/combat)
* Changed local_teams to regular dict (pbge/scenes)
* Fixed recursion problem with deepcopy (gears/base.py)
* Added ammo count to attack widget (game/combat/targetingui.py)
* Fixed crash when using color menu with PyGame 1.92+ (game/cosplay.py)
* Incorporated caramelcolor extension module (pbge/image.py)
* Scale, material passed as defaults to children by text gear loader (gears/__init__.py)
* Widgets only respond to clicks if first widget this tick (pbge/widgets.py)
* Added fieldHQ and backpack (game/)
* Added character generator (game/chargen)
* Added services (game/services.py)
* Currently visible area indicated (pbge/scenes/viewer.py)
* NPC relationship with PC now tracked by Relationship object (gears/relationships.py)
* Added merit badges (gears/meritbadges.py)
* Added jobs system (gears/jobs.py)
* Can activate waypoints via the popup menu (game/exploration.py)
* Random mecha units get random team color if no faction (gears/selector.py)
* Standardized GearHead architectures (game/content/gharchitecture.py)
* Added cosplay module (game/cosplay.py)
* Portrait generator now used by VisibleGear class (gears/base.py)
* Gender may be defined as dict in design files (gears/base.py)
* Added gender (gears/gender.py)
* Player folder now has an image subfolder (gears/)
* Images now have a search path (pbge/image.py)
* Mechanical Tarot can generate causality chains (gears/mechtarot.py)
* Added portraits module (gears/portraits.py)
* Added tarot to GearHeadCampaign (gears/)
* HeightfieldPrep can set maximum levels of lowground, highground (pbge/randmaps/prep.py)

v0.130  June 17, 2018
* Added Joust, Trailblazer mecha
* Added charge attacks (gears/geffects.py)
* Added BurnAttack status effect (gears/attackattributes.py)
* Repair will remove appropriate enchantments (gears/geffects.py)
* Added enchantments
* NPCs will use skills in combat as appropriate (game/combat/aibrain.py)
* Added Search invocation (gears/stats)
* Added Stealth invocation (gears/stats)
* Centralized the move-then-invoke code (game/combat)
* Default offers automatically added to conversation (pbge/dialogue)
* VisibleGears have a shadow (gears/base.py)
* PlaceableThings may be hidden (pbge/scenes)
* Exploration right click menu now works properly (game/exploration.py)
* Combat skill button only shows up if PC has usable skills (game/combat)

v0.120  March 9, 2018
* Version indicated on title screen (main.py)
* Repair skills working (gears/stats.py)
* Added skill invocations (gears/stats.py)
* Added generic invocation targeting UI (game/invoker.py)
* Head mounted sensors get a range bonus (gears/base.py)
* Added ChemThrower, Chem gears (gears/base.py)
* Ammo cost, mass, volume now affected by attributes (gears/base.py)
* Added names_above_heads config option (pbge/scenes/viewer.py)
* Added option to disable music (pbge/)
* The Esc key will now bring up an options menu in-game (game/)
* Added configuration editor (game/configedit.py)
* Reduced power cost of energy, beam weapons (gears/base.py)
* Added Intercept, Flail, Defender, ConeAttack, LineAttack
  attack attributes (gears/attackattributes.py)
* Added Parry, Intercept defenses (gears/)
* Successfully blocking with shield damages shield, costs 1 stamina (gears/)
* Attack invocations record "thrill power" (gears/geffects.py)
* Modules now have attacks (gears/base.py)
* Shields cause aim penalty for weapons in same arm (gears/base.py)
* Head mounted cockpits provide +10 Mobility (gears/base.py)
* Fixed crash when player mecha runs out of attacks (game/combat)
* Added random mecha selector (gears/selector.py)
* Improved the enemy AI (game/combat/aibrain.py)

v0.111  February 15, 2018
* Fixed a dialogue bug in one of the mocha encounters
* Random pilots get random personalities (gears/__init__.py)

v0.110  February 14, 2018
* Enabled loading screens (pbge)
* Added Props (gears/base.py)
* PC should always count as lead party member (game/exploration.py)
* Rewrote dialogue generator to dynamically create each exchange (pbge/dialogue)
* Added cutscenes (pbge/cutscene.py)
* Rooms may be saved for use by scripts (gears/__init__.py)
* Fixed place_party bug (gears/__init__.py)
* Centralized the start_conversation code (game/ghdialogue)
* Fixed free_pilots bug (gears/base.py)
* Movement into range indicated in targeting UI (game/combat/targetingui.py)
* Centralized info display code (gears)
* Added Scatter damage type (game/geffects.py)
* Clicking enemy opens attack menu (game/combat/movementui.py)
* Music is preloaded when scene entered (pbge,game/exploration.py)
* Added OddsInfo block (gears/info.py)
* Melee, Energy attacks ignore target speed (gears/base.py)
* Added Mental, Stamina, and Power (gears/base.py)
* Blast attacks cannot be dodged (gears/geffects.py)
* Energy weapons cut through armor like a hot knife (gears/base.py)
* Added Accurate, BurstFire, Blast attack attributes (gears/attackattributes.py)
* Named waypoints indicated on mouseover (game/exploration.py)
* Border transparency now uses same alpha as GearHead1 (pbge)
* Combat starts when PC moves within half sensor range (game/exploration.py)
* Targeting info shows top three modifiers (game/combat/targetingui.py)
* "card_" portraits contain sprite (game/ghdialogue/gdview.py)
* Images may now have custom frames (pbge/image.py)
* Fixed bugs with Overwhelmed, Target Movement modifiers (gears/geffects.py)
* The InfoPanel is now modular (gears/info.py)
* Added Plot.activate, Plot.deactivate methods (pbge/plots.py)
* Fixed party walking order during exploration bug (game/exploration.py)
* Fixed move-then-fire bug (game/combat/targetingui.py)

v0.100  December 23, 2017
* First public release
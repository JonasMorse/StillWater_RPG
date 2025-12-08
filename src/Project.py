"""
StillWater RPG — Full StillWater Version (Option B) — Stat-based Combat v2
- Stats now meaningfully affect combat:

"""

import random
import time
import os
import sys
# -------------------------
def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def slow_print(text, delay=0.02):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

def short_pause(secs=0.5):
    time.sleep(secs)

def divider():
    print("\n" + "=" * 60 + "\n")

def hp_bar(current, maximum, length=24):
    current = max(0, int(current))
    maximum = max(1, int(maximum))
    filled = int(length * current / maximum)
    empty = length - filled
    return "[" + "█"*filled + "-"*empty + f"] {current}/{maximum}"

def prompt_choice(prompt, options):
    """Prompt until user enters a valid option from options (list of strings)."""
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print("Invalid choice. Try again.")

# -------------------------
# Visuals & ASCII Art
# -------------------------
def show_camp_map():
    print("""
    STILLWATER CAMP MAP
    ┌───────────────────────────────────────────────┐
    │ Tents (T)      Jori          │ Training (R)  │
    │ Work Area (W)  Vell          │ Guard Tower(G)│
    │ Mess Hall (M)  Alva/Ilhera   │ Chapel (C)    │
    └───────────────────────────────────────────────┘
    """)

def player_art():
    print("""
      O
     /|\\
     / \\
    """)

def enemy_art(enemy_name):
    print(f"""
       ALERT! {enemy_name} appears!
          ,     \\    /      ,
         / \\    )\\__/(     / \\
        /   \\  (_\\  /_)   /   \\
   🐾  ____  \\__/_\\__/ __ / ____  🐾
    """)

def ability_effect_visual(ability_name):
    effects = {
        "Spite Strike": "*--->⚔️--->*",
        "Wraith Step": "~~~oO~~~",
        "Scout's Eye": "👁️✨",
        "Swift Hands": "-->>✋>>--",
        "Shimmering Insight": "✨💥✨",
        "Fragmented Heart": "<><><💔><><>",
        "Hammer Swing": "💥🔨💥",
        "Enduring Stance": "[🛡️] Stance",
        "Reflective Shard": "/\\/⚡\\/\\",
        "Crystalline Bind": "🔗❄️🔗"
    }
    return effects.get(ability_name, ">>>*<<<")

def warden_visual():
    print(r"""
                   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀
                   ⠀⠀⠀⠀⠀⠀⠀⣴⣿⡿⠛⠉⠉⠛⢿⣿⣦⠀⠀⠀⠀⠀⠀
                   ⠀⠀⠀⠀⠀⠀⣼⣿⠋⠀⠀⠀⠀⠀⠀⠙⣿⣷⠀⠀⠀⠀⠀
                   ⠀⠀⠀⠀⠀⣼⣿⠃⠀⠀⣀⣀⣀⠀⠀⠀⠸⣿⣧⠀⠀⠀⠀
                   ⠀⠀⠀⠀⣸⣿⡏⠀⢀⣾⣿⣿⣿⣷⡀⠀⢸⣿⣇⠀⠀⠀⠀
        ┌───────────────────────────────────────────────────
        │   THE WARDEN — HAND OF KALUKAR, SCOURGE OF SPITE   │
        └───────────────────────────────────────────────────
    """)

def victory_visual():
    divider()
    print(r"""
     \o/  VICTORY  \o/
      \   |   /
       \  |  /
        \ | /
         \|/
          |
         / \
    """)
    slow_print("The last echo of the fight fades. You stand victorious.")
    divider()

def defeat_visual():
    divider()
    print(r"""
      _____
     /     \
    |  RIP  |
    |_______|
    """)
    slow_print("Your vision fades. The camp consumes another soul.")
    divider()

# -------------------------
# Classes & Abilities
# -------------------------
classes = {
    "Vera's Shadow": {"hp":100, "attack":12, "defense":4, "abilities":["Spite Strike","Wraith Step"]},
    "Jori's Apprentice": {"hp":90, "attack":10, "defense":3, "abilities":["Scout's Eye","Swift Hands"]},
    "Divine Scholar": {"hp":80, "attack":8, "defense":2, "abilities":["Shimmering Insight","Fragmented Heart"]},
    "Labored Warrior": {"hp":120, "attack":14, "defense":5, "abilities":["Hammer Swing","Enduring Stance"]},
    "Mirror Adept": {"hp":85, "attack":9, "defense":3, "abilities":["Reflective Shard","Crystalline Bind"]}
}

ability_effects = {
    "Spite Strike":{"desc":"A vengeful strike that deals extra damage if wounded.","damage":1.5},
    "Wraith Step":{"desc":"Evade enemy attacks and counterattack.","damage":1.0,"dodge":0.25},
    "Scout's Eye":{"desc":"Increases chance of critical hit.","crit":0.25},
    "Swift Hands":{"desc":"Quick attack, slightly lower damage but guaranteed hit.","damage":0.8,"hit":1.0},
    "Shimmering Insight":{"desc":"Magical attack with chance to reduce enemy defense.","damage":1.2,"debuff":"defense"},
    "Fragmented Heart":{"desc":"Attack that has a chance to hit twice.","damage":0.7,"multi":2},
    "Hammer Swing":{"desc":"Heavy swing that may stun enemy.","damage":1.4,"stun":0.15},
    "Enduring Stance":{"desc":"Raises own defense temporarily.","buff":"defense"},
    "Reflective Shard":{"desc":"Attack that reflects some damage back.","damage":1.0,"reflect":0.15},
    "Crystalline Bind":{"desc":"Bind enemy reducing their agility.","damage":1.0,"debuff":"agility"}
}

# -------------------------
# NPCs & Camp
# -------------------------
npcs = {
    "Jori":{"recruitable":True,"recruited":False,"stat_bonus":"strength",
            "dialogue":["Hey, you look capable. Mind if I tag along?",
                       "I know hidden paths. I can help escape.",
                       "Let's train together, I can show tricks."]},
    "Alva":{"recruitable":False,
            "dialogue":["Keep your mind sharp. Observation is key.",
                       "There is more to this camp than you see.",
                       "Patience is survival."]},
    "Talenrel":{"recruitable":False,
                "dialogue":["Strength comes from repetition. Don't falter.",
                           "Focus your anger; it will guide your strikes."]},
    "Vell":{"recruitable":False,
            "dialogue":["I wasn’t really working anyway.",
                       "If you want a laugh, you’re in the right place.",
                       "I may not take things seriously, but I can lend a hand."]},
    "Ilhera":{"recruitable":False,
              "dialogue":["Knowledge is a weapon. Sharpen it daily.",
                         "Divine Hearts hold secrets beyond the physical.",
                         "Careful, even the weak can strike when underestimated."]},
    "Rhain":{"recruitable":False,
             "dialogue":["Strategy beats brute force every time.",
                        "Know your enemies, anticipate their moves.",
                        "Patience is the silent killer in battle."]},
    "Muerin":{"recruitable":False,
               "dialogue":["Mirrors reflect truth and lies alike.",
                          "Control the battlefield with your mind.",
                          "Crystals can be deadly if wielded wisely."]},
    "Dectus":{"recruitable":False,
               "dialogue":["You seek escape? Secrets lie in shadows.",
                          "Few survive by luck. Learn, adapt, survive.",
                          "Keep allies close, enemies closer."]},
}

camp_locations = {
    "Tents":["Jori"],
    "Training Grounds":["Talenrel"],
    "Work Area":["Vell"],
    "Guard Tower":["Rhain","Muerin"],
    "Mess Hall":["Alva","Ilhera"],
    "Chapel":["Dectus"]
}

# -------------------------
# Enemies
# -------------------------
enemies = [
    {"name":"Wild Scavenger","level":(1,3),"hp_base":20},
    {"name":"Feral Miner","level":(3,5),"hp_base":30},
    {"name":"Jash Raider","level":(5,7),"hp_base":45},
    {"name":"Crystal Wraith","level":(6,9),"hp_base":55},
    {"name":"Kalukar Enforcer","level":(8,10),"hp_base":70}
]

# -------------------------
# Player (global)

player = {
    "name":"",
    "class":"",
    "level":1,
    "xp":0,
    "hp":0,
    "max_hp":0,
    "attack":0,
    "defense":0,
    # stats: strength, agility, intelligence, endurance, willpower, luck
    "stats":{"strength":5,"agility":5,"intelligence":5,"endurance":5,"willpower":5,"luck":5},
    "abilities":[],
    "party":[],
    "boss_defeated":False
}

# -------------------------
# Combat math: make stats matter

def calculate_damage(attacker_stats, defender_stats, base, damage_type="physical"):
    """
    Returns (damage_int, crit_bool)
    - damage_type: 'physical' uses strength, 'special' uses willpower
    - crit chance derived from attacker's luck: each point = 0.5% crit chance
    - dodge chance derived from defender agility: each point = 0.5% dodge chance
    - endurance reduces damage (each point ~0.9)
    """
    # Crit check
    crit_chance = attacker_stats.get("luck", 0) * 0.005  # e.g., luck 10 -> 0.05 = 5%
    crit = random.random() < crit_chance

    # Dodge check (defender agility)
    dodge_chance = defender_stats.get("agility", 0) * 0.005
    dodged = random.random() < dodge_chance
    if dodged:
        return 0, False, True  # damage 0, not crit, dodged

    # Base scaling
    if damage_type == "physical":
        scaled = base + attacker_stats.get("strength", 0) * 1.2
    elif damage_type == "special":
        scaled = base + attacker_stats.get("willpower", 0) * 1.6
    else:
        scaled = base + attacker_stats.get("strength", 0)

    # Defense/endurance reduction
    reduction = defender_stats.get("endurance", 0) * 0.9
    damage = max(1, int(scaled - reduction))

    if crit:
        damage = int(damage * 1.5)

    return damage, crit, False

# -------------------------
# Classes & Character Creation

def create_character():
    clear_screen()
    slow_print("Welcome to STILLWATER — the camp where freedom is a memory.")
    name = input("Enter your character's name (default: Vera): ").strip()
    player["name"] = name or "Vera"
    slow_print(f"Welcome, {player['name']}.\n")

    # Class selection
    slow_print("Choose your class:")
    for idx, cls in enumerate(classes.keys(), 1):
        abilities = ", ".join(classes[cls]["abilities"])
        print(f"{idx}. {cls} — Abilities: {abilities}")
    while True:
        choice = input("Enter class number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(classes):
            idx = int(choice)-1
            cls_name = list(classes.keys())[idx]
            player["class"] = cls_name
            break
        print("Invalid choice.")
    # assign stats from class
    c = classes[player["class"]]
    player["max_hp"] = c["hp"]
    player["hp"] = player["max_hp"]
    player["attack"] = c["attack"]
    player["defense"] = c["defense"]
    player["abilities"] = c["abilities"].copy()
    # give small per-class stat flavor (optional)
    if "Warrior" in player["class"] or "Labored" in player["class"]:
        player["stats"]["strength"] += 2
        player["stats"]["endurance"] += 1
    elif "Divine" in player["class"] or "Mirror" in player["class"]:
        player["stats"]["intelligence"] += 2
        player["stats"]["willpower"] += 1
    elif "Jori" in player["class"]:
        player["stats"]["agility"] += 2
        player["stats"]["luck"] += 1

    slow_print(f"\n{player['name']} — {player['class']} joined the ranks.")
    player_art()
    short_pause(0.8)

# -------------------------
# XP & Leveling

def gain_xp(amount):
    player["xp"] += amount
    slow_print(f"You gain {amount} XP!")
    while player["xp"] >= player["level"] * 20:
        player["xp"] -= player["level"] * 20
        player["level"] += 1
        player["max_hp"] += 10
        player["attack"] += 2
        player["defense"] += 1
        # small random stat increases on level
        stat_to_boost = random.choice(list(player["stats"].keys()))
        player["stats"][stat_to_boost] += 1
        player["hp"] = player["max_hp"]
        slow_print(f"LEVEL UP! You are now level {player['level']}! (+1 {stat_to_boost})")
        level_up_visual(player["level"])

def level_up_visual(new_level):
    divider()
    print(rf"""
     ↑ LEVEL {new_level} ↑
      *   *   *   *   *
     *  YOU FEEL STRONGER  *
      *   *   *   *   *
    """)
    time.sleep(1)
    divider()

# -------------------------
# Exploration & Events

def explore_camp():
    divider()
    slow_print("You wander through the camp grounds...")
    show_camp_map()
    print("\nWhere do you want to go?")
    keys = list(camp_locations.keys())
    for i, k in enumerate(keys, 1):
        print(f"{i}. {k}")
    print(f"{len(keys)+1}. Return to Main Camp")
    choice = input("Choose location: ").strip()
    if not choice.isdigit():
        slow_print("You linger oddly and a guard barks. You step back.")
        return
    choice = int(choice)
    if 1 <= choice <= len(keys):
        loc = keys[choice-1]
        slow_print(f"\nYou head to the {loc}...")
        for npc in camp_locations[loc]:
            if npc in npcs:
                dialogue = random.choice(npcs[npc]["dialogue"])
                slow_print(f"{npc}: \"{dialogue}\"", 0.02)
                # recruitment chance for recruitable NPCs (only Jori here)
                if npcs[npc].get("recruitable", False) and not npcs[npc]["recruited"]:
                    recruit = input(f"Do you attempt to recruit {npc}? (y/n): ").strip().lower()
                    if recruit == "y":
                        if random.random() < 0.9:  # high chance
                            npcs[npc]["recruited"] = True
                            player["party"].append(npc)
                            slow_print(f"{npc} has joined your party!")
                        else:
                            slow_print(f"{npc} refuses and walks away.")
        # small random events
        if loc == "Work Area" and random.random() < 0.25:
            slow_print("A cart collapses — you help salvage tools and find a crude shard (+1 XP).")
            gain_xp(1)
        if loc == "Chapel" and random.random() < 0.15:
            slow_print("A hush, a scrap of hymn. Your will steadies (+1 willpower).")
            player["stats"]["willpower"] += 1
    else:
        slow_print("You return to your fire, plotting escape.")

# -------------------------
# Training & Simple Activities

def training_session():
    divider()
    slow_print("You spend an hour training in the yard.")
    rolls = {
        "strength": (1,3),
        "agility": (1,3),
        "intelligence": (0,2),
        "endurance": (1,3),
        "willpower": (0,2),
        "luck": (0,1)
    }
    stat = random.choice(list(rolls.keys()))
    gain = random.randint(*rolls[stat])
    if gain > 0:
        player["stats"][stat] += gain
        slow_print(f"Your {stat} increases by {gain}!")
    else:
        slow_print("The training was dull and taught little.")
    xp_gain = random.randint(2,6)
    gain_xp(xp_gain)
    slow_print(f"(+{xp_gain} XP)")

# -------------------------
# Enemy stat generator

def generate_enemy(enemy_template, level):
    # Return dictionary with hp and stats for combat math
    base_hp = enemy_template.get("hp_base", 20) + level * 5
    stats = {
        "strength": max(1, int(level * 1.5)),
        "agility": max(1, int(level * 0.9)),
        "endurance": max(1, int(level * 1.0)),
        "willpower": max(0, int(level * 0.4)),
        "luck": max(0, int(level * 0.3))
    }
    return {"name": enemy_template["name"], "level": level, "hp": base_hp, "max_hp": base_hp, "stats": stats}

# -------------------------
# Battle Systems
def battle_scaled():
    """Scaled encounter selected from enemies depending on player level."""
    lvl = player["level"]
    if lvl < 3:
        pool = [e for e in enemies if e["level"][1] <= 3]
    elif lvl < 7:
        pool = [e for e in enemies if e["level"][1] <= 7]
    else:
        pool = enemies
    enemy_template = random.choice(pool)
    enemy_level = max(enemy_template["level"][0], min(enemy_template["level"][1], random.randint(enemy_template["level"][0], enemy_template["level"][1])))
    enemy = generate_enemy(enemy_template, enemy_level)
    return enhanced_battle(enemy=enemy)

def enhanced_battle(enemy=None, enemy_level=None, base_hp=None):
    """
    Enhanced battle: visual, abilities, party support.
    If enemy dict provided, uses it. Otherwise creates generic enemy.
    Returns True if player wins, False if player dies or escapes.
    """
    # Create enemy if not provided
    if enemy is None:
        # generic enemy generation
        template = random.choice(enemies)
        lvl = enemy_level or player["level"]
        enemy = generate_enemy(template, lvl)

    enemy_name = enemy["name"]
    enemy_hp = enemy["hp"]
    player_hp = player["hp"]

    battle_intro(enemy_name)
    short_pause(0.2)

    turn = 1
    defend = False
    while enemy_hp > 0 and player_hp > 0:
        divider()
        print(f"Turn {turn} — {player['name']} (HP: {player_hp}/{player['max_hp']}) vs {enemy_name} (HP: {enemy_hp}/{enemy['max_hp']})")
        print(hp_bar(player_hp, player["max_hp"]), "  ", hp_bar(enemy_hp, enemy["max_hp"]))
        short_pause(0.2)

        # Player action
        print("\nActions:")
        print("1. Basic Attack")
        print("2. Use Ability")
        print("3. Defend")
        print("4. Attempt Flee")
        action = prompt_choice("> ", ["1","2","3","4"])

        if action == "1":
            # Basic physical attack base scales with player attack stat
            base = max(4, player["attack"])
            damage, crit, dodged = calculate_damage(player["stats"], enemy["stats"], base, damage_type="physical")
            if dodged:
                slow_print("The enemy nimbly dodged your blow!")
            else:
                player_message = f"You strike for {damage} damage"
                if crit: player_message += " (CRIT!)"
                player_message += "."
                slow_print(player_message)
                enemy_hp -= damage
        elif action == "2":
            if not player["abilities"]:
                slow_print("You have no abilities. You fumble.")
            else:
                print("Abilities:")
                for i, a in enumerate(player["abilities"],1):
                    print(f"{i}. {a} — {ability_effects.get(a, {}).get('desc','')}")
                sel = input("Choose ability number: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(player["abilities"]):
                    a = player["abilities"][int(sel)-1]
                    # base for abilities uses willpower scaling
                    ability_base = max(3, player["attack"]//2 + player["stats"].get("willpower", 0))
                    mult = ability_effects.get(a, {}).get("damage", 1.0)
                    damage, crit, dodged = calculate_damage(player["stats"], enemy["stats"], int(ability_base * mult), damage_type="special")
                    if dodged:
                        slow_print("The enemy dodged your ability!")
                    else:
                        if ability_effects.get(a, {}).get("multi") and random.random() < 0.35:
                            extra = int(damage * 0.4)
                            slow_print("It fragments into multiple strikes!")
                            damage += extra
                        slow_print(f"You use {a}, dealing {damage} damage!" + (" (CRIT!)" if crit else ""))
                        enemy_hp -= damage
                        # small special: stun chance
                        if ability_effects.get(a, {}).get("stun") and random.random() < ability_effects[a]["stun"]:
                            slow_print("You stagger the enemy! They may miss a turn.")
                            enemy["stunned"] = True
                else:
                    slow_print("You hesitate and lose your chance.")
        elif action == "3":
            slow_print("You brace for impact, reducing incoming damage this turn.")
            defend = True
        elif action == "4":
            if random.random() < 0.45:
                slow_print("You slip away successfully.")
                player["hp"] = player_hp
                return False  # escaped
            else:
                slow_print("You fail to escape!")

        # Party support
        if player["party"]:
            for member in player["party"]:
                pd_base = 2 + random.randint(0,4)
                # party member damage can be scaled slightly by player's level
                pd = pd_base + int(player["level"]/2)
                slow_print(f"{member} assists for {pd} damage!")
                enemy_hp -= pd

        if enemy_hp <= 0:
            victory_visual()
            gain_xp(enemy["level"] * 6)
            player["hp"] = min(player["max_hp"], player_hp)
            return True

        # Enemy turn
        slow_print(f"\n{enemy_name} prepares to strike!")
        # handle enemy stunned flag
        if enemy.get("stunned", False):
            slow_print(f"{enemy_name} is stunned and cannot act!")
            enemy["stunned"] = False
        else:
            # enemy uses physical attack base scaled by their strength
            base_enemy = max(3, enemy["stats"].get("strength", 1) + enemy["level"])
            damage, crit, dodged = calculate_damage(enemy["stats"], player["stats"], base_enemy, damage_type="physical")
            if dodged:
                slow_print("You nimbly dodge the enemy's attack!")
            else:
                # if player defended, reduce damage by half roughly
                if defend:
                    damage = max(1, int(damage * 0.5))
                    defend = False
                slow_print(f"You take {damage} damage!" + (" (CRIT!)" if crit else ""))
                player_hp -= damage

            # enemy may have small special chance to apply pressure (flavor)
            if random.random() < 0.05 and enemy["level"] > 3:
                slow_print(f"{enemy_name} pushes you, you feel drained (-1 endurance).")
                player["stats"]["endurance"] = max(0, player["stats"]["endurance"] - 1)

        if player_hp <= 0:
            defeat_visual()
            player["hp"] = 0
            return False

        turn += 1
        short_pause(0.25)

    player["hp"] = player_hp
    return player["hp"] > 0

def battle_intro(enemy_name):
    divider()
    print(rf"""
      ⚔️  BATTLE COMMENCES ⚔️
    Enemy: {enemy_name}
    """)
    time.sleep(0.25)

# -------------------------
# Boss Fight — The Warden
def boss_fight():
    clear_screen()
    slow_print("You approach the final gate... thunder breaks like bone.")
    warden_visual()
    slow_print('\nA booming voice: "Vera... you were never meant to be free."', 0.03)
    input("\nPress Enter to defy him...")

    # Boss stats scale with player level
    base_warden_hp = 220 + player["level"] * 2
    warden = {
        "name": "The Warden",
        "level": max(3, player["level"] + 1),
        "hp": base_warden_hp,
        "max_hp": base_warden_hp,
        # boss stats: big strength/endurance, moderate agility, moderate willpower
        "stats": {"strength": 12 + player["level"]*1, "agility": 6 + player["level"], "endurance": 10 + player["level"], "willpower": 5 + player["level"]//2, "luck": 2}
    }

    warden_phase = 1
    player_hp = player["hp"]
    defend = False
    stunned = False

    slow_print("\nThe Warden charges, his glaive humming with crystal light.", 0.03)

    while warden["hp"] > 0 and player_hp > 0:
        divider()
        print(f"You (HP: {player_hp}/{player['max_hp']})  |  {warden['name']} (HP: {warden['hp']}/{warden['max_hp']})  Phase: {warden_phase}")
        print("1. Attack  2. Use Ability  3. Defend  4. Rally (party buff)")
        choice = prompt_choice("> ", ["1","2","3","4"])

        if choice == "1":
            base = max(8, player["attack"] + player["stats"].get("strength",0)//2)
            dmg, crit, dodged = calculate_damage(player["stats"], warden["stats"], base, damage_type="physical")
            if dodged:
                slow_print("The Warden evades your strike!")
            else:
                if warden_phase >= 2:
                    # some armor effect at later phases
                    dmg = max(1, int(dmg - (player["level"]/2)))
                slow_print(f"You strike the Warden for {dmg} damage." + (" (CRIT!)" if crit else ""))
                warden["hp"] -= dmg
        elif choice == "2":
            if not player["abilities"]:
                slow_print("You have no abilities.")
            else:
                print("Abilities:")
                for i, a in enumerate(player["abilities"],1):
                    print(f"{i}. {a} — {ability_effects.get(a, {}).get('desc','')}")
                sel = input("Choose ability number: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(player["abilities"]):
                    a = player["abilities"][int(sel)-1]
                    ability_base = max(6, player["attack"]//2 + player["stats"].get("willpower",0))
                    mult = ability_effects.get(a, {}).get("damage", 1.0)
                    dmg, crit, dodged = calculate_damage(player["stats"], warden["stats"], int(ability_base * mult), damage_type="special")
                    if dodged:
                        slow_print("The Warden shifts aside and avoids the strike!")
                    else:
                        if ability_effects.get(a, {}).get("multi") and random.random() < 0.35:
                            slow_print("The strike fractures across his armor—multiple hits!")
                            dmg += int(dmg * 0.35)
                        slow_print(f"{a} deals {dmg} damage!" + (" (CRIT!)" if crit else ""))
                        warden["hp"] -= dmg
                        # stun check
                        if ability_effects.get(a, {}).get("stun") and random.random() < ability_effects[a]["stun"]:
                            slow_print("The Warden staggers! He'll likely miss his next strike.")
                            stunned = True
                else:
                    slow_print("You fumble the attempt.")
        elif choice == "3":
            slow_print("You take a defensive stance.")
            defend = True
        elif choice == "4":
            if player["party"]:
                slow_print("You rally your allies. Their resolve bolsters you.")
                for m in player["party"]:
                    buff_amount = max(1, int(1 + player["level"]/3))
                    player["attack"] += buff_amount
                short_pause(0.4)
            else:
                slow_print("You have no allies to rally.")

        # Phase transitions
        max_hp = warden["max_hp"]
        if warden["hp"] <= max_hp * 0.6 and warden_phase == 1:
            slow_print("\nThe Warden's crystal plates glow — he moves more fiercely.")
            warden_phase = 2
            # armor augmentation in phase 2
            warden["stats"]["endurance"] += 4 + player["level"]
        if warden["hp"] <= max_hp * 0.25 and warden_phase == 2:
            slow_print("\nThe Warden howls — the final surge begins.")
            warden_phase = 3

        # Warden's turn
        if stunned:
            slow_print("The Warden is stunned and flails helplessly!")
            stunned = False
        else:
            # heavy attack
            base_e = 14 + player["level"]
            e_dmg, e_crit, e_dodged = calculate_damage(warden["stats"], player["stats"], base_e, damage_type="physical")
            if e_dodged:
                slow_print("You dodge the Warden's strike!")
            else:
                if defend:
                    e_dmg = max(1, int(e_dmg * 0.5))
                    defend = False
                slow_print(f"The Warden hits you for {e_dmg} damage!" + (" (CRIT!)" if e_crit else ""))
                player_hp -= e_dmg

        # Phase 3 area attack
        if warden_phase == 3 and random.random() < 0.35:
            aoe_base = 12 + player["level"]*2
            aoe_dmg, aoe_crit, aoe_dodged = calculate_damage(warden["stats"], player["stats"], aoe_base, damage_type="special")
            if not aoe_dodged:
                slow_print(f"A crystal storm batters you for {aoe_dmg} damage!")
                player_hp -= aoe_dmg

        if player_hp <= 0:
            defeat_visual()
            player["hp"] = 0
            slow_print("The Warden's final blow closes your story.")
            return False

        short_pause(0.3)

    # victory
    slow_print("\nThe Warden collapses. The storm eases. You have broken the chain.")
    victory_visual()
    player["boss_defeated"] = True
    player["hp"] = max(1, player_hp)
    gain_xp(100 + player["level"]*10)
    return True

"""
StillWater RPG
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

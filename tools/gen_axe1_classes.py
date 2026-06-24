#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur AXE 1 — émet les fichiers Config du mod (source de vérité unique).

Modèle (J1.12) :
  - 7 BRANCHES = 7 attributs visibles = 7 onglets (Survivant en plus).
  - Chaque sous-classe = plusieurs SOUS-BRANCHES (skills) ; chaque sous-branche ~6-7 perks
    -> ~20 perks par sous-classe (profondeur, fin de classe ~niv 50). Drill-down UI natif :
       attribut(onglet) -> skills(sous-branches) -> perks.
  - Perks : "stat" (5 niv, scalés) ou "unlock" (max 1 ; débloque une recette signature via
    RecipeTagUnlocked = NOM de recette, méthode vanilla). Un unlock "auto" (coût 0) est octroyé
    par le livre/magazine (= identité de classe) ; les autres sont achetables (coût 1, palier).
  - Progression par MAGAZINE = +1 POINT DE CLASSE (cvar dhsPts<code>), dépensable librement
    dans les perks de la classe (palier de niveau respecté par les level_requirements).
    L'octroi est pur XML (ModifyCVar) ; la DÉPENSE est gérée par un patch Harmony C#.
  - Seul Fermier (FarmAgri + FarmCook) est rempli en profondeur ; les 12 autres sous-classes
    utilisent un template (1 sous-branche) pour charger, en attendant réplication.

Génère : progression.xml, items.xml, recipes.xml, buffs.xml, loot.xml, Localization.csv
(NB: V3.0 charge Config/Localization.CSV, pas .txt). Loc catégories en MINUSCULES.
"""
import os, re, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "Mods", "DeadHotSummer", "Config")

LVL = [1, 12, 24, 36, 48]  # paliers PlayerLevel par rang
PALIERS = [1, 12, 24, 36, 48]  # paliers de niveau pour les déblocages de craft

# ---- Données vanilla (noms FR des items + recettes débloquées par niveau/livres) ----
def _find_file(cands):
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None
VAN_LOC = _find_file(["/home/louis-quentin/7dtd/Data/Config/Localization.txt",
                      os.path.join(ROOT, "Data", "Config", "Localization.txt")])
VAN_PROG = _find_file([os.path.join(ROOT, "Data", "Config", "progression.xml"),
                       "/home/louis-quentin/7dtd/Data/Config/progression.xml"])

def _load_vanilla_fr():
    d = {}
    if not VAN_LOC:
        return d
    with open(VAN_LOC, encoding="utf-8") as f:
        r = csv.reader(f); h = next(r); fi = h.index("french")
        for row in r:
            if row and len(row) > fi and row[0]:
                d.setdefault(row[0], row[fi])
    return d
VANILLA_FR = _load_vanilla_fr()

def _load_craft_unlocks():
    """{nom_crafting_skill: [(recette, niveau_skill), ...]} d'après progression.xml vanilla.
    Ce sont exactement les crafts qui se débloquaient par niveau/magazines dans l'Artisanat."""
    out = {}
    if not VAN_PROG:
        return out
    xml = open(VAN_PROG, encoding="utf-8").read()
    for m in re.finditer(r'<crafting_skill name="([^"]+)".*?</crafting_skill>', xml, re.S):
        nm, blk, lst = m.group(1), m.group(0), []
        for lv, tags in re.findall(
                r'RecipeTagUnlocked"\s+operation="base_set"\s+level="(\d+)[^"]*"\s+value="1"\s+tags="([^"]+)"', blk):
            for t in tags.split(","):
                lst.append((t, int(lv)))
        out[nm] = lst
    return out
CRAFT_UNLOCKS = _load_craft_unlocks()

def palier_from_craftlevel(cl):
    """Niveau de compétence d'artisanat vanilla (1-100) -> palier de niveau joueur cohérent."""
    if cl <= 9:  return 1
    if cl <= 25: return 12
    if cl <= 45: return 24
    if cl <= 70: return 36
    return 48

# Template de perks par "kind" (sous-branche ARME des 12 sous-classes "domaine").
# Chaque kind est AUTONOME : ensemble d'effets TOUS DISTINCTS (aucun doublon intra-classe).
# Tout est scopé au tag d'arme de la sous-classe (sauf indication). (suffixe, EN, FR, effet,
# op, v1, v5, scoped_au_tag, EN desc, FR desc).  Maniement = WeaponHandling (prise en main).
PERKS = {
    "gun": [
        ("Dmg","Dégâts","Dégâts","EntityDamage","perc_add",".08",".40",True,"Augmente les dégâts de l'arme de classe.","Augmente les dégâts de l'arme de classe."),
        ("Hand","Maniement","Maniement","WeaponHandling","perc_add",".10",".50",True,"Améliore la prise en main : visée plus rapide, recul et oscillation réduits.","Améliore la prise en main : visée plus rapide, recul et oscillation réduits."),
        ("Reload","Rechargement rapide","Rechargement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Recharge plus vite.","Recharge plus vite."),
        ("Aim","Précision","Précision","SpreadMultiplierAiming","perc_add","-.06","-.30",True,"Réduit la dispersion des tirs en visée.","Réduit la dispersion des tirs en visée."),
        ("Pierce","Perforation","Perforation","TargetArmor","perc_add","-.06","-.30",True,"Vos tirs ignorent davantage l'armure.","Vos tirs ignorent davantage l'armure."),
        ("WStam","Aisance","Aisance","StaminaLoss","perc_add","-.05","-.25",True,"Réduit l'endurance dépensée en maniant cette arme.","Réduit l'endurance dépensée en maniant cette arme."),
    ],
    "bow": [
        ("Dmg","Dégâts","Dégâts","EntityDamage","perc_add",".08",".40",True,"Augmente les dégâts arc/arbalète.","Augmente les dégâts arc/arbalète."),
        ("Hand","Maniement","Maniement","WeaponHandling","perc_add",".10",".50",True,"Améliore la prise en main : visée plus stable, bandage plus régulier.","Améliore la prise en main : visée plus stable, bandage plus régulier."),
        ("Draw","Armement rapide","Armement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Encoche et arme plus vite.","Encoche et arme plus vite."),
        ("Velo","Tir puissant","Tir puissant","ProjectileVelocity","perc_add",".10",".50",True,"Augmente la vitesse des projectiles (portée, précision).","Augmente la vitesse des projectiles (portée, précision)."),
        ("Pierce","Perforation","Perforation","TargetArmor","perc_add","-.06","-.30",True,"Vos projectiles ignorent davantage l'armure.","Vos projectiles ignorent davantage l'armure."),
        ("WStam","Aisance","Aisance","StaminaLoss","perc_add","-.05","-.25",True,"Réduit l'endurance dépensée en bandant l'arc.","Réduit l'endurance dépensée en bandant l'arc."),
    ],
    "melee": [
        ("Dmg","Dégâts","Dégâts","EntityDamage","perc_add",".08",".40",True,"Augmente les dégâts de mêlée.","Augmente les dégâts de mêlée."),
        ("Hand","Maniement","Maniement","WeaponHandling","perc_add",".10",".50",True,"Améliore la prise en main : attaques plus vives.","Améliore la prise en main : attaques plus vives."),
        ("Dismember","Brutalité","Brutalité","DismemberChance","base_add",".05",".25",True,"Augmente les chances de démembrement.","Augmente les chances de démembrement."),
        ("Block","Force de frappe","Force de frappe","BlockDamage","perc_add",".10",".50",True,"Augmente les dégâts portés aux blocs et objets.","Augmente les dégâts portés aux blocs et objets."),
        ("Pierce","Perforation","Perforation","TargetArmor","perc_add","-.06","-.30",True,"Vos coups ignorent davantage l'armure.","Vos coups ignorent davantage l'armure."),
        ("WStam","Aisance","Aisance","StaminaLoss","perc_add","-.05","-.25",True,"Réduit l'endurance dépensée en attaquant.","Réduit l'endurance dépensée en attaquant."),
    ],
    "thrown": [
        ("Dmg","Dégâts","Dégâts","EntityDamage","perc_add",".08",".40",True,"Augmente les dégâts de jet.","Augmente les dégâts de jet."),
        ("Hand","Maniement","Maniement","WeaponHandling","perc_add",".10",".50",True,"Améliore la prise en main : armement et lancer plus vifs.","Améliore la prise en main : armement et lancer plus vifs."),
        ("Velo","Bon bras","Bon bras","ProjectileVelocity","perc_add",".10",".50",True,"Lance plus loin et plus vite.","Lance plus loin et plus vite."),
        ("Pierce","Perforation","Perforation","TargetArmor","perc_add","-.06","-.30",True,"Vos projectiles ignorent davantage l'armure.","Vos projectiles ignorent davantage l'armure."),
        ("WStam","Aisance","Aisance","StaminaLoss","perc_add","-.05","-.25",True,"Réduit l'endurance dépensée en lançant.","Réduit l'endurance dépensée en lançant."),
    ],
    "robotics": [
        ("Dmg","Dégâts","Dégâts","EntityDamage","perc_add",".08",".40",True,"Augmente les dégâts robotiques (tourelles, drones).","Augmente les dégâts robotiques (tourelles, drones)."),
        ("Hand","Maniement","Maniement","WeaponHandling","perc_add",".10",".50",True,"Améliore la prise en main et la stabilité des armes robotiques.","Améliore la prise en main et la stabilité des armes robotiques."),
        ("Reload","Maintenance","Maintenance","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Recharge et entretient plus vite.","Recharge et entretient plus vite."),
        ("Pierce","Perforation","Perforation","TargetArmor","perc_add","-.06","-.30",True,"Vos tirs robotiques ignorent davantage l'armure.","Vos tirs robotiques ignorent davantage l'armure."),
    ],
    "tools": [
        ("Harvest","Récolte","Récolte","HarvestCount","perc_add",".10",".50",True,"Récolte davantage avec les outils.","Récolte davantage avec les outils."),
        ("Block","Outils puissants","Outils puissants","BlockDamage","perc_add",".10",".50",True,"Augmente les dégâts portés aux blocs.","Augmente les dégâts portés aux blocs."),
        ("Dmg","Mordant","Mordant","EntityDamage","perc_add",".08",".40",True,"Augmente les dégâts des outils contre les ennemis.","Augmente les dégâts des outils contre les ennemis."),
        ("Hand","Maniement","Maniement","WeaponHandling","perc_add",".10",".50",True,"Améliore la prise en main des outils.","Améliore la prise en main des outils."),
        ("WStam","Aisance","Aisance","StaminaLoss","perc_add","-.05","-.25",True,"Réduit l'endurance dépensée avec les outils.","Réduit l'endurance dépensée avec les outils."),
    ],
}

# Branches : (cléBranche, EN, FR, icône, [ sous-classes ])
# sous-classe : (code, EN, FR, tag d'arme, kind, foreignId, icône, EN flavor, FR flavor)
BRANCHES = [
    ("Engineer","Engineer","Ingénieur","ui_game_symbol_wrench", [
        ("EngiMech","Mechanic","Mécanicien","perkTurrets","robotics",11,"ui_game_symbol_wrench",
         "vehicles, junk turrets and drones","les véhicules, tourelles et drones de récup'"),
        ("EngiElec","Electrician","Électricien","perkElectrocutioner","melee",12,"ui_game_symbol_electric_generator",
         "electricity, traps and the stun baton","l'électricité, les pièges et la matraque"),
    ]),
    ("Medic","Medic","Médecin","ui_game_symbol_medical", [
        ("MedicSurg","Surgeon","Chirurgien","perkDeepCuts","melee",21,"ui_game_symbol_medical",
         "healing and bladed weapons","les soins et les armes blanches"),
        ("MedicChem","Chemist","Chimiste","perkDemolitionsExpert","thrown",22,"ui_game_symbol_science",
         "chemistry, drugs and thrown weapons","la chimie, les drogues et les armes de jet"),
    ]),
    ("Soldier","Soldier","Soldat","ui_game_symbol_armor_iron", [
        ("SoldSnip","Marksman","Tireur d'élite","perkDeadEye","gun",31,"ui_game_symbol_long_shot",
         "marksman rifles","les fusils de précision"),
        ("SoldAslt","Assault","Assaut","perkMachineGunner","gun",32,"ui_game_symbol_rifle",
         "machine guns and sustained fire","les mitrailleuses et le tir nourri"),
    ]),
    ("Survivalist","Survivalist","Survivaliste","ui_game_symbol_animal_tracker", [
        ("SurvHunt","Hunter","Chasseur","perkArchery","bow",41,"ui_game_symbol_archery",
         "bows, crossbows and hunting","les arcs, arbalètes et la chasse"),
        ("SurvHerb","Herbalist","Herboriste","perkJavelinMaster","melee",42,"ui_game_symbol_crops",
         "foraging, remedies and spears","la cueillette, les remèdes et les lances"),
    ]),
    ("Builder","Builder","Bâtisseur","ui_game_symbol_hammer", [
        ("BuilArch","Architect","Architecte","perkSkullCrusher","melee",51,"ui_game_symbol_hammer",
         "fortifications and sledgehammers","les fortifications et les masses"),
        ("BuilArti","Artisan","Artisan","perkMiner","tools",52,"ui_game_symbol_workbench",
         "workstations, tools and crafting","les ateliers, outils et l'artisanat"),
    ]),
    ("Scout","Scout","Éclaireur","ui_game_symbol_stealth", [
        ("ScoutTrac","Tracker","Pisteur","perkGunslinger","gun",61,"ui_game_symbol_run",
         "mobility, exploration and handguns","la mobilité, l'exploration et les pistolets"),
        ("ScoutInfi","Infiltrator","Infiltrateur","perkBrawler","melee",62,"ui_game_symbol_stealth2",
         "stealth, looting and fist weapons","la furtivité, le pillage et les armes de poing"),
    ]),
    ("Farmer","Farmer","Fermier","ui_game_symbol_crops", [
        ("FarmAgri","Farmer","Agriculteur","perkBoomstick","gun",71,"ui_game_symbol_crops",
         "crops and the pump shotgun","les cultures et le fusil à pompe"),
        ("FarmCook","Cook","Cuisinier","perkPummelPete","melee",72,"ui_game_symbol_fork",
         "cooking, team buffs and clubs","la cuisine, les buffs d'équipe et les gourdins"),
    ]),
]

SUBS = [s for _bk,_en,_fr,_ic,subs in BRANCHES for s in subs]
CODE2BRANCH = {s[0]: bk for bk,_en,_fr,_ic,subs in BRANCHES for s in subs}
SUB_BY_CODE = {s[0]: s for s in SUBS}

def cvar(code): return "dhsCls" + code
def ptsvar(code): return "dhsPts" + code
def attr_of_branch(bk): return "attClass" + bk

# ============================================================================
# Modèle de perks détaillé (sous-branches). Helpers :
#   stat  : perk scalé (5 niv par défaut). tags="" = non scopé.
#   unlock: perk max 1 débloquant une/des recette(s) signature (par NOM).
# ============================================================================
def stat(suf, en, fr, eff, op, v1, vmax, nlev, tags, ed, fd, icon="ui_game_symbol_character"):
    return {"k":"stat","suf":suf,"en":en,"fr":fr,"eff":eff,"op":op,"v1":v1,"vmax":vmax,
            "n":nlev,"tags":tags,"ed":ed,"fd":fd,"icon":icon}
def unlock(suf, en, fr, icon, recipes, auto, palier, ed, fd):
    return {"k":"unlock","suf":suf,"en":en,"fr":fr,"icon":icon,"recipes":recipes,
            "auto":auto,"palier":palier,"ed":ed,"fd":fd}
def sp(suf, fr, fd, eff, op, v1, vmax, n, tags="", icon="ui_game_symbol_character"):
    """Raccourci pour un perk de Spécialité (FR dans en+fr, desc=fd)."""
    return stat(suf, fr, fr, eff, op, v1, vmax, n, tags, fd, fd, icon)

# ---- FERMIER : Agriculteur (cultures + fusil à pompe) ----
FARM_AGRI = [
    ("Shotgun","Pump Shotgun","Fusil à pompe","ui_game_symbol_shotgun", [
        stat("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",5,"perkBoomstick",
             "Increases pump shotgun damage.","Augmente les dégâts au fusil à pompe.","ui_game_symbol_shotgun"),
        stat("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",5,"perkBoomstick",
             "Améliore la prise en main du fusil : visée plus rapide, recul et oscillation réduits.","Améliore la prise en main du fusil : visée plus rapide, recul et oscillation réduits.","ui_game_symbol_shotgun"),
        stat("Reload","Fast Reload","Rechargement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",5,"perkBoomstick",
             "Reloads the shotgun faster.","Recharge le fusil plus vite.","ui_game_symbol_shotgun"),
        stat("Aim","Choke","Précision","SpreadMultiplierAiming","perc_add","-.06","-.30",5,"perkBoomstick",
             "Tightens aimed shot spread.","Resserre la gerbe en visée.","ui_game_symbol_shotgun"),
        stat("Pierce","Slugger","Perforation","TargetArmor","perc_add","-.06","-.30",5,"perkBoomstick",
             "Les tirs au fusil ignorent davantage l'armure.","Les tirs au fusil ignorent davantage l'armure.","ui_game_symbol_shotgun"),
    ]),
    ("Farming","Farming","Agriculture","ui_game_symbol_crops", [
        stat("Green","Green Thumb","Main verte","HarvestCount","perc_add",".15",".75",5,"cropHarvest",
             "Récolte bien plus sur vos cultures.","Récolte bien plus sur vos cultures.","ui_game_symbol_crops"),
        stat("Butcher","Homesteader","Éleveur","HarvestCount","perc_add",".10",".50",5,"butcherHarvest",
             "Récolte plus de viande et de ressources sur les animaux.","Récolte plus de viande et de ressources sur les animaux.","ui_game_symbol_deep_cuts"),
        stat("FastCraft","Cadence agricole","Cadence agricole","CraftingTime","perc_add","-.10","-.50",5,"dhsCraftFarmAgri",
             "Fabrique vos recettes d'Agriculteur plus vite.","Fabrique vos recettes d'Agriculteur plus vite.","ui_game_symbol_workbench"),
        stat("Cart","Charrette","Charrette","CarryCapacity","base_add","2","10",5,"",
             "Ajoute des emplacements pour transporter vos récoltes.","Ajoute des emplacements pour transporter vos récoltes.","ui_game_symbol_pack_mule"),
        stat("StamRegen","Field Stamina","Souffle paysan","StaminaChangeOT","perc_add",".05",".25",5,"",
             "Récupère l'endurance plus vite.","Récupère l'endurance plus vite.","ui_game_symbol_cardio"),
    ]),
    ("Provider","Provider","Terroir","ui_game_symbol_crops", [
        sp("Wild","Fourrageur","Récolte plus sur les plantes sauvages.","HarvestCount","perc_add",".10",".50",5,"wildCropsHarvest","ui_game_symbol_crops"),
        sp("Sun","Travailleur des champs","Améliore la résistance à la chaleur.","HyperthermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
        sp("Trade","Maquignon","Améliore les prix de vente chez les marchands.","BarteringSelling","base_add","2","10",5,"","ui_game_symbol_barter"),
        sp("Forage","Glaneur des champs","Améliore la qualité du butin de fouille.","LootStage","perc_add",".04",".20",5,"","ui_game_symbol_map"),
        sp("Quiet","Vie au grand air","Réduit le bruit que vous faites.","NoiseMultiplier","perc_add","-.04","-.20",5,"","ui_game_symbol_stealth"),
        sp("Sturdy","Robuste paysan","Réduit les dégâts physiques subis.","PhysicalDamageResist","base_add","1","5",5,"","ui_game_symbol_armor_iron"),
    ]),
]

# ---- FERMIER : Cuisinier (cuisine + gourdins + soutien d'équipe) ----
FARM_COOK = [
    ("Club","Club","Gourdin","ui_game_symbol_hammer", [
        stat("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",5,"perkPummelPete",
             "Increases club damage.","Augmente les dégâts au gourdin.","ui_game_symbol_hammer"),
        stat("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",5,"perkPummelPete",
             "Améliore la prise en main du gourdin : attaques plus vives.","Améliore la prise en main du gourdin : attaques plus vives.","ui_game_symbol_hammer"),
        stat("Dismember","Tenderizer","Attendrisseur","DismemberChance","base_add",".05",".25",5,"perkPummelPete",
             "Increases dismemberment with clubs.","Augmente le démembrement au gourdin.","ui_game_symbol_hammer"),
        stat("Stam","Conditioning","Conditionnement","StaminaLoss","perc_add","-.06","-.30",5,"perkPummelPete",
             "Reduces stamina spent attacking.","Réduit l'endurance dépensée en attaquant.","ui_game_symbol_cardio"),
        stat("Block","Meat Mallet","Massue","BlockDamage","perc_add",".10",".50",5,"perkPummelPete",
             "Increases block damage with clubs.","Augmente les dégâts aux blocs au gourdin.","ui_game_symbol_hammer"),
        stat("Armor","Bonecrusher","Broyeur d'armure","TargetArmor","perc_add","-.06","-.30",5,"perkPummelPete",
             "Club hits ignore more armor.","Les coups ignorent davantage l'armure.","ui_game_symbol_hammer"),
    ]),
    ("Kitchen","Kitchen","Cuisine","ui_game_symbol_fork", [
        stat("FastCook","Sous-Chef","Marmiton","CraftingTime","perc_add","-.10","-.50",5,"dhsCraftFarmCook",
             "Cuisine vos recettes de Cuisinier plus vite.","Cuisine vos recettes de Cuisinier plus vite.","ui_game_symbol_fork"),
        stat("Butcher","Butcher","Boucher","HarvestCount","perc_add",".10",".50",5,"butcherHarvest",
             "Récolte plus de viande sur les animaux.","Récolte plus de viande sur les animaux.","ui_game_symbol_deep_cuts"),
        stat("Pantry","Garde-manger","Garde-manger","CarryCapacity","base_add","2","10",5,"",
             "Ajoute des emplacements pour transporter vos provisions.","Ajoute des emplacements pour transporter vos provisions.","ui_game_symbol_pack_mule"),
    ]),
    ("Support","Support","Maison & équipe","ui_game_symbol_medical", [
        sp("Provision","Intendance","Récupère davantage de butin.","LootQuantity","perc_add",".04",".20",5,"","ui_game_symbol_pack_mule"),
        sp("Trade","Restaurateur","Améliore les prix de vente chez les marchands.","BarteringSelling","base_add","2","10",5,"","ui_game_symbol_barter"),
        sp("Elem","Cuistot endurci","Réduit les dégâts élémentaires (feu) subis.","ElementalDamageResist","base_add","2","10",5,"","ui_game_symbol_medical"),
        sp("Calm","Maître du coup de feu","Résiste aux effets négatifs.","BuffResistance","base_add","1","4",4,"","ui_game_symbol_light_armor2"),
        sp("Heat","Près des fourneaux","Améliore la résistance à la chaleur.","HyperthermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
        sp("Plate","Carrure de chef","Réduit les dégâts physiques subis.","PhysicalDamageResist","base_add","1","4",4,"","ui_game_symbol_armor_iron"),
    ]),
]

SUBCLASS_DEF = {"FarmAgri": FARM_AGRI, "FarmCook": FARM_COOK}

# ============================================================================
# Identité par les crafts (J1.13) — données de domaine pour les 12 sous-classes
# non-Fermier (Fermier reste détaillé à la main dans SUBCLASS_DEF).
# ============================================================================
# Familles d'armes -> recettes T1-T3 (noms = tags CraftingTier/RecipeTagUnlocked vérifiés).
WEAPON_TIERS = {
    "perkDeadEye":          ["gunRifleT1HuntingRifle","gunRifleT2LeverActionRifle","gunRifleT3SniperRifle"],
    "perkMachineGunner":    ["gunMGT1AK47","gunMGT2TacticalAR","gunMGT3M60"],
    "perkGunslinger":       ["gunHandgunT1Pistol","gunHandgunT2Magnum44","gunHandgunT3SMG5","gunHandgunT3DesertVulture"],
    "perkBoomstick":        ["gunShotgunT1DoubleBarrel","gunShotgunT2PumpShotgun","gunShotgunT3AutoShotgun"],
    "perkArchery":          ["gunBowT1WoodenBow","gunBowT1IronCrossbow","gunBowT3CompoundBow","gunBowT3CompoundCrossbow"],
    "perkPummelPete":       ["meleeWpnClubT1BaseballBat","meleeWpnClubT3SteelClub"],
    "perkDeepCuts":         ["meleeWpnBladeT1HuntingKnife","meleeWpnBladeT3Machete"],
    "perkJavelinMaster":    ["meleeWpnSpearT1IronSpear","meleeWpnSpearT3SteelSpear"],
    "perkSkullCrusher":     ["meleeWpnSledgeT1IronSledgehammer","meleeWpnSledgeT3SteelSledgehammer"],
    "perkBrawler":          ["meleeWpnKnucklesT1IronKnuckles","meleeWpnKnucklesT3SteelKnuckles"],
    "perkElectrocutioner":  ["meleeWpnBatonT2StunBaton"],
    "perkMiner":            ["meleeToolPickT1IronPickaxe","meleeToolAxeT1IronFireaxe","meleeToolShovelT1IronShovel",
                             "meleeToolPickT2SteelPickaxe","meleeToolAxeT2SteelAxe","meleeToolShovelT2SteelShovel",
                             "meleeToolPickT3Auger","meleeToolAxeT3Chainsaw"],
    "perkTurrets":          ["gunBotT1JunkSledge","gunBotT2JunkTurret","gunBotT3JunkDrone"],
    "perkDemolitionsExpert":["gunExplosivesT3RocketLauncher"],
}
# Armes T0 (tuyau/pierre/primitif) + outils T0 -> débloquées par Survivant (pour TOUS).
T0_ALL = ["gunHandgunT0PipePistol","gunRifleT0PipeRifle","gunMGT0PipeMachineGun","gunShotgunT0PipeShotgun",
          "gunBowT0PrimitiveBow","meleeWpnClubT0WoodenClub","meleeWpnBladeT0BoneKnife","meleeWpnSpearT0StoneSpear",
          "meleeWpnSledgeT0StoneSledgehammer","meleeWpnKnucklesT0LeatherKnuckles","meleeWpnBatonT0PipeBaton",
          "meleeToolRepairT0StoneAxe","meleeToolShovelT0StoneShovel"]
# Plats de base + eau -> débloqués par Survivant (pour TOUS).
BASE_FOODS = ["foodGrilledMeat","foodBoiledMeat","foodCornOnTheCob","foodBakedPotato","drinkJarBoiledWater","foodMeatStew"]

# ---- Crafts génériques -> rattachés à SURVIVANT (pour TOUS) ----
# (L'onglet Artisanat vanilla est masqué ; ces recettes, sans identité de classe, deviennent
#  l'identité de la classe commune. Listes extraites de recipes.xml.)
SURV_STATIONS = ["forge","workbench","chemistryStation","cementMixer","cntDewCollector",
                 "toolForgeCrucible","toolAnvil","toolCookingPot","toolCookingGrill"]
SURV_RESOURCES = ["resourceCloth","resourceCoalBundle","resourceGunPowderBundle","resourceLeadBundle","resourceLockPick","resourceLockPickBundle","resourceOil","resourceOilShaleBundle","resourcePotassiumNitratePowderBundle","resourceRocketCasing","resourceRocketTip","resourceRockSmallBundle","resourceScrapIronBundle","resourceWoodBundle"]
# Armure de base + munitions de base (lots) restent dans Survivant (pour TOUS).
SURV_ARMOR_BASIC = ["armorPrimitiveBoots","armorPrimitiveGloves","armorPrimitiveHelmet","armorPrimitiveOutfit"]
SURV_AMMO_BASIC = ["ammoBundle9mmBulletBall","ammoBundle762mmBulletBall","ammoBundle44MagnumBulletBall",
                   "ammoBundleArrowIron","ammoBundleArrowStone","ammoBundleCrossbowBoltIron",
                   "ammoBundleCrossbowBoltStone","ammoBundleShotgunShell","ammoBundleJunkTurretRegular"]

# ============================================================================
# Répartition ARMURES / MODS / MUNITIONS SPÉCIFIQUES dans les sous-classes adaptées (J1.21).
# Chaque sous-classe reçoit une sous-branche "Équipement" (déblocages auto = identité).
# ============================================================================
ARMOR_PIECES = ("Helmet", "Outfit", "Gloves", "Boots")
def armor_set(prefix): return [prefix + p for p in ARMOR_PIECES]
# Panoplie d'armure thématique par sous-classe (Primitive -> Survivant).
ARMOR_BY_CODE = {
    "SoldSnip": ("armorRanger",   "Ranger (longue portée)"),
    "SoldAslt": ("armorCommando", "Commando"),
    "ScoutTrac":("armorNomad",    "Nomade"),
    "ScoutInfi":("armorAssassin", "Assassin"),
    "SurvHunt": ("armorRogue",    "Maraudeur"),
    "SurvHerb": ("armorScavenger","Charognard"),
    "BuilArch": ("armorRaider",   "Pillard"),
    "BuilArti": ("armorMiner",    "Mineur"),
    "EngiMech": ("armorBiker",    "Motard"),
    "EngiElec": ("armorEnforcer", "Exécuteur"),
    "MedicSurg":("armorPreacher", "Prêcheur"),
    "MedicChem":("armorNerd",     "Intello"),
    "FarmAgri": ("armorFarmer",   "Fermier"),
    "FarmCook": ("armorLumberjack","Bûcheron"),
}
# Armure "Athletic" en plus pour le Pisteur (mobilité), pour couvrir les 15 panoplies non-Primitive.
ARMOR_EXTRA = {"ScoutTrac": ("armorAthletic", "Athlète")}

# Munitions spécifiques par sous-classe (les munitions de base restent dans Survivant).
AMMO_BY_CODE = {
    "SoldSnip": ["ammo762mmBulletAP","ammoBundle762mmBulletAP"],
    "SoldAslt": ["ammo762mmBulletHP","ammoBundle762mmBulletHP"],
    "ScoutTrac":["ammo9mmBulletAP","ammo9mmBulletHP","ammoBundle9mmBulletAP","ammoBundle9mmBulletHP",
                 "ammo44MagnumBulletAP","ammo44MagnumBulletHP","ammoBundle44MagnumBulletAP","ammoBundle44MagnumBulletHP"],
    "SurvHunt": ["ammoArrowExploding","ammoArrowFlaming","ammoArrowSteelAP",
                 "ammoCrossbowBoltExploding","ammoCrossbowBoltFlaming","ammoCrossbowBoltSteelAP",
                 "ammoBundleArrowExploding","ammoBundleArrowFlaming","ammoBundleArrowSteelAP",
                 "ammoBundleCrossbowBoltExploding","ammoBundleCrossbowBoltFlaming","ammoBundleCrossbowBoltSteelAP"],
    "EngiMech": ["ammoJunkTurretShell","ammoJunkTurretAP","ammoBundleJunkTurretShell","ammoBundleJunkTurretAP","ammoGasCanBundle"],
    "MedicChem":["ammoRocketFrag","ammoRocketHE","thrownAmmoPipeBomb","thrownDynamite","thrownGrenade","thrownGrenadeContact","thrownTimedCharge"],
    "FarmAgri": ["ammoShotgunSlug","ammoShotgunBreachingSlug","ammoBundleShotgunSlug","ammoBundleShotgunBreachingSlug"],
}
# Liste maîtresse des munitions à débloquer (spécifiques + lots de base) = contrôle de couverture.
AMMO_ALL = sorted(set(SURV_AMMO_BASIC) | {a for v in AMMO_BY_CODE.values() for a in v})

# Modifications par sous-classe (adaptées à l'arme/au domaine).
MODS_BY_CODE = {
    "SoldSnip": ["modGunScopeLarge","modGunScopeMedium","modGunScopeSmall","modGunReflexSight","modGunLaserSight","modGunFlashlight"],
    "SoldAslt": ["modGunBarrelExtender","modGunBipod","modGunCrippleEm","modGunDrumMagazineExtender","modGunForegrip","modGunMagazineExtender","modGunMuzzleBrake","modGunRetractingStock","modGunSoundSuppressorSilencer","modGunTriggerGroupAutomatic","modGunTriggerGroupBurst3","modGunTriggerGroupSemi"],
    "ScoutInfi":["modMeleeErgonomicGrip","modMeleeFortifyingGrip","modGunMeleeRadRemover","modGunMeleeTheHunter"],
    "SurvHunt": ["modGunBowArrowRest","modGunBowPolymerString"],
    "BuilArch": ["modMeleeBunkerBuster","modMeleeWoodSplitter","modMeleeFiremansAxeMod","modMeleeGraveDigger","modMeleeIronBreaker","modMeleeWeightedHead","modMeleeStructuralBrace"],
    "BuilArti": ["modArmorAdvancedMuffledConnectors","modArmorBandolier","modArmorCigar","modArmorCoolingMesh","modArmorCustomizedFittings","modArmorDoubleStoragePocket","modArmorHelmetLight","modArmorImpactBracing","modArmorImprovedFittings","modArmorInsulatedLiner","modArmorMuffledConnectors","modArmorPlatingBasic","modArmorPlatingReinforced","modArmorQuadStoragePocket","modArmorStealthBoots","modArmorStoragePocket","modArmorTripleStoragePocket","modArmorWaterPurifier"],
    "EngiMech": ["modVehicleArmor","modVehicleExpandedSeat","modVehicleFuelSaver","modVehicleOffRoadHeadlights","modVehiclePlow","modVehicleReserveFuelTank","modVehicleSuperCharger","modFuelTankLarge","modFuelTankSmall","modRoboticDroneArmorPlatingMod","modRoboticDroneCargoMod","modRoboticDroneHeadlampMod","modRoboticDroneMedicMod","modRoboticDroneMoraleBoosterMod","modRoboticDroneWeaponMod"],
    "EngiElec": ["modMeleeStunBatonRepulsor"],
    "MedicSurg":["modMeleeSerratedBlade","modMeleeTemperedBlade","modMeleeDiamondTip"],
    "FarmAgri": ["modGunChoke","modGunDuckbill","modGunShotgunTubeExtenderMagazine","modShotgunSawedOffBarrel"],
    "FarmCook": ["modMeleeClubBarbedWire","modMeleeClubBurningShaft","modMeleeClubMetalChain","modMeleeClubMetalSpikes"],
}
MODS_ALL = sorted({m for v in MODS_BY_CODE.values() for m in v})

# Panoplie d'armure -> code de sous-classe (pour router les recettes craftingArmor vanilla).
ARMORSET2CODE = {}
for _c, (_p, _l) in list(ARMOR_BY_CODE.items()) + list(ARMOR_EXTRA.items()):
    ARMORSET2CODE[_p] = _c
# Compétence d'artisanat vanilla -> notre sous-classe (migration des crafts level/livres).
CRAFTSKILL2CLASS = {
    "craftingHandguns": "ScoutTrac", "craftingRifles": "SoldSnip", "craftingShotguns": "FarmAgri",
    "craftingMachineGuns": "SoldAslt", "craftingBows": "SurvHunt", "craftingExplosives": "MedicChem",
    "craftingBlades": "MedicSurg", "craftingClubs": "FarmCook", "craftingKnuckles": "ScoutInfi",
    "craftingSpears": "SurvHerb", "craftingSledgehammers": "BuilArch", "craftingHarvestingTools": "BuilArti",
    "craftingRepairTools": "BuilArti", "craftingSalvageTools": "EngiMech", "craftingRobotics": "EngiMech",
    "craftingElectrician": "EngiElec", "craftingVehicles": "EngiMech", "craftingMedical": "MedicSurg",
    "craftingFood": "FarmCook", "craftingSeeds": "FarmAgri", "craftingTraps": "EngiElec",
    "craftingWorkstations": "Common", "craftingArmor": "Common",  # armor routé par panoplie ci-dessous
}

def route_recipe(recipe, skill):
    """Recette vanilla -> code de classe. Les bases (T0, primitive, plats de base) -> Survivant."""
    if "T0" in recipe:
        return "Common"
    if recipe.startswith("armor"):
        if recipe.startswith("armorPrimitive") or recipe.endswith("Master"):
            return "Common"
        for pref, code in ARMORSET2CODE.items():
            if recipe.startswith(pref):
                return code
        return "Common"
    if recipe in BASE_FOODS:
        return "Common"
    return CRAFTSKILL2CLASS.get(skill, "Common")

def ammo_palier(r):
    if any(k in r for k in ("Exploding", "Flaming", "SteelAP", "RocketHE", "RocketFrag", "Breaching")):
        return 24
    return 12

# Sous-branche d'accueil d'un déblocage (regroupement UI). Survivant = découpage fin.
def unlock_bucket(code, recipe):
    if code == "Common":
        if recipe.startswith(("gun", "meleeWpn", "meleeTool")): return ("BArme", "Armes de base", "ui_game_symbol_knife")
        if recipe.startswith("armor"):                          return ("BArmure", "Armures de base", "ui_game_symbol_armor_iron")
        if recipe.startswith(("food", "drink")):                return ("BCuisine", "Cuisine de survie", "ui_game_symbol_fork")
        if recipe.startswith(("ammo", "thrown")):               return ("BMuns", "Munitions de base", "ui_game_symbol_rifle")
        if recipe.startswith("resource"):                       return ("BMat", "Matériaux", "ui_game_symbol_smelt")
        return ("BAtelier", "Établis & stations", "ui_game_symbol_workbench")
    if recipe.startswith(("gun", "meleeWpn", "meleeTool")):     return ("FArme", "Fabrication d'armes", "ui_game_symbol_knife")
    if recipe.startswith(("armor", "mod")):                     return ("FEquip", "Équipement", "ui_game_symbol_armor_iron")
    if recipe.startswith(("ammo", "thrown")):                   return ("FMuns", "Munitions", "ui_game_symbol_rifle")
    return ("FFab", "Fabrication", "ui_game_symbol_workbench")

# Domaine de craft par sous-classe : (tag de catégorie pour CraftingTime/déblocage, libellé FR).
DOMAIN = {
    "SoldSnip": ("perkDeadEye","fusils de précision"),
    "SoldAslt": ("perkMachineGunner","armes automatiques"),
    "ScoutTrac": ("perkGunslinger","pistolets"),
    "ScoutInfi": ("perkBrawler","armes de poing et pillage"),
    "SurvHunt": ("perkArchery","arcs et chasse"),
    "SurvHerb": ("craftingMedical","remèdes naturels"),
    "BuilArch": ("cementMixerCrafting","construction et fortifications"),
    "BuilArti": ("craftingHarvestingTools","outils et équipement"),
    "EngiMech": ("perkGreaseMonkey","véhicules et robotique"),
    "EngiElec": ("perkAdvancedEngineering","électricité et pièges"),
    "MedicSurg": ("craftingMedical","médecine"),
    "MedicChem": ("chemStationCrafting","chimie et explosifs"),
}

# ---- SURVIVANT (classe commune, pour TOUS) : socle vital MINIMAL + bases ----
# Survivant ne garde QUE des stats vitales "universelles" (santé, nourriture, XP, résistance
# générale). Tous les autres génériques (endurance, port, résistances spécifiques, thermie...)
# sont RÉPARTIS dans les sous-classes (cf RESERVED_SURVIVOR + validate()). Aucun TYPE d'effet
# de Survivant n'apparaît dans une sous-classe -> zéro doublon général<->sous-classe.
RESERVED_SURVIVOR = {"HealthMax", "FoodMax", "PlayerExpGain", "GeneralDamageResist"}
# Survivant = stats vitales (branche "Survie"). Les déblocages de craft (armes T0, armure
# primitive, établis, cuisine, munitions de base, matériaux) sont générés en PER-RECETTE
# par collect_unlocks() (1 point chacun, gatés par niveau) -> classe "bien plus développée".
SURVIVOR_STATS = [
    sp("Vitalite","Vitalité","Augmente votre santé maximale.","HealthMax","base_add","5","25",5,"","ui_game_symbol_healing_factor"),
    sp("Metab","Métabolisme","Augmente votre nourriture maximale.","FoodMax","base_add","5","25",5,"","ui_game_symbol_stomach"),
    sp("Consti","Constitution","Réduit légèrement tous les dégâts subis.","GeneralDamageResist","base_add","1","3",3,"","ui_game_symbol_armor_iron"),
    sp("Survie","Instinct de survie","Augmente toute l'expérience gagnée.","PlayerExpGain","perc_add",".02",".10",5,"","ui_game_symbol_adventure"),
]

# ---- Spécialité UNIQUE par sous-classe (perks thématiques, pas de générique répété) ----
THEME_SPEC = {
    "SoldSnip": [
        sp("Cover","Sous le feu","Réduit les dégâts d'explosion subis.","ExplosionIncomingDamage","perc_add","-.06","-.30",5,"","ui_game_symbol_armor_iron"),
        sp("Plates","Tenue pare-balles","Réduit les dégâts élémentaires subis.","ElementalDamageResist","base_add","2","10",5,"","ui_game_symbol_armor_iron"),
        sp("Recon","Repérage de cibles","Améliore la qualité du butin trouvé.","LootStage","perc_add",".04",".20",5,"","ui_game_symbol_map"),
        sp("Calm","Sang-froid","Résiste aux effets négatifs en plein combat.","BuffResistance","base_add","1","4",4,"","ui_game_symbol_light_armor2"),
        sp("Hold","Position dominante","Réduit les dégâts physiques subis.","PhysicalDamageResist","base_add","1","5",5,"","ui_game_symbol_armor_iron"),
        sp("Quarter","Économe de guerre","Améliore les prix de vente chez les marchands.","BarteringSelling","base_add","2","10",5,"","ui_game_symbol_barter"),
    ],
    "SoldAslt": [
        sp("Heavy","Blindage lourd","Réduit fortement les dégâts physiques subis.","PhysicalDamageResist","base_add","1","6",6,"","ui_game_symbol_armor_iron"),
        sp("Blast","Anti-souffle","Réduit les dégâts d'explosion subis.","ExplosionIncomingDamage","perc_add","-.08","-.40",5,"","ui_game_symbol_armor_iron"),
        sp("Suit","Combinaison de combat","Réduit les dégâts élémentaires subis.","ElementalDamageResist","base_add","2","12",6,"","ui_game_symbol_armor_iron"),
        sp("Push","Percée","Augmente votre mobilité sous le feu.","Mobility","perc_add",".02",".10",5,"","ui_game_symbol_run"),
        sp("Belt","Ceinture de munitions","Récupère davantage de butin.","LootQuantity","perc_add",".04",".20",5,"","ui_game_symbol_pack_mule"),
        sp("Morale","Cri de guerre","Résiste aux effets négatifs.","BuffResistance","base_add","1","4",4,"","ui_game_symbol_light_armor2"),
    ],
    "ScoutTrac": [
        sp("Run","Coureur des bois","Augmente votre mobilité.","Mobility","perc_add",".04",".20",5,"","ui_game_symbol_run"),
        sp("Quiet","Pas feutrés","Réduit le bruit que vous faites.","NoiseMultiplier","perc_add","-.05","-.25",5,"","ui_game_symbol_stealth"),
        sp("Eye","Œil d'éclaireur","Améliore la qualité du butin trouvé.","LootStage","perc_add",".05",".25",5,"","ui_game_symbol_map"),
        sp("Trade","Négociateur","Améliore les prix d'achat chez les marchands.","BarteringBuying","base_add","2","10",5,"","ui_game_symbol_barter"),
        sp("Glean","Glaneur","Récupère davantage de butin.","LootQuantity","perc_add",".04",".20",5,"","ui_game_symbol_pack_mule"),
        sp("Heat","Routard","Améliore la résistance à la chaleur.","HyperthermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
    ],
    "ScoutInfi": [
        sp("Shadow","Ombre","Réduit fortement le bruit que vous faites.","NoiseMultiplier","perc_add","-.06","-.30",5,"","ui_game_symbol_stealth"),
        sp("Sneak","Démarche feutrée","Augmente votre mobilité.","Mobility","perc_add",".03",".15",5,"","ui_game_symbol_run"),
        sp("Lock","Crocheteur","Crochète les serrures plus vite.","LockPickTime","perc_subtract",".1",".5",5,"","ui_game_symbol_lock"),
        sp("Loot","Pillard","Récupère davantage de butin.","LootQuantity","perc_add",".05",".25",5,"","ui_game_symbol_pack_mule"),
        sp("Thief","Œil du voleur","Améliore la qualité du butin trouvé.","LootStage","perc_add",".05",".25",5,"","ui_game_symbol_map"),
        sp("Rare","Fouineur","Augmente les chances de butin rare.","LootDropProb","perc_add",".05",".25",5,"","ui_game_symbol_map"),
    ],
    "SurvHunt": [
        sp("Skinner","Dépeceur","Récolte plus de viande, de cuir et d'os sur les animaux.","HarvestCount","perc_add",".10",".50",5,"butcherHarvest","ui_game_symbol_pack_mule"),
        sp("Track","Traqueur","Augmente votre mobilité en extérieur.","Mobility","perc_add",".03",".15",5,"","ui_game_symbol_run"),
        sp("Cold","Trappeur","Améliore la résistance au froid.","HypothermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
        sp("Quiet","Approche silencieuse","Réduit le bruit que vous faites.","NoiseMultiplier","perc_add","-.04","-.20",5,"","ui_game_symbol_stealth"),
        sp("Forage","Fourrageur","Améliore la qualité du butin de fouille.","LootStage","perc_add",".04",".20",5,"","ui_game_symbol_map"),
        sp("Heat","Endurci au climat","Améliore la résistance à la chaleur.","HyperthermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
    ],
    "SurvHerb": [
        sp("Gather","Cueilleur émérite","Récolte plus sur les plantes sauvages.","HarvestCount","perc_add",".10",".50",5,"wildCropsHarvest","ui_game_symbol_crops"),
        sp("Toxin","Anticorps","Résiste fortement aux effets négatifs (poisons, maladies).","BuffResistance","base_add","1","5",5,"","ui_game_symbol_medical"),
        sp("Cold","Acclimaté au froid","Améliore la résistance au froid.","HypothermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
        sp("Heat","Acclimaté à la chaleur","Améliore la résistance à la chaleur.","HyperthermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
        sp("Elem","Onguents protecteurs","Réduit les dégâts élémentaires subis.","ElementalDamageResist","base_add","2","10",5,"","ui_game_symbol_medical"),
        sp("Forage","Herboriste chevronné","Améliore la qualité du butin de fouille.","LootStage","perc_add",".03",".15",5,"","ui_game_symbol_map"),
    ],
    "BuilArch": [
        sp("Quarry","Carrier","Récolte plus de minerai et de bois.","HarvestCount","perc_add",".10",".50",5,"oreWoodHarvest","ui_game_symbol_pack_mule"),
        sp("Trap","Génie défensif","Réduit les dégâts subis de vos propres pièges.","TrapIncomingDamage","perc_add","-.1","-.5",5,"","ui_game_symbol_armor_iron"),
        sp("Blast","Bâtisseur solide","Réduit les dégâts d'explosion subis.","ExplosionIncomingDamage","perc_add","-.06","-.30",5,"","ui_game_symbol_armor_iron"),
        sp("Haul","Bête de somme","Ajoute des emplacements de portage pour les matériaux.","CarryCapacity","base_add","2","10",5,"","ui_game_symbol_pack_mule"),
        sp("Plate","Carapace","Réduit les dégâts physiques subis.","PhysicalDamageResist","base_add","1","5",5,"","ui_game_symbol_armor_iron"),
        sp("Heat","Forgeron endurci","Améliore la résistance à la chaleur.","HyperthermalResist","base_add","2","10",5,"","ui_game_symbol_temperature"),
    ],
    "BuilArti": [
        sp("Scrap","Récupérateur","Récupère plus de ressources en démontant.","HarvestCount","perc_add",".10",".50",5,"salvageHarvest","ui_game_symbol_pack_mule"),
        sp("Trade","Marchand","Améliore les prix de vente.","BarteringSelling","base_add","2","10",5,"","ui_game_symbol_barter"),
        sp("Deal","Acheteur avisé","Améliore les prix d'achat.","BarteringBuying","base_add","2","10",5,"","ui_game_symbol_barter"),
        sp("Eye","Brocanteur","Améliore la qualité du butin.","LootStage","perc_add",".05",".25",5,"","ui_game_symbol_map"),
        sp("Stock","Magasinier","Récupère davantage de butin.","LootQuantity","perc_add",".04",".20",5,"","ui_game_symbol_pack_mule"),
        sp("Plate","Atelier blindé","Réduit les dégâts physiques subis.","PhysicalDamageResist","base_add","1","4",4,"","ui_game_symbol_armor_iron"),
    ],
    "EngiMech": [
        sp("Wreck","Ferrailleur","Récupère plus de pièces en démontant.","HarvestCount","perc_add",".10",".50",5,"salvageHarvest","ui_game_symbol_wrench"),
        sp("Drive","Pilote","Augmente votre mobilité.","Mobility","perc_add",".03",".15",5,"","ui_game_symbol_run"),
        sp("Spark","Isolation","Réduit les dégâts élémentaires subis.","ElementalDamageResist","base_add","2","10",5,"","ui_game_symbol_electric_generator"),
        sp("Blast","Châssis renforcé","Réduit les dégâts d'explosion subis.","ExplosionIncomingDamage","perc_add","-.06","-.30",5,"","ui_game_symbol_armor_iron"),
        sp("Parts","Magasin de pièces","Récupère davantage de butin.","LootQuantity","perc_add",".04",".20",5,"","ui_game_symbol_pack_mule"),
        sp("Trade","Casse auto","Améliore les prix de vente.","BarteringSelling","base_add","2","10",5,"","ui_game_symbol_barter"),
    ],
    "EngiElec": [
        sp("Disman","Démonteur","Récupère plus de composants en démontant.","HarvestCount","perc_add",".10",".50",5,"salvageHarvest","ui_game_symbol_wrench"),
        sp("Insul","Isolation électrique","Réduit fortement les dégâts élémentaires subis.","ElementalDamageResist","base_add","3","15",5,"","ui_game_symbol_electric_generator"),
        sp("Trap","Maître des pièges","Réduit les dégâts subis de vos propres pièges.","TrapIncomingDamage","perc_add","-.1","-.5",5,"","ui_game_symbol_electric_generator"),
        sp("Light","Œil dans le noir","Améliore la qualité du butin trouvé.","LootStage","perc_add",".04",".20",5,"","ui_game_symbol_map"),
        sp("Quiet","Discrétion électronique","Réduit le bruit que vous faites.","NoiseMultiplier","perc_add","-.04","-.20",5,"","ui_game_symbol_stealth"),
        sp("Plate","Combinaison isolante","Réduit les dégâts physiques subis.","PhysicalDamageResist","base_add","1","4",4,"","ui_game_symbol_armor_iron"),
    ],
    "MedicSurg": [
        sp("Steady","Mains stables","Résiste fortement aux effets négatifs.","BuffResistance","base_add","1","5",5,"","ui_game_symbol_medical"),
        sp("Sterile","Asepsie","Réduit les dégâts élémentaires subis.","ElementalDamageResist","base_add","2","10",5,"","ui_game_symbol_medical"),
        sp("Calm","Sang-froid clinique","Réduit les dégâts d'explosion subis.","ExplosionIncomingDamage","perc_add","-.05","-.25",5,"","ui_game_symbol_armor_iron"),
        sp("Supply","Pharmacie","Améliore la qualité du butin trouvé.","LootStage","perc_add",".04",".20",5,"","ui_game_symbol_map"),
        sp("Tough","Constitution de fer","Réduit les dégâts physiques subis.","PhysicalDamageResist","base_add","1","5",5,"","ui_game_symbol_armor_iron"),
        sp("Trade","Praticien","Améliore les prix de vente.","BarteringSelling","base_add","2","10",5,"","ui_game_symbol_barter"),
    ],
    "MedicChem": [
        sp("Hazmat","Combinaison NBC","Réduit fortement les dégâts élémentaires subis.","ElementalDamageResist","base_add","3","15",5,"","ui_game_symbol_science"),
        sp("Antitox","Antidote","Résiste fortement aux effets négatifs.","BuffResistance","base_add","1","5",5,"","ui_game_symbol_science"),
        sp("Blast","Manipulation prudente","Réduit les dégâts d'explosion subis.","ExplosionIncomingDamage","perc_add","-.08","-.40",5,"","ui_game_symbol_science"),
        sp("Lab","Laborantin","Améliore la qualité du butin trouvé.","LootStage","perc_add",".04",".20",5,"","ui_game_symbol_map"),
        sp("Yield","Distillateur","Récupère davantage de butin.","LootQuantity","perc_add",".04",".20",5,"","ui_game_symbol_pack_mule"),
        sp("Quiet","Pas discrets","Réduit le bruit que vous faites.","NoiseMultiplier","perc_add","-.04","-.20",5,"","ui_game_symbol_stealth"),
    ],
}

def build_domain_subbranches(code):
    """Construit ~20 perks (3 sous-branches : Arme / Métier / Spécialité) pour une sous-classe
    à partir de son arme (WEAPON_TIERS) et de son domaine de craft (DOMAIN). Tout en français."""
    c,en,fr,tag,kind,fid,icon,efl,ffl = SUB_BY_CODE[code]
    tiers = WEAPON_TIERS.get(tag, [])
    catTag, domFR = DOMAIN[code]
    wic = icon
    # --- Sous-branche ARME (maîtrise de l'arme de classe) ---
    # PERKS[kind] est autonome : chaque effet est unique (pas de doublon intra-branche).
    arme = []
    for (suf,pen,pfr,nm,op,v1,v5,scoped,ed,fd) in PERKS[kind]:
        arme.append(stat(suf,pfr,pfr,nm,op,v1,v5,5, tag if scoped else "", fd, fd, wic))
    # --- Sous-branche MÉTIER (identité de craft) ---
    metier = []
    if tiers:
        metier.append(stat("Quality","Maîtrise d'artisanat","Maîtrise d'artisanat","CraftingTier","base_add","1","5",5, ",".join(tiers),
                           f"Améliore la qualité de ce que vous fabriquez ({domFR}).",
                           f"Améliore la qualité de ce que vous fabriquez ({domFR}).","ui_game_symbol_workbench"))
    metier.append(stat("Speed","Production rapide","Production rapide","CraftingTime","perc_add","-.10","-.50",5, catTag,
                       f"Fabrique plus vite ({domFR}).",f"Fabrique plus vite ({domFR}).","ui_game_symbol_workbench"))
    # NB: les déblocages de recettes (tiers d'armes, items de domaine, signature) sont désormais
    # générés en PER-RECETTE et gatés par niveau par collect_unlocks() -> sous-branches dédiées.
    # --- Sous-branche SPÉCIALITÉ (stats thématiques) ---
    # Spécialité UNIQUE par sous-classe (plus aucun générique : ils sont chez Survivant).
    spec = list(THEME_SPEC.get(code, []))
    return [("Arme", "Arme", "Arme", wic, arme),
            ("Metier", "Métier", "Métier", "ui_game_symbol_workbench", metier),
            ("Spec", "Spécialité", "Spécialité", "ui_game_symbol_character", spec)]

# NB: le système de déblocages per-recette (collect_unlocks/subbranches_for) est défini APRÈS
# CRAFTABLES (il en a besoin), plus bas dans le fichier.

# ============================================================================
# CRAFTABLES signature (items + recettes + buffs + loc), référencés par les unlocks.
# ============================================================================
def _food_item(name, icon_tint, desckey, food, health, water, buff, aoe):
    aoe_line = f'\n        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="{buff}" target="otherAOE" range="25"/>' if (buff and aoe) else ""
    buff_line = f'\n        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="{buff}"/>' if buff else ""
    return f'''    <item name="{name}">
      <property name="Tags" value="food,foodSkill,fitness"/>
      <property name="HoldType" value="31"/>
      <property name="DisplayType" value="foodWater"/>
      <property name="Meshfile" value="@:Other/Items/Misc/parcelPrefab.prefab"/>
      <property name="DropMeshfile" value="@:Other/Items/Misc/sack_droppedPrefab.prefab"/>
      <property name="Material" value="Morganic"/>
      <property name="Stacknumber" value="20"/>
      <property name="EconomicValue" value="200"/>
      <property name="CustomIcon" value="foodMeatStew"/>
      <property name="CustomIconTint" value="{icon_tint}"/>
      <property name="DescriptionKey" value="{desckey}"/>
      <property name="SoundPickup" value="food_bowl1_grab"/>
      <property name="SoundPlace" value="food_bowl1_place"/>
      <property class="Action0">
        <property name="Class" value="Eat"/>
        <property name="Delay" value="1.0"/>
        <property name="Sound_start" value="player_drinking"/>
      </property>
      <property name="Group" value="Food/Cooking"/>
      <effect_group name="{name}" tiered="false">
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="$foodAmountAdd" operation="add" value="{food}"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="foodHealthAmount" operation="add" value="{health}"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="$waterAmountAdd" operation="add" value="{water}"/>{buff_line}{aoe_line}
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="buffProcessConsumables"/>
      </effect_group>
    </item>'''

def _team_buff(name, namekey, desckey, icon, color, resist, stamloss, stamregen):
    extra = f'\n        <passive_effect name="StaminaChangeOT" operation="perc_add" value="{stamregen}"/>' if stamregen else ""
    return f'''    <buff name="{name}" name_key="{namekey}" description_key="{desckey}" icon="{icon}" icon_color="{color}">
      <duration value="600"/>
      <stack_type value="replace"/>
      <effect_group>
        <passive_effect name="PhysicalDamageResist" operation="base_add" value="{resist}"/>
        <passive_effect name="StaminaLoss" operation="perc_add" value="{stamloss}"/>{extra}
      </effect_group>
    </buff>'''

CRAFTABLES = {
    "FarmAgri": {
        "items": [
            # Slug : Extends ammoShotgunSlug (base_set 102 tags perkBoomstick) ; +60% en perc_add.
            '''    <item name="dhsAmmoFarmerSlug">
      <property name="Extends" value="ammoShotgunSlug"/>
      <property name="CustomIcon" value="ammoShotgunSlug"/>
      <property name="CustomIconTint" value="ffcc44"/>
      <property name="DescriptionKey" value="dhsAmmoFarmerSlugDesc"/>
      <property name="EconomicValue" value="40"/>
      <effect_group name="dhsFarmerSlug" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".6" tags="perkBoomstick"/>
        <passive_effect name="BlockDamage" operation="perc_add" value=".5" tags="perkBoomstick"/>
      </effect_group>
    </item>''',
            # Buckshot : Extends ammoShotgunShell ; +50% dégâts.
            '''    <item name="dhsAmmoFarmerBuck">
      <property name="Extends" value="ammoShotgunShell"/>
      <property name="CustomIcon" value="ammoShotgunShell"/>
      <property name="CustomIconTint" value="ff8844"/>
      <property name="DescriptionKey" value="dhsAmmoFarmerBuckDesc"/>
      <property name="EconomicValue" value="30"/>
      <effect_group name="dhsFarmerBuck" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".5" tags="perkBoomstick"/>
        <passive_effect name="BlockDamage" operation="perc_add" value=".4" tags="perkBoomstick"/>
      </effect_group>
    </item>''',
            _food_item("dhsFoodPreserves","cc8844","dhsFoodPreservesDesc","40","20","10",None,False),
        ],
        "recipes": [
            '<recipe name="dhsAmmoFarmerSlug" count="2" craft_area="workbench" craft_time="4" tags="learnable,workbenchCrafting,dhsCraftFarmAgri"><ingredient name="ammoShotgunShell" count="3"/><ingredient name="resourceGunPowder" count="4"/><ingredient name="resourceForgedIron" count="1"/></recipe>',
            '<recipe name="dhsAmmoFarmerBuck" count="6" craft_area="workbench" craft_time="3" tags="learnable,workbenchCrafting,dhsCraftFarmAgri"><ingredient name="resourceGunPowder" count="4"/><ingredient name="resourceForgedIron" count="1"/></recipe>',
            '<recipe name="dhsFoodPreserves" count="2" craft_area="campfire" craft_tool="toolCookingPot" craft_time="20" tags="learnable,dhsCraftFarmAgri"><ingredient name="foodGrilledMeat" count="3"/><ingredient name="foodCropPotato" count="2"/><ingredient name="drinkJarBoiledWater" count="1"/></recipe>',
        ],
        "buffs": [],
        "loc": [
            ("dhsAmmoFarmerSlug","Farmer Slug","Cartouche de fermier"),
            ("dhsAmmoFarmerSlugDesc","A heavy hand-packed slug that hits much harder than a standard slug. Crafted only by Farmers.",
             "Une lourde balle montée main, bien plus puissante qu'une balle standard. Fabriquée uniquement par les Agriculteurs."),
            ("dhsAmmoFarmerBuck","Farmer Buckshot","Chevrotine de fermier"),
            ("dhsAmmoFarmerBuckDesc","Heavy hand-packed buckshot for close work. Crafted only by Farmers.",
             "Lourde chevrotine montée main pour le combat rapproché. Fabriquée uniquement par les Agriculteurs."),
            ("dhsFoodPreserves","Farmer's Preserves","Conserves du fermier"),
            ("dhsFoodPreservesDesc","Home-canned food: filling, keeps well, stacks deep. Cooked only by Farmers.",
             "Conserve maison : copieuse, se garde longtemps, s'empile. Cuisinée uniquement par les Agriculteurs."),
        ],
    },
    "FarmCook": {
        "items": [
            _food_item("dhsFoodFeast","ff9933","dhsFoodFeastDesc","60","30","25","dhsBuffFeast",True),
            _food_item("dhsFoodFeastGrand","ffcc33","dhsFoodFeastGrandDesc","80","40","30","dhsBuffFeastGrand",True),
            # Tonique : Extends drinkJarCoffee (gère l'eau) ; on AJOUTE juste le buff (soi + AOE).
            '''    <item name="dhsDrinkTonic">
      <property name="Extends" value="drinkJarCoffee"/>
      <property name="CustomIcon" value="drinkJarCoffee"/>
      <property name="CustomIconTint" value="ffaa55"/>
      <property name="DescriptionKey" value="dhsDrinkTonicDesc"/>
      <property name="EconomicValue" value="120"/>
      <effect_group name="dhsTonic" tiered="false">
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="dhsBuffTonic"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="dhsBuffTonic" target="otherAOE" range="25"/>
      </effect_group>
    </item>''',
        ],
        "recipes": [
            '<recipe name="dhsFoodFeast" count="1" craft_area="campfire" craft_tool="toolCookingPot" craft_time="30" tags="learnable,dhsCraftFarmCook"><ingredient name="foodGrilledMeat" count="3"/><ingredient name="foodCropPotato" count="3"/><ingredient name="foodCropCorn" count="3"/><ingredient name="resourceAnimalFat" count="2"/><ingredient name="drinkJarBoiledWater" count="2"/></recipe>',
            '<recipe name="dhsFoodFeastGrand" count="1" craft_area="campfire" craft_tool="toolCookingPot" craft_time="45" tags="learnable,dhsCraftFarmCook"><ingredient name="foodGrilledMeat" count="4"/><ingredient name="foodCropPotato" count="4"/><ingredient name="foodCropCorn" count="4"/><ingredient name="resourceAnimalFat" count="3"/><ingredient name="drinkJarBoiledWater" count="3"/></recipe>',
            '<recipe name="dhsDrinkTonic" count="2" craft_area="campfire" craft_tool="toolCookingPot" craft_time="15" tags="learnable,dhsCraftFarmCook"><ingredient name="drinkJarBoiledWater" count="2"/><ingredient name="foodCropCorn" count="2"/></recipe>',
        ],
        "buffs": [
            _team_buff("dhsBuffFeast","dhsBuffFeastName","dhsBuffFeastDesc","ui_game_symbol_fork","255,153,51","5","-.15",None),
            _team_buff("dhsBuffFeastGrand","dhsBuffFeastGrandName","dhsBuffFeastGrandDesc","ui_game_symbol_fork","255,204,51","8","-.25",".25"),
            _team_buff("dhsBuffTonic","dhsBuffTonicName","dhsBuffTonicDesc","ui_game_symbol_cardio","255,170,85","2","-.15",".35"),
        ],
        "loc": [
            ("dhsFoodFeast","Team Feast","Festin d'équipe"),
            ("dhsFoodFeastDesc","A hearty shared meal. Feeds you well and buffs nearby allies. Cooked only by Cooks.",
             "Un copieux repas partagé. Vous rassasie et buff les alliés proches. Cuisiné uniquement par les Cuisiniers."),
            ("dhsFoodFeastGrand","Grand Feast","Grand festin"),
            ("dhsFoodFeastGrandDesc","A lavish shared banquet. Feeds and strongly buffs nearby allies. Cooked only by Cooks.",
             "Un banquet partagé fastueux. Nourrit et buff fortement les alliés proches. Cuisiné uniquement par les Cuisiniers."),
            ("dhsDrinkTonic","Cook's Tonic","Tonique du chef"),
            ("dhsDrinkTonicDesc","A reviving brew. Drinking it boosts stamina recovery for you and nearby allies.",
             "Un breuvage revigorant. Le boire booste la récupération d'endurance pour vous et les alliés proches."),
            ("dhsBuffFeastName","Team Feast","Festin d'équipe"),
            ("dhsBuffFeastDesc","Well fed by a Cook: reduced damage taken and stamina use.",
             "Bien nourri par un Cuisinier : dégâts subis et endurance dépensée réduits."),
            ("dhsBuffFeastGrandName","Grand Feast","Grand festin"),
            ("dhsBuffFeastGrandDesc","Feasted by a Cook: greatly reduced damage taken, stamina use and faster stamina recovery.",
             "Festoyé par un Cuisinier : dégâts subis et endurance fortement réduits, récupération accélérée."),
            ("dhsBuffTonicName","Cook's Tonic","Tonique du chef"),
            ("dhsBuffTonicDesc","Energized by a Cook's tonic: faster stamina recovery and less stamina use.",
             "Revigoré par le tonique du chef : récupération d'endurance accélérée, moins d'endurance dépensée."),
        ],
    },
    # ---- Signatures des sous-classes "domaine" (munitions/medical/jet/boisson via Extends) ----
    "SoldSnip": {
        "items": ['''    <item name="dhsAmmoMatchAP">
      <property name="Extends" value="ammo762mmBulletAP"/>
      <property name="CustomIcon" value="ammo762mmBulletAP"/>
      <property name="CustomIconTint" value="cce066"/>
      <property name="DescriptionKey" value="dhsAmmoMatchAPDesc"/>
      <effect_group name="dhsMatchAP" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".35" tags="perkDeadEye"/>
        <passive_effect name="BlockDamage" operation="perc_add" value=".3" tags="perkDeadEye"/>
      </effect_group>
    </item>'''],
        "recipes": ['<recipe name="dhsAmmoMatchAP" count="6" craft_area="workbench" craft_time="4" tags="learnable,workbenchCrafting,perkDeadEye"><ingredient name="resourceGunPowder" count="5"/><ingredient name="resourceForgedIron" count="2"/></recipe>'],
        "buffs": [],
        "loc": [("dhsAmmoMatchAP","Cartouche de match perforante","Cartouche de match perforante"),
                ("dhsAmmoMatchAPDesc","Munition de précision montée main : dégâts et perforation accrus. Fabriquée uniquement par le Tireur d'élite.","Munition de précision montée main : dégâts et perforation accrus. Fabriquée uniquement par le Tireur d'élite.")],
        "sigperks": [unlock("SigAmmo","Munitions de précision","Munitions de précision","ui_game_symbol_long_shot","dhsAmmoMatchAP",True,1,
                            "Débloque la fabrication des Cartouches de match perforantes.","Débloque la fabrication des Cartouches de match perforantes.")],
    },
    "SoldAslt": {
        "items": ['''    <item name="dhsAmmoBattle">
      <property name="Extends" value="ammo762mmBulletBall"/>
      <property name="CustomIcon" value="ammo762mmBulletBall"/>
      <property name="CustomIconTint" value="e09966"/>
      <property name="DescriptionKey" value="dhsAmmoBattleDesc"/>
      <effect_group name="dhsBattle" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".30" tags="perkMachineGunner"/>
      </effect_group>
    </item>'''],
        "recipes": ['<recipe name="dhsAmmoBattle" count="10" craft_area="workbench" craft_time="4" tags="learnable,workbenchCrafting,perkMachineGunner"><ingredient name="resourceGunPowder" count="6"/><ingredient name="resourceForgedIron" count="2"/></recipe>'],
        "buffs": [],
        "loc": [("dhsAmmoBattle","Cartouche de combat","Cartouche de combat"),
                ("dhsAmmoBattleDesc","Munition de combat surchargée pour le tir nourri. Fabriquée uniquement par l'Assaut.","Munition de combat surchargée pour le tir nourri. Fabriquée uniquement par l'Assaut.")],
        "sigperks": [unlock("SigAmmo","Munitions de combat","Munitions de combat","ui_game_symbol_rifle","dhsAmmoBattle",True,1,
                            "Débloque la fabrication des Cartouches de combat.","Débloque la fabrication des Cartouches de combat.")],
    },
    "ScoutTrac": {
        "items": ['''    <item name="dhsAmmoLight">
      <property name="Extends" value="ammo9mmBulletHP"/>
      <property name="CustomIcon" value="ammo9mmBulletHP"/>
      <property name="CustomIconTint" value="66cce0"/>
      <property name="DescriptionKey" value="dhsAmmoLightDesc"/>
      <effect_group name="dhsLight" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".30" tags="perkGunslinger"/>
      </effect_group>
    </item>'''],
        "recipes": ['<recipe name="dhsAmmoLight" count="10" craft_area="workbench" craft_time="3" tags="learnable,workbenchCrafting,perkGunslinger"><ingredient name="resourceGunPowder" count="4"/><ingredient name="resourceForgedIron" count="1"/></recipe>'],
        "buffs": [],
        "loc": [("dhsAmmoLight","Balle légère du pisteur","Balle légère du pisteur"),
                ("dhsAmmoLightDesc","Balle de pistolet allégée, dégâts accrus pour le tir rapide. Fabriquée uniquement par le Pisteur.","Balle de pistolet allégée, dégâts accrus pour le tir rapide. Fabriquée uniquement par le Pisteur.")],
        "sigperks": [unlock("SigAmmo","Munitions du pisteur","Munitions du pisteur","ui_game_symbol_run","dhsAmmoLight",True,1,
                            "Débloque la fabrication des Balles légères du pisteur.","Débloque la fabrication des Balles légères du pisteur.")],
    },
    "SurvHunt": {
        "items": ['''    <item name="dhsAmmoHuntArrow">
      <property name="Extends" value="ammoArrowIron"/>
      <property name="CustomIcon" value="ammoArrowIron"/>
      <property name="CustomIconTint" value="66cc66"/>
      <property name="DescriptionKey" value="dhsAmmoHuntArrowDesc"/>
      <effect_group name="dhsHuntArrow" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".5" tags="perkArchery"/>
      </effect_group>
    </item>'''],
        "recipes": ['<recipe name="dhsAmmoHuntArrow" count="4" craft_area="workbench" craft_time="3" tags="learnable,workbenchCrafting,perkArchery"><ingredient name="ammoArrowIron" count="4"/><ingredient name="resourceForgedIron" count="1"/></recipe>'],
        "buffs": [],
        "loc": [("dhsAmmoHuntArrow","Flèche de chasse","Flèche de chasse"),
                ("dhsAmmoHuntArrowDesc","Flèche lourde de chasseur, bien plus pénétrante sur le gibier et les morts. Fabriquée uniquement par le Chasseur.","Flèche lourde de chasseur, bien plus pénétrante sur le gibier et les morts. Fabriquée uniquement par le Chasseur.")],
        "sigperks": [unlock("SigArrow","Carquois du chasseur","Carquois du chasseur","ui_game_symbol_archery","dhsAmmoHuntArrow",True,1,
                            "Débloque la fabrication des Flèches de chasse.","Débloque la fabrication des Flèches de chasse.")],
    },
    "MedicChem": {
        "items": ['''    <item name="dhsThrownFirebomb">
      <property name="Extends" value="thrownAmmoMolotovCocktail"/>
      <property name="CustomIcon" value="thrownAmmoMolotovCocktail"/>
      <property name="CustomIconTint" value="ff6633"/>
      <property name="DescriptionKey" value="dhsThrownFirebombDesc"/>
      <effect_group name="dhsFirebomb" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".4" tags="perkDemolitionsExpert"/>
      </effect_group>
    </item>'''],
        "recipes": ['<recipe name="dhsThrownFirebomb" count="2" craft_area="chemistryStation" craft_time="10" tags="learnable,chemStationCrafting,perkDemolitionsExpert"><ingredient name="resourceGunPowder" count="3"/><ingredient name="resourceOil" count="2"/><ingredient name="drinkJarBoiledWater" count="1"/></recipe>'],
        "buffs": [],
        "loc": [("dhsThrownFirebomb","Cocktail incendiaire du chimiste","Cocktail incendiaire du chimiste"),
                ("dhsThrownFirebombDesc","Cocktail incendiaire renforcé à la chimie : bien plus dévastateur. Fabriqué uniquement par le Chimiste.","Cocktail incendiaire renforcé à la chimie : bien plus dévastateur. Fabriqué uniquement par le Chimiste.")],
        "sigperks": [unlock("SigBomb","Cocktails du chimiste","Cocktails du chimiste","ui_game_symbol_science","dhsThrownFirebomb",True,1,
                            "Débloque la fabrication des Cocktails incendiaires du chimiste.","Débloque la fabrication des Cocktails incendiaires du chimiste.")],
    },
    "MedicSurg": {
        "items": ['''    <item name="dhsMedSurgeryKit">
      <property name="Extends" value="medicalFirstAidKit"/>
      <property name="CustomIcon" value="medicalFirstAidKit"/>
      <property name="CustomIconTint" value="ff6688"/>
      <property name="DescriptionKey" value="dhsMedSurgeryKitDesc"/>
    </item>'''],
        "recipes": ['<recipe name="dhsMedSurgeryKit" count="1" craft_area="workbench" craft_time="20" tags="learnable,workbenchCrafting,craftingMedical"><ingredient name="medicalFirstAidBandage" count="1"/><ingredient name="medicalSplint" count="1"/><ingredient name="drinkJarBoiledWater" count="1"/></recipe>'],
        "buffs": [],
        "loc": [("dhsMedSurgeryKit","Trousse de chirurgie","Trousse de chirurgie"),
                ("dhsMedSurgeryKitDesc","Trousse de soins complète de qualité hospitalière. Fabriquée uniquement par le Chirurgien.","Trousse de soins complète de qualité hospitalière. Fabriquée uniquement par le Chirurgien.")],
        "sigperks": [unlock("SigKit","Bloc opératoire","Bloc opératoire","ui_game_symbol_medical","dhsMedSurgeryKit",True,1,
                            "Débloque la fabrication de la Trousse de chirurgie.","Débloque la fabrication de la Trousse de chirurgie.")],
    },
    "SurvHerb": {
        "items": ['''    <item name="dhsDrinkDecoction">
      <property name="Extends" value="drinkJarRedTea"/>
      <property name="CustomIcon" value="drinkJarRedTea"/>
      <property name="CustomIconTint" value="88dd88"/>
      <property name="DescriptionKey" value="dhsDrinkDecoctionDesc"/>
      <effect_group name="dhsDecoction" tiered="false">
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="dhsBuffHerbal"/>
      </effect_group>
    </item>'''],
        "recipes": ['<recipe name="dhsDrinkDecoction" count="2" craft_area="campfire" craft_tool="toolCookingPot" craft_time="15" tags="learnable,craftingMedical"><ingredient name="drinkJarBoiledWater" count="2"/><ingredient name="resourceYuccaFibers" count="3"/></recipe>'],
        "buffs": [_team_buff("dhsBuffHerbal","dhsBuffHerbalName","dhsBuffHerbalDesc","ui_game_symbol_healing_factor","136,221,136","3","-.10",".20")],
        "loc": [("dhsDrinkDecoction","Décoction d'herboriste","Décoction d'herboriste"),
                ("dhsDrinkDecoctionDesc","Tisane fortifiante : régule l'endurance et endurcit le corps. Préparée uniquement par l'Herboriste.","Tisane fortifiante : régule l'endurance et endurcit le corps. Préparée uniquement par l'Herboriste."),
                ("dhsBuffHerbalName","Décoction d'herboriste","Décoction d'herboriste"),
                ("dhsBuffHerbalDesc","Revigoré par une décoction : endurance et résistance améliorées.","Revigoré par une décoction : endurance et résistance améliorées.")],
        "sigperks": [unlock("SigBrew","Herboristerie","Herboristerie","ui_game_symbol_crops","dhsDrinkDecoction",True,1,
                            "Débloque la préparation de la Décoction d'herboriste.","Débloque la préparation de la Décoction d'herboriste.")],
    },
    "EngiMech": {
        "items": ['''    <item name="dhsAmmoTurretHV">
      <property name="Extends" value="ammoJunkTurretShell"/>
      <property name="CustomIcon" value="ammoJunkTurretShell"/>
      <property name="CustomIconTint" value="ffcc66"/>
      <property name="DescriptionKey" value="dhsAmmoTurretHVDesc"/>
      <effect_group name="dhsTurretHV" tiered="false">
        <passive_effect name="EntityDamage" operation="perc_add" value=".4" tags="perkTurrets"/>
      </effect_group>
    </item>'''],
        "recipes": ['<recipe name="dhsAmmoTurretHV" count="20" craft_area="workbench" craft_time="5" tags="learnable,workbenchCrafting,perkTurrets"><ingredient name="resourceGunPowder" count="6"/><ingredient name="resourceForgedIron" count="3"/></recipe>'],
        "buffs": [],
        "loc": [("dhsAmmoTurretHV","Munition de tourelle haute vélocité","Munition de tourelle haute vélocité"),
                ("dhsAmmoTurretHVDesc","Munition optimisée pour tourelles et drones : dégâts robotiques accrus. Fabriquée uniquement par le Mécanicien.","Munition optimisée pour tourelles et drones : dégâts robotiques accrus. Fabriquée uniquement par le Mécanicien.")],
        "sigperks": [unlock("SigTurret","Atelier robotique","Atelier robotique","ui_game_symbol_wrench","dhsAmmoTurretHV",True,1,
                            "Débloque la fabrication des Munitions de tourelle haute vélocité.","Débloque la fabrication des Munitions de tourelle haute vélocité.")],
    },
    "ScoutInfi": {
        "items": ['''    <item name="dhsDrugProwler">
      <property name="Extends" value="drugCovertCats"/>
      <property name="CustomIcon" value="drugCovertCats"/>
      <property name="CustomIconTint" value="aa88ff"/>
      <property name="DescriptionKey" value="dhsDrugProwlerDesc"/>
    </item>'''],
        "recipes": ['<recipe name="dhsDrugProwler" count="2" craft_area="campfire" craft_tool="toolCookingPot" craft_time="12" tags="learnable,perkBrawler"><ingredient name="resourceYuccaFibers" count="3"/><ingredient name="drinkJarBoiledWater" count="1"/></recipe>'],
        "buffs": [],
        "loc": [("dhsDrugProwler","Stimulant du rôdeur","Stimulant du rôdeur"),
                ("dhsDrugProwlerDesc","Stimulant maison qui aiguise la furtivité et les réflexes. Préparé uniquement par l'Infiltrateur.","Stimulant maison qui aiguise la furtivité et les réflexes. Préparé uniquement par l'Infiltrateur.")],
        "sigperks": [unlock("SigStim","Pharmacopée du rôdeur","Pharmacopée du rôdeur","ui_game_symbol_stealth","dhsDrugProwler",True,1,
                            "Débloque la préparation du Stimulant du rôdeur.","Débloque la préparation du Stimulant du rôdeur.")],
    },
    "EngiElec": {
        "items": ['''    <item name="dhsBatteryHD">
      <property name="Extends" value="carBattery"/>
      <property name="CustomIcon" value="carBattery"/>
      <property name="CustomIconTint" value="66e0ff"/>
      <property name="DescriptionKey" value="dhsBatteryHDDesc"/>
    </item>'''],
        "recipes": ['<recipe name="dhsBatteryHD" count="1" craft_area="workbench" craft_time="20" tags="learnable,workbenchCrafting,perkAdvancedEngineering"><ingredient name="resourceElectricParts" count="3"/><ingredient name="resourceForgedIron" count="3"/><ingredient name="resourceDuctTape" count="2"/></recipe>'],
        "buffs": [],
        "loc": [("dhsBatteryHD","Cellule d'énergie renforcée","Cellule d'énergie renforcée"),
                ("dhsBatteryHDDesc","Batterie haute capacité pour pièges et installations électriques. Fabriquée uniquement par l'Électricien.","Batterie haute capacité pour pièges et installations électriques. Fabriquée uniquement par l'Électricien.")],
        "sigperks": [unlock("SigCell","Génie électrique","Génie électrique","ui_game_symbol_electric_generator","dhsBatteryHD",True,1,
                            "Débloque la fabrication de la Cellule d'énergie renforcée.","Débloque la fabrication de la Cellule d'énergie renforcée.")],
    },
    "BuilArti": {
        "items": ['''    <item name="dhsRepairKitPro">
      <property name="Extends" value="resourceRepairKit"/>
      <property name="CustomIcon" value="resourceRepairKit"/>
      <property name="CustomIconTint" value="ffdd66"/>
      <property name="DescriptionKey" value="dhsRepairKitProDesc"/>
    </item>'''],
        "recipes": ['<recipe name="dhsRepairKitPro" count="2" craft_area="workbench" craft_time="10" tags="learnable,workbenchCrafting,craftingHarvestingTools"><ingredient name="resourceForgedIron" count="3"/><ingredient name="resourceMechanicalParts" count="2"/><ingredient name="resourceDuctTape" count="1"/></recipe>'],
        "buffs": [],
        "loc": [("dhsRepairKitPro","Trousse de réparation pro","Trousse de réparation pro"),
                ("dhsRepairKitProDesc","Trousse d'artisan complète, idéale pour entretenir armes, outils et véhicules. Fabriquée uniquement par l'Artisan.","Trousse d'artisan complète, idéale pour entretenir armes, outils et véhicules. Fabriquée uniquement par l'Artisan.")],
        "sigperks": [unlock("SigKit","Atelier d'artisan","Atelier d'artisan","ui_game_symbol_workbench","dhsRepairKitPro",True,1,
                            "Débloque la fabrication de la Trousse de réparation pro.","Débloque la fabrication de la Trousse de réparation pro.")],
    },
}

def craft(code): return CRAFTABLES.get(code)

# ============================================================================
# Déblocages PER-RECETTE (1 point, gatés par niveau) — défini après CRAFTABLES.
# ============================================================================
# Noms FR des items : vanilla d'abord, puis nos items signature (CRAFTABLES), sinon la clé brute.
DHS_FR = {}
for _cr in CRAFTABLES.values():
    for k, _e, f in _cr.get("loc", []):
        DHS_FR.setdefault(k, f)
# Quelques items sans entrée FR dans Localization.txt (loc dans un autre fichier) -> override.
NAME_FR_OVERRIDE = {
    "drinkJarHoneyTea": "Thé au miel",
    "foodHoneyBrisket": "Poitrine de bœuf au miel",
    "foodHoneyGlazedSham": "Sham glacé au miel",
}
def name_fr(recipe):
    return NAME_FR_OVERRIDE.get(recipe) or VANILLA_FR.get(recipe) or DHS_FR.get(recipe) or recipe

def _sig_recipe_names(cr):
    out = []
    for r in cr.get("recipes", []):
        m = re.search(r'name="([^"]+)"', r)
        if m: out.append(m.group(1))
    return out

def collect_unlocks():
    """Construit les déblocages PER-RECETTE (1 point, gatés par niveau) par code de classe,
    regroupés en sous-branches. Sources : crafting_skills vanilla (armes/outils/armures/domaines),
    munitions & mods (répartition manuelle J1.21), matériaux de base, crafts signature."""
    out = {}  # code -> {bsuf: [bfr, bicon, [(recipe, palier), ...]]}
    seen = set()
    def add(code, recipe, lvl):
        if (code, recipe) in seen:  # une recette ne se débloque qu'une fois par classe
            return
        seen.add((code, recipe))
        bsuf, bfr, bicon = unlock_bucket(code, recipe)
        d = out.setdefault(code, {})
        d.setdefault(bsuf, [bfr, bicon, []])[2].append((recipe, lvl))
    # 1) Crafts qui se débloquaient par niveau/livres dans l'Artisanat vanilla.
    for skill, lst in CRAFT_UNLOCKS.items():
        for recipe, cl in lst:
            if recipe.endswith("Master"):
                continue  # tag de catégorie d'armure (pas une vraie recette) -> ignoré
            add(route_recipe(recipe, skill), recipe, palier_from_craftlevel(cl))
    # 2) Munitions spécialisées (réparties manuellement) + munitions de base -> Survivant.
    for code, lst in AMMO_BY_CODE.items():
        for r in lst: add(code, r, ammo_palier(r))
    for r in SURV_AMMO_BASIC: add("Common", r, 1)
    # 3) Mods (répartis manuellement).
    for code, lst in MODS_BY_CODE.items():
        for r in lst: add(code, r, 24)
    # 4) Matériaux/intermédiaires de base -> Survivant.
    for r in SURV_RESOURCES: add("Common", r, 1)
    # 5) Crafts signature exclusifs (items dhs*) -> leur classe, dès le niveau 1 (identité).
    for code, cr in CRAFTABLES.items():
        for r in _sig_recipe_names(cr): add(code, r, 1)
    return out
UNLOCKS = collect_unlocks()

# Ordre d'affichage des sous-branches de déblocage.
_BUCKET_ORDER = ["BArme","BArmure","BAtelier","BCuisine","BMuns","BMat","FArme","FEquip","FMuns","FFab"]

def unlock_subbranches(code):
    """Sous-branches de déblocage (per-recette) d'un code, prêtes à rendre."""
    coll = UNLOCKS.get(code, {})
    out = []
    for bsuf in _BUCKET_ORDER:
        if bsuf not in coll: continue
        bfr, bicon, items = coll[bsuf]
        perks = []
        for recipe, lvl in items:
            suf = "U" + re.sub(r'[^A-Za-z0-9]', '', recipe)
            fr = name_fr(recipe)
            perks.append(unlock(suf, fr, fr, bicon, recipe, False, lvl,
                                f"Débloque la fabrication : {fr}.", f"Débloque la fabrication : {fr}."))
        out.append((bsuf, bfr, bfr, bicon, perks))
    return out

def stat_subbranches(code):
    """Sous-branches de STATS (Arme/Métier/Spécialité, ou Survie pour Survivant)."""
    if code == "Common":
        return [("Survie", "Survie", "Survie", "ui_game_symbol_character", SURVIVOR_STATS)]
    return list(SUBCLASS_DEF[code]) if code in SUBCLASS_DEF else build_domain_subbranches(code)

def subbranches_for(code):
    """Toutes les sous-branches d'un code : stats puis déblocages per-recette."""
    return stat_subbranches(code) + unlock_subbranches(code)

def auto_unlock_perks(code):
    return []  # plus aucun déblocage automatique : tout s'achète par point, gaté par niveau.

# ---------- progression.xml ----------
def _palier(i):
    return LVL[i] if i < len(LVL) else LVL[-1]

# --- Détail des stats par niveau (rempli dans le grand cadre de l'UI via long_desc) ---
def _interp(v1, vmax, i, n):
    """Valeur d'un passive_effect 'level=1,n value=v1,vmax' au rang i (interpolation linéaire,
    comme le moteur)."""
    a, b = float(v1), float(vmax)
    return a if n <= 1 else a + (b - a) * (i - 1) / (n - 1)

def _fmt(op, x):
    """Formate une valeur d'effet pour l'affichage FR (pourcentage ou points)."""
    if op == "perc_add":
        return f"{x*100:+.0f} %"
    if op == "perc_subtract":   # valeur stockée positive = réduction
        return f"{-x*100:+.0f} %"
    # base_add / base_set / base_subtract : fraction (<1) = %, sinon points entiers
    if x != 0 and abs(x) < 1.0:
        return f"{x*100:+.0f} %"
    return f"{x:+.0f}"

def rank_rows(code, p):
    """Lignes de localisation pour le détail par niveau d'un perk (titre + texte long avec la
    valeur calculée), affichées dans le cadre sous la description."""
    base = f"dhsPerk{code}{p['suf']}"
    rows = []
    if p["k"] == "stat":
        n = p["n"]
        for i in range(1, n + 1):
            s = _fmt(p["op"], _interp(p["v1"], p["vmax"], i, n))
            longtxt = f"Niveau {i} : {s}. {p['fd']}"
            rows.append((f"{base}R{i}", p["fr"], p["fr"]))
            rows.append((f"{base}R{i}Long", longtxt, longtxt))
    else:
        rows.append((f"{base}R1", p["fr"], p["fr"]))
        rows.append((f"{base}R1Long", p["fd"], p["fd"]))
    return rows

def _perk_xml(L, code, skill, p, gated=True):
    """Émet un <perk>. gated=True -> requiert la classe (CVarCompare). On ajoute des
    <effect_description> (réutilisant la clé Desc FR) pour que l'UI affiche le texte FR
    par niveau au lieu du nom brut de l'effet (ex. 'HealthMax: 105')."""
    name = f"perkClass{code}{p['suf']}"
    dkey = f"dhsPerk{code}{p['suf']}Desc"
    nkey = f"dhsPerk{code}{p['suf']}Name"
    rbase = f"dhsPerk{code}{p['suf']}"
    def req(lvl, palier):
        g = f'<requirement name="CVarCompare" cvar="{cvar(code)}" operation="Equals" value="1" desc_key="dhsReqClass{code}"/>' if gated else ''
        return f'      <level_requirements level="{lvl}">{g}<requirement name="PlayerLevel" operation="GTE" value="{palier}" desc_key="dhsReqLvl{palier}"/></level_requirements>'
    if p["k"] == "stat":
        n = p["n"]
        L.append(f'    <perk name="{name}" parent="{skill}" name_key="{nkey}" desc_key="{dkey}" icon="{p["icon"]}" max_level="{n}">')
        for i in range(n):
            L.append(req(i+1, _palier(i)))
        tagattr = f' tags="{p["tags"]}"' if p["tags"] else ''
        L.append('      <effect_group>')
        L.append(f'        <passive_effect name="{p["eff"]}" operation="{p["op"]}" level="1,{n}" value="{p["v1"]},{p["vmax"]}"{tagattr}/>')
        # desc_key = titre du rang ; long_desc_key = détail avec la valeur calculée (cadre UI).
        for i in range(n):
            L.append(f'        <effect_description level="{i+1}" desc_key="{rbase}R{i+1}" long_desc_key="{rbase}R{i+1}Long"/>')
        L.append('      </effect_group>')
        L.append('    </perk>')
    else:  # unlock
        cost = '0' if p["auto"] else '1'
        L.append(f'    <perk name="{name}" parent="{skill}" name_key="{nkey}" desc_key="{dkey}" icon="{p["icon"]}" max_level="1" base_skill_point_cost="{cost}">')
        L.append(req(1, p["palier"]))
        L.append('      <effect_group>')
        L.append(f'        <passive_effect name="RecipeTagUnlocked" operation="base_set" level="1" value="1" tags="{p["recipes"]}"/>')
        L.append(f'        <effect_description level="1" desc_key="{rbase}R1" long_desc_key="{rbase}R1Long"/>')
        L.append('      </effect_group>')
        L.append('    </perk>')

def gen_progression():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — ne pas editer a la main. -->',
         '<configs>',
         '  <!-- Verrouillage strict : on coupe le déblocage de recettes par les compétences',
         '       d\'artisanat vanilla (magazines). Seuls NOS perks de classe débloquent les recettes',
         '       (RecipeTagUnlocked par nom). Toutes les recettes vanilla concernées sont routées',
         '       vers une classe (cf validate()). Les recettes verrouillées restent VISIBLES (grisées). -->',
         '  <remove xpath="/progression/crafting_skills/crafting_skill/effect_group/passive_effect[@name=\'RecipeTagUnlocked\']"/>',
         '  <append xpath="/progression/attributes">']
    # NB: <effect_group/> obligatoire, sinon ProgressionClass.Effects == null et l'UI
    # (windowSkillAttributeInfo, binding "detailsdescription") plante en NullReference.
    L.append('    <attribute name="attClassCommon" name_key="dhsAttClassCommonName" desc_key="dhsAttClassCommonDesc" icon="ui_game_symbol_modded" min_level="0" max_level="0" base_skill_point_cost="0"><effect_group/></attribute>')
    for bk,_en,_fr,icon,_subs in BRANCHES:
        a = attr_of_branch(bk)
        L.append(f'    <attribute name="{a}" name_key="dhs{a}Name" desc_key="dhs{a}Desc" icon="{icon}" min_level="0" max_level="0" base_skill_point_cost="0"><effect_group/></attribute>')
    L.append('  </append>')
    # Skills : une sous-branche (skill) par sous-branche de Survivant + de chaque sous-classe.
    L.append('  <append xpath="/progression/skills">')
    for sk,_ben,_bfr,bicon,_perks in subbranches_for("Common"):
        L.append(f'    <skill name="skillClassCommon{sk}" parent="attClassCommon" name_key="dhsSkillClassCommon{sk}Name" desc_key="dhsSkillClassCommon{sk}Desc" icon="{bicon}"><effect_group/></skill>')
    for code,_sen,_sfr,_tag,_kind,_fid,_sicon,_efl,_ffl in SUBS:
        a = attr_of_branch(CODE2BRANCH[code])
        for sk,_ben,_bfr,bicon,_perks in subbranches_for(code):
            L.append(f'    <skill name="skillClass{code}{sk}" parent="{a}" name_key="dhsSkillClass{code}{sk}Name" desc_key="dhsSkillClass{code}{sk}Desc" icon="{bicon}"><effect_group/></skill>')
    L.append('  </append>')
    # Perks
    L.append('  <append xpath="/progression/perks">')
    # Survivant (commun, pour TOUS) : stats vitales + déblocages de base (per-recette). Non gaté.
    for sk,_ben,_bfr,_bicon,perks in subbranches_for("Common"):
        skill = f"skillClassCommon{sk}"
        for p in perks:
            _perk_xml(L, "Common", skill, p, gated=False)
    for code,_sen,_sfr,_tag,_kind,_fid,_sicon,_efl,_ffl in SUBS:
        for sk,_ben,_bfr,_bicon,perks in subbranches_for(code):
            skill = f"skillClass{code}{sk}"
            for p in perks:
                _perk_xml(L, code, skill, p)
    L.append('  </append>')
    L.append('</configs>')
    return "\n".join(L)+"\n"

# ---------- items.xml ----------
def gen_items():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — ne pas editer a la main. -->',
         '<configs>', '  <append xpath="/items">']
    for code,_sen,_sfr,_tag,_kind,fid,_sicon,_efl,_ffl in SUBS:
        autos = auto_unlock_perks(code)
        # ----- Livre de classe (choix de classe) -----
        L.append(f'    <item name="dhsBookClass{code}">')
        L.append('      <property name="Extends" value="schematicMaster"/>')
        L.append('      <property name="CustomIcon" value="schematicMaster"/>')
        L.append('      <property name="CustomIconTint" value="6699ff"/>')
        L.append('      <property name="Stacknumber" value="1"/>')
        L.append(f'      <property name="DescriptionKey" value="dhsBookClass{code}Desc"/>')
        L.append('      <effect_group tiered="false">')
        L.append('        <requirement name="CVarCompare" cvar="dhsClassSlotFree" operation="Equals" value="1"/>')
        L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="{cvar(code)}" operation="set" value="1"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="dhsClassSlotFree" operation="set" value="0"/>')
        L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="dhsClassActiveForeign" operation="set" value="{fid}"/>')
        L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="{ptsvar(code)}" operation="add" value="3"/>')
        for ap in autos:
            L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddProgressionLevel" progression_name="{ap}" level="1"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="GiveExp" exp="50"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="DeadHotSummer.MinEventActionDhsClassEvent, DeadHotSummer"/>')
        L.append('      </effect_group>')
        L.append('    </item>')
        # ----- Magazine de classe (+1 point de classe) -----
        L.append(f'    <item name="dhsMag{code}">')
        L.append('      <property name="Extends" value="schematicMaster"/>')
        L.append('      <property name="CustomIcon" value="schematicMaster"/>')
        L.append('      <property name="CustomIconTint" value="88cc88"/>')
        L.append('      <property name="Stacknumber" value="20"/>')
        L.append('      <property name="EconomicValue" value="120"/>')
        L.append(f'      <property name="DescriptionKey" value="dhsMag{code}Desc"/>')
        L.append('      <property name="Group" value="Books,BooksOnly,TCReading"/>')
        L.append(f'      <property name="Tags" value="dhsCsm{code},csm"/>')
        L.append('      <effect_group tiered="false">')
        L.append(f'        <requirement name="CVarCompare" cvar="{cvar(code)}" operation="Equals" value="1"/>')
        L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="{ptsvar(code)}" operation="add" value="1"/>')
        for ap in autos:  # la sœur (débloquée par complétion, sans livre) obtient le craft signature
            L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddProgressionLevel" progression_name="{ap}" level="1"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="GiveExp" exp="50"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="DeadHotSummer.MinEventActionDhsClassEvent, DeadHotSummer"/>')
        L.append('      </effect_group>')
        L.append('    </item>')
    # ----- Items craftables signature -----
    for code in [c for c,_e,_f,_t,_k,_fi,_i,_ef,_ff in SUBS]:
        cr = craft(code)
        if not cr: continue
        for it in cr["items"]:
            L.append(it)
    L += ['  </append>', '</configs>']
    return "\n".join(L)+"\n"

# ---------- recipes.xml ----------
def gen_recipes():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — recettes signature de classe. -->',
         '<configs>', '  <append xpath="/recipes">']
    for code in [c for c,_e,_f,_t,_k,_fi,_i,_ef,_ff in SUBS]:
        cr = craft(code)
        if not cr: continue
        for r in cr["recipes"]:
            L.append("    " + r)
    L += ['  </append>', '</configs>']
    return "\n".join(L)+"\n"

# ---------- buffs.xml ----------
def gen_buffs():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — buffs signature de classe. -->',
         '<configs>', '  <append xpath="/buffs">']
    for code in [c for c,_e,_f,_t,_k,_fi,_i,_ef,_ff in SUBS]:
        cr = craft(code)
        if not cr: continue
        for b in cr["buffs"]:
            L.append(b)
    L += ['  </append>', '</configs>']
    return "\n".join(L)+"\n"

# ---------- loot.xml ----------
def gen_loot():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — ne pas editer a la main. -->',
         '<configs>',
         '  <append xpath="/lootcontainers/lootgroup[@name=\'perkBooks\']">']
    for code,_sen,_sfr,_tag,_kind,_fid,_sicon,_efl,_ffl in SUBS:
        L.append(f'    <item name="dhsMag{code}"><requirement class="CVar" cvar="{cvar(code)}" operation="EQ" value="1"/></item>')
    L += ['  </append>', '</configs>']
    return "\n".join(L)+"\n"

# ---------- Localization.csv ----------
def gen_loc():
    rows = [("Key","english","french")]
    rows.append(("attclasscommon","Survivor","Survivant"))
    for bk,en,fr,_ic,_subs in BRANCHES:
        rows.append((attr_of_branch(bk).lower(), en, fr))
    rows.append(("dhsAttClassCommonName","Survivor","Survivant"))
    rows.append(("dhsAttClassCommonDesc","Common skills for everyone","Compétences communes à tous"))
    rows.append(("dhsClassPointsLabel","Class points","Points de classe"))
    # Libellés FR des prérequis de niveau (sinon l'UI affiche « Player level GTE N » en anglais).
    for v in sorted(set(LVL) | set(PALIERS)):
        txt = "Aucun prérequis de niveau" if v <= 1 else f"Niveau {v} requis"
        rows.append((f"dhsReqLvl{v}", txt, txt))
    for bk,en,fr,_ic,_subs in BRANCHES:
        a = attr_of_branch(bk)
        rows.append((f"dhs{a}Name", en, fr))
        rows.append((f"dhs{a}Desc", f"{en} branch", f"Branche {fr}"))
    # Loc des sous-branches + perks de Survivant (stats + déblocages per-recette).
    for sk,ben,bfr,_bicon,perks in subbranches_for("Common"):
        rows.append((f"dhsSkillClassCommon{sk}Name", f"Survivor — {ben}", f"Survivant — {bfr}"))
        rows.append((f"dhsSkillClassCommon{sk}Desc", f"Survivor sub-branch: {ben}.", f"Sous-branche Survivant : {bfr}."))
        for p in perks:
            rows.append((f"dhsPerkCommon{p['suf']}Name", p["en"], p["fr"]))
            rows.append((f"dhsPerkCommon{p['suf']}Desc", p["ed"], p["fd"]))
            rows += rank_rows("Common", p)
    for code,en,fr,_tag,_kind,_fid,_sicon,efl,ffl in SUBS:
        rows.append((f"dhsReqClass{code}", f"Requires the {en} class", f"Nécessite la classe {fr}"))
        rows.append((f"dhsBookClass{code}", f"Class Manual: {en}", f"Manuel de classe : {fr}"))
        rows.append((f"dhsBookClass{code}Desc",
                     f"Become a {en}: master {efl}. Reading it picks the {en} class and grants a few class points to spend in its tree (perks and crafts unlock by level).",
                     f"Devenez {fr} : maîtrisez {ffl}. La lecture choisit la classe {fr} et octroie quelques points de classe à dépenser dans son arbre (perks et crafts se débloquent par niveau)."))
        rows.append((f"dhsMag{code}", f"{en} Manual", f"Manuel : {fr}"))
        rows.append((f"dhsMag{code}Desc",
                     f"A {en} magazine. Reading it grants 1 {en} class point to spend in the {en} tree. Useful only to members of this class.",
                     f"Un magazine de {fr}. Le lire octroie 1 point de classe {fr} à dépenser dans l'arbre {fr}. Utile uniquement à cette classe."))
        # sous-branches (skills) + perks
        for sk,ben,bfr,_bicon,perks in subbranches_for(code):
            rows.append((f"dhsSkillClass{code}{sk}Name", f"{en} — {ben}", f"{fr} — {bfr}"))
            rows.append((f"dhsSkillClass{code}{sk}Desc", f"{en} sub-branch: {ben}.", f"Sous-branche {fr} : {bfr}."))
            for p in perks:
                rows.append((f"dhsPerk{code}{p['suf']}Name", p["en"], p["fr"]))
                rows.append((f"dhsPerk{code}{p['suf']}Desc", p["ed"], p["fd"]))
                rows += rank_rows(code, p)
        # loc des craftables
        cr = craft(code)
        if cr:
            for (k,e,f) in cr["loc"]:
                rows.append((k, e, f))
    # L'utilisateur veut TOUT en français (client en anglais) -> on met le français dans les
    # DEUX colonnes (english+french) pour garantir l'affichage FR quelle que soit la langue.
    rows = [rows[0]] + [(k, f, f) for (k, _e, f) in rows[1:]]
    def esc(c):
        if any(ch in c for ch in (",", '"', "\n")):
            return '"' + c.replace('"', '""') + '"'
        return c
    out = [",".join(esc(c) for c in r) for r in rows]
    return "\n".join(out)+"\n"

def _perk_sig(p):
    """Signature d'unicité d'un perk : (effet, tags triés) pour une stat ; ('unlock', recettes)
    pour un déblocage (toujours distinct par recettes)."""
    if p["k"] == "unlock":
        return ("unlock", p["recipes"])
    return (p["eff"], tuple(sorted(t for t in p["tags"].split(",") if t)))

def validate():
    """Garantit les règles d'unicité demandées :
      1) aucun TYPE d'effet réservé à Survivant n'apparaît dans une sous-classe (zéro doublon
         général <-> sous-classe) ;
      2) au sein d'une sous-classe (Arme + Métier + Spécialité), aucun perk en double
         (même effet ET mêmes tags) -> chaque perk a un gameplay distinct.
    Lève AssertionError listant toutes les violations."""
    errors = []
    # 1) Stats : pas de doublon (effet,tags) intra-classe + types réservés disjoints.
    surv_sigs = {}
    for p in SURVIVOR_STATS:
        sig = _perk_sig(p)
        if sig in surv_sigs:
            errors.append(f"Survivant : doublon {sig} ({p['suf']} == {surv_sigs[sig]})")
        surv_sigs[sig] = p["suf"]
    for code, *_ in SUBS:
        seen = {}
        for sk, _en, _fr, _ic, perks in subbranches_for(code):
            for p in perks:
                if p["k"] != "stat":
                    continue
                if p["eff"] in RESERVED_SURVIVOR:
                    errors.append(f"{code}/{sk}/{p['suf']} : effet '{p['eff']}' réservé à Survivant")
                sig = _perk_sig(p)
                if sig in seen:
                    errors.append(f"{code} : doublon {sig} ({sk}/{p['suf']} == {seen[sig]})")
                seen[sig] = f"{sk}/{p['suf']}"
    # 2) Déblocages : un nom de perk unique partout, une recette débloquée une seule fois par classe.
    perk_names = {}
    for code in ["Common"] + [c for c, *_ in SUBS]:
        for sk, _en, _fr, _ic, perks in subbranches_for(code):
            for p in perks:
                nm = f"perkClass{code}{p['suf']}"
                if nm in perk_names:
                    errors.append(f"nom de perk dupliqué : {nm}")
                perk_names[nm] = code
    # 3) Toutes les recettes craftées par niveau dans l'Artisanat vanilla sont bien routées.
    routed = {r for d in UNLOCKS.values() for b in d.values() for r, _l in b[2]}
    craft_recipes = {r for lst in CRAFT_UNLOCKS.values() for r, _l in lst if not r.endswith("Master")}
    missing = craft_recipes - routed
    if missing:
        errors.append(f"{len(missing)} recettes vanilla non routées (ex: {sorted(missing)[:5]})")
    if errors:
        raise AssertionError("Violations de génération :\n  - " + "\n  - ".join(errors))
    n_unlocks = len(routed)
    print(f"validate(): OK — {len(SUBS)} sous-classes + Survivant, {len(perk_names)} perks, "
          f"{n_unlocks} recettes débloquables réparties, aucun doublon")

def main():
    validate()
    files = {
        "progression.xml": gen_progression(),
        "items.xml": gen_items(),
        "recipes.xml": gen_recipes(),
        "buffs.xml": gen_buffs(),
        "loot.xml": gen_loot(),
        "Localization.csv": gen_loc(),
    }
    for name, content in files.items():
        with open(os.path.join(CFG, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"écrit {name} ({len(content.splitlines())} lignes)")
    old = os.path.join(CFG, "Localization.txt")
    if os.path.exists(old):
        os.remove(old); print("supprimé Localization.txt (obsolète)")

if __name__ == "__main__":
    main()

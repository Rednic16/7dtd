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
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "Mods", "DeadHotSummer", "Config")

LVL = [1, 12, 24, 36, 48]  # paliers PlayerLevel par rang

# Template de perks par "kind" (utilisé pour les 12 sous-classes pas encore détaillées).
# (suffixe, EN, FR, effet, op, v1, v5, scoped_au_tag, EN desc, FR desc)
PERKS = {
    "gun": [
        ("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases your class weapon damage.","Augmente les dégâts de l'arme de classe."),
        ("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves weapon handling.","Améliore la maniabilité."),
        ("Reload","Fast Reload","Rechargement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Reloads faster.","Recharge plus vite."),
        ("Aim","Precision","Précision","SpreadMultiplierAiming","perc_add","-.06","-.30",True,"Reduces aimed spread.","Réduit la dispersion en visée."),
    ],
    "bow": [
        ("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases bow/crossbow damage.","Augmente les dégâts arc/arbalète."),
        ("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves handling.","Améliore la maniabilité."),
        ("Draw","Quick Draw","Armement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Nocks faster.","Encoche plus vite."),
        ("Velo","Power Shot","Tir puissant","ProjectileVelocity","perc_add",".10",".50",True,"Increases projectile velocity.","Augmente la vitesse des projectiles."),
    ],
    "melee": [
        ("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases melee damage.","Augmente les dégâts de mêlée."),
        ("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves handling.","Améliore la maniabilité."),
        ("Dismember","Brutality","Brutalité","DismemberChance","base_add",".05",".25",True,"Increases dismemberment.","Augmente le démembrement."),
        ("Stam","Conditioning","Conditionnement","StaminaLoss","perc_add","-.06","-.30",False,"Reduces stamina spent.","Réduit l'endurance dépensée."),
    ],
    "thrown": [
        ("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases thrown damage.","Augmente les dégâts de jet."),
        ("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves handling.","Améliore la maniabilité."),
        ("Velo","Strong Arm","Bon bras","ProjectileVelocity","perc_add",".10",".50",True,"Throws farther.","Lance plus loin."),
    ],
    "robotics": [
        ("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases robotics damage.","Augmente les dégâts robotiques."),
        ("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves handling.","Améliore la maniabilité."),
        ("Reload","Maintenance","Maintenance","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Services faster.","Entretient plus vite."),
    ],
    "tools": [
        ("Harvest","Harvesting","Récolte","HarvestCount","perc_add",".10",".50",True,"Harvests more with tools.","Récolte plus avec les outils."),
        ("Block","Power Tools","Outils puissants","BlockDamage","perc_add",".10",".50",True,"Increases block damage.","Augmente les dégâts aux blocs."),
        ("Stam","Conditioning","Conditionnement","StaminaLoss","perc_add","-.06","-.30",False,"Reduces stamina spent.","Réduit l'endurance dépensée."),
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
def stat(suf, en, fr, eff, op, v1, vmax, nlev, tags, ed, fd, icon="ui_game_symbol_skill_points"):
    return {"k":"stat","suf":suf,"en":en,"fr":fr,"eff":eff,"op":op,"v1":v1,"vmax":vmax,
            "n":nlev,"tags":tags,"ed":ed,"fd":fd,"icon":icon}
def unlock(suf, en, fr, icon, recipes, auto, palier, ed, fd):
    return {"k":"unlock","suf":suf,"en":en,"fr":fr,"icon":icon,"recipes":recipes,
            "auto":auto,"palier":palier,"ed":ed,"fd":fd}

# ---- FERMIER : Agriculteur (cultures + fusil à pompe) ----
FARM_AGRI = [
    ("Shotgun","Pump Shotgun","Fusil à pompe","ui_game_symbol_shotgun", [
        stat("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",5,"perkBoomstick",
             "Increases pump shotgun damage.","Augmente les dégâts au fusil à pompe.","ui_game_symbol_shotgun"),
        stat("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",5,"perkBoomstick",
             "Improves shotgun handling.","Améliore la maniabilité du fusil à pompe.","ui_game_symbol_shotgun"),
        stat("Reload","Fast Reload","Rechargement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",5,"perkBoomstick",
             "Reloads the shotgun faster.","Recharge le fusil plus vite.","ui_game_symbol_shotgun"),
        stat("Aim","Choke","Précision","SpreadMultiplierAiming","perc_add","-.06","-.30",5,"perkBoomstick",
             "Tightens aimed shot spread.","Resserre la gerbe en visée.","ui_game_symbol_shotgun"),
        stat("Pierce","Slugger","Perforation","TargetArmor","perc_add","-.06","-.30",5,"perkBoomstick",
             "Shotgun shots ignore more armor.","Les tirs ignorent davantage l'armure.","ui_game_symbol_shotgun"),
        unlock("Slug","Farmer's Arsenal","Arsenal du fermier","ui_game_symbol_shotgun","dhsAmmoFarmerSlug",True,1,
               "Unlocks crafting Farmer Slugs (heavy slugs) at a workbench.",
               "Débloque la fabrication de Cartouches de fermier (balles lourdes) à l'établi."),
        unlock("Buck","Field Loads","Cartouchière","ui_game_symbol_shotgun","dhsAmmoFarmerBuck",False,12,
               "Unlocks crafting Farmer Buckshot (heavy buckshot) at a workbench.",
               "Débloque la fabrication de Chevrotine de fermier (chevrotine lourde) à l'établi."),
    ]),
    ("Farming","Farming","Agriculture","ui_game_symbol_crops", [
        stat("Green","Green Thumb","Main verte","HarvestCount","perc_add",".15",".75",5,"cropHarvest,wildCropsHarvest",
             "Harvest much more from crops and wild plants.","Récolte bien plus sur cultures et plantes sauvages.","ui_game_symbol_crops"),
        stat("Butcher","Homesteader","Éleveur","HarvestCount","perc_add",".10",".50",5,"butcherHarvest",
             "Harvest more meat and resources from animals.","Récolte plus de viande/ressources sur les animaux.","ui_game_symbol_meat"),
        stat("FastCraft","Farmhand","Tâcheron","CraftingTime","perc_add","-.10","-.50",5,"dhsCraftFarmAgri",
             "Crafts your Farmer recipes faster.","Fabrique vos recettes d'Agriculteur plus vite.","ui_game_symbol_crafting"),
        unlock("Preserve","Cannery","Conserverie","ui_game_symbol_fork","dhsFoodPreserves",False,24,
               "Unlocks cooking Farmer's Preserves (long-lasting filling food).",
               "Débloque la cuisson des Conserves du fermier (nourriture copieuse qui se garde)."),
        stat("Belly","Big Eater","Estomac solide","FoodMax","base_add","5","25",5,"",
             "Increases your maximum food.","Augmente votre nourriture maximale.","ui_game_symbol_food"),
        stat("XP","Early Riser","Lève-tôt","PlayerExpGain","perc_add",".02",".10",5,"",
             "Increases all experience gained.","Augmente toute l'expérience gagnée.","ui_game_symbol_xp"),
        stat("StamRegen","Field Stamina","Souffle paysan","StaminaChangeOT","perc_add",".05",".25",5,"",
             "Recovers stamina faster.","Récupère l'endurance plus vite.","ui_game_symbol_stamina"),
    ]),
    ("Provider","Provider","Subsistance","ui_game_symbol_campfire", [
        stat("Stam","Hardy","Endurance paysanne","StaminaLoss","perc_add","-.06","-.30",5,"",
             "Reduces stamina spent on actions.","Réduit l'endurance dépensée par les actions.","ui_game_symbol_stamina"),
        stat("Carry","Pack Mule","Bête de somme","CarryCapacity","base_add","1","3",3,"",
             "Adds carry capacity slots.","Ajoute des emplacements de portage.","ui_game_symbol_backpack"),
        stat("Tough","Weathered","Coriace","PhysicalDamageResist","base_add","1","5",5,"",
             "Reduces physical damage taken.","Réduit les dégâts physiques subis.","ui_game_symbol_armor_iron"),
        stat("Resist","Sturdy","Constitution","GeneralDamageResist","base_add","1","3",3,"",
             "Reduces all damage taken slightly.","Réduit légèrement tous les dégâts subis.","ui_game_symbol_armor_iron"),
        stat("HP","Strong Back","Robuste","HealthMax","base_add","5","25",5,"",
             "Increases your maximum health.","Augmente votre santé maximale.","ui_game_symbol_health"),
        stat("Buff","Iron Gut","Estomac d'acier","BuffResistance","base_add","1","3",3,"",
             "Resists negative status effects.","Résiste aux effets négatifs.","ui_game_symbol_buff"),
    ]),
]

# ---- FERMIER : Cuisinier (cuisine + gourdins + soutien d'équipe) ----
FARM_COOK = [
    ("Club","Club","Gourdin","ui_game_symbol_hammer", [
        stat("Dmg","Damage","Dégâts","EntityDamage","perc_add",".08",".40",5,"perkPummelPete",
             "Increases club damage.","Augmente les dégâts au gourdin.","ui_game_symbol_hammer"),
        stat("Hand","Handling","Maniement","WeaponHandling","perc_add",".10",".50",5,"perkPummelPete",
             "Improves club handling.","Améliore la maniabilité du gourdin.","ui_game_symbol_hammer"),
        stat("Dismember","Tenderizer","Attendrisseur","DismemberChance","base_add",".05",".25",5,"perkPummelPete",
             "Increases dismemberment with clubs.","Augmente le démembrement au gourdin.","ui_game_symbol_hammer"),
        stat("Stam","Conditioning","Conditionnement","StaminaLoss","perc_add","-.06","-.30",5,"perkPummelPete",
             "Reduces stamina spent attacking.","Réduit l'endurance dépensée en attaquant.","ui_game_symbol_stamina"),
        stat("Block","Meat Mallet","Massue","BlockDamage","perc_add",".10",".50",5,"perkPummelPete",
             "Increases block damage with clubs.","Augmente les dégâts aux blocs au gourdin.","ui_game_symbol_hammer"),
        stat("Armor","Bonecrusher","Broyeur d'armure","TargetArmor","perc_add","-.06","-.30",5,"perkPummelPete",
             "Club hits ignore more armor.","Les coups ignorent davantage l'armure.","ui_game_symbol_hammer"),
    ]),
    ("Kitchen","Kitchen","Cuisine","ui_game_symbol_fork", [
        stat("FastCook","Sous-Chef","Marmiton","CraftingTime","perc_add","-.10","-.50",5,"dhsCraftFarmCook",
             "Cooks your Cook recipes faster.","Cuisine vos recettes de Cuisinier plus vite.","ui_game_symbol_fork"),
        stat("Gourmet","Gourmet","Gourmet","FoodMax","base_add","5","25",5,"",
             "Increases your maximum food.","Augmente votre nourriture maximale.","ui_game_symbol_food"),
        unlock("Feast","Cook's Kitchen","Cuisine du chef","ui_game_symbol_fork","dhsFoodFeast",True,1,
               "Unlocks cooking the Team Feast: a shared meal that buffs nearby allies.",
               "Débloque la cuisson du Festin d'équipe : un plat qui buff les alliés proches."),
        unlock("Tonic","Mixology","Mixologie","ui_game_symbol_fork","dhsDrinkTonic",False,12,
               "Unlocks brewing the Cook's Tonic: a shared stamina drink.",
               "Débloque la préparation du Tonique du chef : une boisson d'endurance partagée."),
        unlock("Grand","Grand Chef","Grand chef","ui_game_symbol_fork","dhsFoodFeastGrand",False,36,
               "Unlocks cooking the Grand Feast: a stronger team meal.",
               "Débloque la cuisson du Grand festin : un repas d'équipe renforcé."),
        stat("Butcher","Butcher","Boucher","HarvestCount","perc_add",".10",".50",5,"butcherHarvest",
             "Harvest more meat from animals.","Récolte plus de viande sur les animaux.","ui_game_symbol_meat"),
        stat("XP","Quick Learner","Apprenti rapide","PlayerExpGain","perc_add",".02",".10",5,"",
             "Increases all experience gained.","Augmente toute l'expérience gagnée.","ui_game_symbol_xp"),
    ]),
    ("Support","Support","Soutien d'équipe","ui_game_symbol_medical", [
        stat("Tough","Hearty","Robustesse","PhysicalDamageResist","base_add","1","5",5,"",
             "Reduces physical damage taken.","Réduit les dégâts physiques subis.","ui_game_symbol_armor_iron"),
        stat("Resist","Bulwark","Garde","GeneralDamageResist","base_add","1","3",3,"",
             "Reduces all damage taken slightly.","Réduit légèrement tous les dégâts subis.","ui_game_symbol_armor_iron"),
        stat("HP","Big Boned","Solide gaillard","HealthMax","base_add","5","25",5,"",
             "Increases your maximum health.","Augmente votre santé maximale.","ui_game_symbol_health"),
        stat("Carry","Porter","Porteur","CarryCapacity","base_add","1","3",3,"",
             "Adds carry capacity slots.","Ajoute des emplacements de portage.","ui_game_symbol_backpack"),
        stat("StamRegen","Second Wind","Second souffle","StaminaChangeOT","perc_add",".05",".25",5,"",
             "Recovers stamina faster.","Récupère l'endurance plus vite.","ui_game_symbol_stamina"),
        stat("Buff","Cast Iron","Estomac d'acier","BuffResistance","base_add","1","3",3,"",
             "Resists negative status effects.","Résiste aux effets négatifs.","ui_game_symbol_buff"),
        stat("Meneur","Quartermaster","Intendant","PlayerExpGain","perc_add",".02",".10",5,"",
             "Increases all experience gained.","Augmente toute l'expérience gagnée.","ui_game_symbol_xp"),
    ]),
]

SUBCLASS_DEF = {"FarmAgri": FARM_AGRI, "FarmCook": FARM_COOK}

def subbranches_for(code):
    """Sous-branches d'une sous-classe : détaillées si définies, sinon template (1 sous-branche)."""
    if code in SUBCLASS_DEF:
        return SUBCLASS_DEF[code]
    c,en,fr,tag,kind,fid,icon,efl,ffl = SUB_BY_CODE[code]
    perks = []
    for (suf,pen,pfr,nm,op,v1,v5,scoped,ed,fd) in PERKS[kind]:
        perks.append(stat(suf,pen,pfr,nm,op,v1,v5,5, tag if scoped else "", ed, fd, icon))
    return [("Spec", en, fr, icon, perks)]

def auto_unlock_perks(code):
    out = []
    for _sk,_en,_fr,_ic,perks in subbranches_for(code):
        for p in perks:
            if p["k"] == "unlock" and p["auto"]:
                out.append(f"perkClass{code}{p['suf']}")
    return out

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
            _team_buff("dhsBuffTonic","dhsBuffTonicName","dhsBuffTonicDesc","ui_game_symbol_stamina","255,170,85","2","-.15",".35"),
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
}

def craft(code): return CRAFTABLES.get(code)

# ---------- progression.xml ----------
def _palier(i):
    return LVL[i] if i < len(LVL) else LVL[-1]

def _perk_xml(L, code, skill, p):
    name = f"perkClass{code}{p['suf']}"
    if p["k"] == "stat":
        L.append(f'    <perk name="{name}" parent="{skill}" name_key="dhsPerk{code}{p["suf"]}Name" desc_key="dhsPerk{code}{p["suf"]}Desc" icon="{p["icon"]}" max_level="{p["n"]}">')
        for i in range(p["n"]):
            L.append(f'      <level_requirements level="{i+1}"><requirement name="CVarCompare" cvar="{cvar(code)}" operation="Equals" value="1" desc_key="dhsReqClass{code}"/><requirement name="PlayerLevel" operation="GTE" value="{_palier(i)}"/></level_requirements>')
        tagattr = f' tags="{p["tags"]}"' if p["tags"] else ''
        L.append(f'      <effect_group><passive_effect name="{p["eff"]}" operation="{p["op"]}" level="1,{p["n"]}" value="{p["v1"]},{p["vmax"]}"{tagattr}/></effect_group>')
        L.append('    </perk>')
    else:  # unlock
        cost = '0' if p["auto"] else '1'
        L.append(f'    <perk name="{name}" parent="{skill}" name_key="dhsPerk{code}{p["suf"]}Name" desc_key="dhsPerk{code}{p["suf"]}Desc" icon="{p["icon"]}" max_level="1" base_skill_point_cost="{cost}">')
        L.append(f'      <level_requirements level="1"><requirement name="CVarCompare" cvar="{cvar(code)}" operation="Equals" value="1" desc_key="dhsReqClass{code}"/><requirement name="PlayerLevel" operation="GTE" value="{p["palier"]}"/></level_requirements>')
        L.append(f'      <effect_group><passive_effect name="RecipeTagUnlocked" operation="base_set" level="1" value="1" tags="{p["recipes"]}"/></effect_group>')
        L.append('    </perk>')

def gen_progression():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — ne pas editer a la main. -->',
         '<configs>',
         '  <append xpath="/progression/attributes">']
    L.append('    <attribute name="attClassCommon" name_key="dhsAttClassCommonName" desc_key="dhsAttClassCommonDesc" icon="ui_game_symbol_modded" min_level="0" max_level="0" base_skill_point_cost="0"/>')
    for bk,_en,_fr,icon,_subs in BRANCHES:
        a = attr_of_branch(bk)
        L.append(f'    <attribute name="{a}" name_key="dhs{a}Name" desc_key="dhs{a}Desc" icon="{icon}" min_level="0" max_level="0" base_skill_point_cost="0"/>')
    L.append('  </append>')
    # Skills : Survivant + une sous-branche (skill) par sous-branche de chaque sous-classe.
    L.append('  <append xpath="/progression/skills">')
    L.append('    <skill name="skillClassCommon" parent="attClassCommon" name_key="dhsSkillClassCommonName" desc_key="dhsSkillClassCommonDesc" icon="ui_game_symbol_modded"><effect_group/></skill>')
    for code,_sen,_sfr,_tag,_kind,_fid,_sicon,_efl,_ffl in SUBS:
        a = attr_of_branch(CODE2BRANCH[code])
        for sk,_ben,_bfr,bicon,_perks in subbranches_for(code):
            L.append(f'    <skill name="skillClass{code}{sk}" parent="{a}" name_key="dhsSkillClass{code}{sk}Name" desc_key="dhsSkillClass{code}{sk}Desc" icon="{bicon}"><effect_group/></skill>')
    L.append('  </append>')
    # Perks
    L.append('  <append xpath="/progression/perks">')
    base = [
        ("Toughness","ui_game_symbol_armor_iron","PhysicalDamageResist","base_add","2","10",None),
        ("Forager","ui_game_symbol_hand","HarvestCount","perc_add",".1",".5","butcherHarvest,wildCropsHarvest"),
        ("Endurance","ui_game_symbol_run","StaminaLoss","perc_add","-.05","-.25",None),
    ]
    for suf,icon,nm,op,v1,v5,tag in base:
        L.append(f'    <perk name="perkClassCommon{suf}" parent="skillClassCommon" name_key="dhsPerkCommon{suf}Name" desc_key="dhsPerkCommon{suf}Desc" icon="{icon}" max_level="5">')
        for i in range(5):
            L.append(f'      <level_requirements level="{i+1}"><requirement name="PlayerLevel" operation="GTE" value="{LVL[i]}"/></level_requirements>')
        tagattr = f' tags="{tag}"' if tag else ''
        L.append(f'      <effect_group><passive_effect name="{nm}" operation="{op}" level="1,5" value="{v1},{v5}"{tagattr}/></effect_group>')
        L.append('    </perk>')
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
    for bk,en,fr,_ic,_subs in BRANCHES:
        a = attr_of_branch(bk)
        rows.append((f"dhs{a}Name", en, fr))
        rows.append((f"dhs{a}Desc", f"{en} branch", f"Branche {fr}"))
    rows += [
        ("dhsSkillClassCommonName","Survivor","Survivant"),
        ("dhsSkillClassCommonDesc","Common skills available to everyone","Compétences communes à tous"),
        ("dhsPerkCommonToughnessName","Toughness","Robustesse"),
        ("dhsPerkCommonToughnessDesc","Reduces physical damage taken.","Réduit les dégâts physiques subis."),
        ("dhsPerkCommonForagerName","Forager","Cueilleur"),
        ("dhsPerkCommonForagerDesc","Harvest more from animals and wild plants.","Récolte plus sur les animaux et plantes sauvages."),
        ("dhsPerkCommonEnduranceName","Endurance","Endurance"),
        ("dhsPerkCommonEnduranceDesc","Reduces stamina loss from actions.","Réduit la perte d'endurance des actions."),
    ]
    for code,en,fr,_tag,_kind,_fid,_sicon,efl,ffl in SUBS:
        rows.append((f"dhsReqClass{code}", f"Requires the {en} class", f"Nécessite la classe {fr}"))
        rows.append((f"dhsBookClass{code}", f"Class Manual: {en}", f"Manuel de classe : {fr}"))
        rows.append((f"dhsBookClass{code}Desc",
                     f"Become a {en}: master {efl}. Reading it picks the {en} class, unlocks its signature craft and grants a few class points.",
                     f"Devenez {fr} : maîtrisez {ffl}. La lecture choisit la classe {fr}, débloque son craft signature et octroie quelques points de classe."))
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
        # loc des craftables
        cr = craft(code)
        if cr:
            for (k,e,f) in cr["loc"]:
                rows.append((k, e, f))
    def esc(c):
        if any(ch in c for ch in (",", '"', "\n")):
            return '"' + c.replace('"', '""') + '"'
        return c
    out = [",".join(esc(c) for c in r) for r in rows]
    return "\n".join(out)+"\n"

def main():
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

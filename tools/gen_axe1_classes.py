#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur AXE 1 — émet les fichiers Config du mod (source de vérité unique).
Régénère :
  Mods/DeadHotSummer/Config/progression.xml   (8 attributs-catégories : Survivant + 7 branches ;
                                                skills par sous-classe ; perks)
  Mods/DeadHotSummer/Config/items.xml          (livres de classe + magazines, descriptions claires)
  Mods/DeadHotSummer/Config/loot.xml           (gating loot des magazines par cvar)
  Mods/DeadHotSummer/Config/Localization.csv   (EN+FR ; NB: V3.0 charge Localization.CSV, pas .txt)

UI : chaque BRANCHE = un onglet (attribut visible) contenant ses 2 sous-classes (skills).
La barre de catégories affiche Localization.Get(attribut.Name) -> Name est en MINUSCULES.
Le masquage des attributs vanilla + l'affichage de nos catégories sont gérés par le patch
Harmony SkillCategoryPatch (allowlist: attClass* + attCrafting).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "Mods", "DeadHotSummer", "Config")

LVL = [1, 12, 24, 36, 48]  # paliers PlayerLevel par rang (fin de classe ~niv 45-55)

# Perks par "kind" (type d'arme signature). Effets = passive_effect vérifiés vanilla.
# (suffixe, EN, FR, effet, op, v1, v5, scoped_au_tag, EN desc, FR desc)
PERKS = {
    "gun": [
        ("Damage","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases your class weapon damage.","Augmente les dégâts de l'arme de classe."),
        ("Handling","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves aim, reload feel and weapon handling.","Améliore la prise en main et la maniabilité."),
        ("Reload","Fast Reload","Rechargement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Reloads your class weapon faster.","Recharge l'arme de classe plus vite."),
        ("Aim","Precision","Précision","SpreadMultiplierAiming","perc_add","-.06","-.30",True,"Reduces aimed spread for tighter shots.","Réduit la dispersion en visée."),
    ],
    "bow": [
        ("Damage","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases bow/crossbow damage.","Augmente les dégâts arc/arbalète."),
        ("Handling","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves bow/crossbow handling.","Améliore la maniabilité arc/arbalète."),
        ("Draw","Quick Draw","Armement rapide","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Nocks and reloads arrows/bolts faster.","Encoche et recharge flèches/carreaux plus vite."),
        ("Velocity","Power Shot","Tir puissant","ProjectileVelocity","perc_add",".10",".50",True,"Increases projectile velocity and range.","Augmente la vitesse et la portée des projectiles."),
    ],
    "melee": [
        ("Damage","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases your class melee damage.","Augmente les dégâts de mêlée de classe."),
        ("Handling","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves melee handling.","Améliore la maniabilité en mêlée."),
        ("Dismember","Brutality","Brutalité","DismemberChance","base_add",".05",".25",True,"Increases dismemberment chance.","Augmente les chances de démembrement."),
        ("Stamina","Conditioning","Conditionnement","StaminaLoss","perc_add","-.06","-.30",False,"Reduces stamina spent attacking.","Réduit l'endurance dépensée en attaquant."),
    ],
    "thrown": [
        ("Damage","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases thrown weapon damage.","Augmente les dégâts des armes de jet."),
        ("Handling","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves thrown weapon handling.","Améliore la maniabilité des armes de jet."),
        ("Velocity","Strong Arm","Bon bras","ProjectileVelocity","perc_add",".10",".50",True,"Throws farther and faster.","Lance plus loin et plus vite."),
    ],
    "robotics": [
        ("Damage","Damage","Dégâts","EntityDamage","perc_add",".08",".40",True,"Increases robotics/turret damage.","Augmente les dégâts robotiques/tourelles."),
        ("Handling","Handling","Maniement","WeaponHandling","perc_add",".10",".50",True,"Improves robotics handling.","Améliore la maniabilité robotique."),
        ("Reload","Maintenance","Maintenance","ReloadSpeedMultiplier","perc_add","-.06","-.30",True,"Reloads/services robotics faster.","Recharge/entretient la robotique plus vite."),
    ],
    "tools": [
        ("Harvest","Harvesting","Récolte","HarvestCount","perc_add",".10",".50",True,"Harvests more resources with class tools.","Récolte plus de ressources avec les outils de classe."),
        ("Block","Power Tools","Outils puissants","BlockDamage","perc_add",".10",".50",True,"Increases block/harvest damage with tools.","Augmente les dégâts aux blocs avec les outils."),
        ("Stamina","Conditioning","Conditionnement","StaminaLoss","perc_add","-.06","-.30",False,"Reduces stamina spent using tools.","Réduit l'endurance dépensée avec les outils."),
    ],
}

# Branches : (cléBranche, EN, FR, icône, [ sous-classes ])
# sous-classe : (code, EN, FR, tag d'arme vérifié, kind, foreignId, icône, EN flavor, FR flavor)
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

# Toutes les sous-classes à plat (pour items/loot).
SUBS = [s for _bk,_en,_fr,_ic,subs in BRANCHES for s in subs]

def cvar(code): return "dhsCls" + code
def attr_of_branch(bk): return "attClass" + bk          # ex. attClassFarmer (Name -> minuscules cote moteur)

# ============================================================================
# SIGNATURES — contenu EXCLUSIF par sous-classe (au-dela des perks de stats).
#   extra_perks : perks 5 niveaux supplementaires (cvar-gates) propres a l'identite.
#                 (suffixe, EN, FR, effet, op, v1, v5, tags, EN desc, FR desc)
#   unlock      : perk "deblocage de craft" (max 1, cout 0, octroye par livre+magazine)
#                 -> passive_effect RecipeTagUnlocked tags=<noms de recettes signature>.
#                 (suffixe, EN, FR, icone, recettes_csv, EN desc, FR desc)
#   items/recipes/buffs : XML brut des craftables signature.
#   loc         : (cle, EN, FR) pour items/buffs (les perks tirent leur loc des tuples).
# Deblocage de recette = methode vanilla blindee : RecipeTagUnlocked matchant le NOM de
# la recette (cf. ammoShotgunSlug). Recettes taggees "learnable" comme en vanilla.
# Seul Fermier est rempli pour l'instant (exemplaire) ; les autres viendront ensuite.
# ============================================================================
SIGNATURES = {
    # --- Agriculteur : cultures + fusil a pompe -> Cartouche de fermier (slug renforce) ---
    "FarmAgri": {
        "extra_perks": [
            ("GreenThumb","Green Thumb","Main verte","HarvestCount","perc_add",".15",".75",
             "cropHarvest,wildCropsHarvest","Harvest significantly more from your own crops.",
             "Récolte nettement plus sur vos propres cultures."),
        ],
        "unlock": ("Arsenal","Farmer's Arsenal","Arsenal du fermier","ui_game_symbol_shotgun",
                   "dhsAmmoFarmerSlug",
                   "Unlocks crafting Farmer Slugs (heavy shotgun slugs) at a workbench.",
                   "Débloque la fabrication de Cartouches de fermier (balles lourdes) à l'établi."),
        # Extends ammoShotgunSlug (slug base_set 102 tags=perkBoomstick) ; on AJOUTE en perc_add
        # scope perkBoomstick -> compose proprement par-dessus la base heritee.
        "items": [
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
        ],
        "recipes": [
            '<recipe name="dhsAmmoFarmerSlug" count="2" craft_area="workbench" craft_time="4" tags="learnable,workbenchCrafting"><ingredient name="ammoShotgunShell" count="3"/><ingredient name="resourceGunPowder" count="4"/><ingredient name="resourceForgedIron" count="1"/></recipe>',
        ],
        "buffs": [],
        "loc": [
            ("dhsAmmoFarmerSlug","Farmer Slug","Cartouche de fermier"),
            ("dhsAmmoFarmerSlugDesc","A heavy hand-packed shotgun slug that hits much harder than a standard slug. Crafted only by Farmers.",
             "Une lourde cartouche à balle montée main, bien plus puissante qu'une balle standard. Fabriquée uniquement par les Agriculteurs."),
        ],
    },
    # --- Cuisinier : cuisine + gourdins -> Festin d'équipe (repas qui buff le groupe) ---
    "FarmCook": {
        "extra_perks": [
            ("WellFed","Hearty Cook","Fin gourmet","PhysicalDamageResist","base_add","1","5",
             "","Your own body better withstands punishment (passive toughness).",
             "Votre corps encaisse mieux les coups (robustesse passive)."),
        ],
        "unlock": ("Kitchen","Cook's Kitchen","Cuisine du chef","ui_game_symbol_fork",
                   "dhsFoodFeast",
                   "Unlocks cooking the Team Feast: a shared meal that buffs nearby allies.",
                   "Débloque la cuisson du Festin d'équipe : un plat qui buff les alliés proches."),
        # Festin AUTONOME (pas d'Extends) : un seul effect_group -> un seul buffProcessConsumables.
        "items": [
            '''    <item name="dhsFoodFeast">
      <property name="Tags" value="food,foodSkill,fitness"/>
      <property name="HoldType" value="31"/>
      <property name="DisplayType" value="foodWater"/>
      <property name="Meshfile" value="@:Other/Items/Misc/parcelPrefab.prefab"/>
      <property name="DropMeshfile" value="@:Other/Items/Misc/sack_droppedPrefab.prefab"/>
      <property name="Material" value="Morganic"/>
      <property name="Stacknumber" value="10"/>
      <property name="EconomicValue" value="200"/>
      <property name="CustomIcon" value="foodMeatStew"/>
      <property name="CustomIconTint" value="ff9933"/>
      <property name="DescriptionKey" value="dhsFoodFeastDesc"/>
      <property name="SoundPickup" value="food_bowl1_grab"/>
      <property name="SoundPlace" value="food_bowl1_place"/>
      <property class="Action0">
        <property name="Class" value="Eat"/>
        <property name="Delay" value="1.0"/>
        <property name="Sound_start" value="player_drinking"/>
      </property>
      <property name="Group" value="Food/Cooking"/>
      <effect_group name="dhsFeast" tiered="false">
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="$foodAmountAdd" operation="add" value="60"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="foodHealthAmount" operation="add" value="30"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="ModifyCVar" cvar="$waterAmountAdd" operation="add" value="25"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="dhsBuffFeast"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="dhsBuffFeast" target="otherAOE" range="25"/>
        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddBuff" buff="buffProcessConsumables"/>
      </effect_group>
    </item>''',
        ],
        "recipes": [
            '<recipe name="dhsFoodFeast" count="1" craft_area="campfire" craft_tool="toolCookingPot" craft_time="30" tags="learnable"><ingredient name="foodGrilledMeat" count="3"/><ingredient name="foodCropPotato" count="3"/><ingredient name="foodCropCorn" count="3"/><ingredient name="resourceAnimalFat" count="2"/><ingredient name="drinkJarBoiledWater" count="2"/></recipe>',
        ],
        "buffs": [
            '''    <buff name="dhsBuffFeast" name_key="dhsBuffFeastName" description_key="dhsBuffFeastDesc" icon="ui_game_symbol_fork" icon_color="255,153,51">
      <duration value="600"/>
      <stack_type value="replace"/>
      <effect_group>
        <passive_effect name="PhysicalDamageResist" operation="base_add" value="15"/>
        <passive_effect name="StaminaLoss" operation="perc_add" value="-.15"/>
      </effect_group>
    </buff>''',
        ],
        "loc": [
            ("dhsFoodFeast","Team Feast","Festin d'équipe"),
            ("dhsFoodFeastDesc","A hearty shared meal. Eating it feeds you well and buffs nearby allies. Cooked only by Cooks.",
             "Un copieux repas partagé. Le manger vous rassasie et buff les alliés proches. Cuisiné uniquement par les Cuisiniers."),
            ("dhsBuffFeastName","Team Feast","Festin d'équipe"),
            ("dhsBuffFeastDesc","Well fed by a Cook: reduced damage taken and stamina use.",
             "Bien nourri par un Cuisinier : dégâts subis et endurance dépensée réduits."),
        ],
    },
}

def sig(code): return SIGNATURES.get(code)

# ---------- recipes.xml (signatures) ----------
def gen_recipes():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — recettes signature de classe. -->',
         '<configs>', '  <append xpath="/recipes">']
    for code in [c for c,_e,_f,_t,_k,_fi,_i,_ef,_ff in SUBS]:
        s = sig(code)
        if not s: continue
        for r in s["recipes"]:
            L.append("    " + r)
    L += ['  </append>', '</configs>']
    return "\n".join(L)+"\n"

# ---------- buffs.xml (signatures) ----------
def gen_buffs():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — buffs signature de classe. -->',
         '<configs>', '  <append xpath="/buffs">']
    for code in [c for c,_e,_f,_t,_k,_fi,_i,_ef,_ff in SUBS]:
        s = sig(code)
        if not s: continue
        for b in s["buffs"]:
            L.append(b)
    L += ['  </append>', '</configs>']
    return "\n".join(L)+"\n"

# ---------- progression.xml ----------
def gen_progression():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — ne pas editer a la main. -->',
         '<configs>',
         '  <append xpath="/progression/attributes">']
    # Survivant (commun) + 7 branches, tous visibles (style attBooks/attCrafting)
    L.append('    <attribute name="attClassCommon" name_key="dhsAttClassCommonName" desc_key="dhsAttClassCommonDesc" icon="ui_game_symbol_modded" min_level="0" max_level="0" base_skill_point_cost="0"/>')
    for bk,_en,_fr,icon,_subs in BRANCHES:
        a = attr_of_branch(bk)
        L.append(f'    <attribute name="{a}" name_key="dhs{a}Name" desc_key="dhs{a}Desc" icon="{icon}" min_level="0" max_level="0" base_skill_point_cost="0"/>')
    L.append('  </append>')
    # Skills : commun sous attClassCommon ; chaque sous-classe sous l'attribut de sa branche
    L.append('  <append xpath="/progression/skills">')
    L.append('    <skill name="skillClassCommon" parent="attClassCommon" name_key="dhsSkillClassCommonName" desc_key="dhsSkillClassCommonDesc" icon="ui_game_symbol_modded"><effect_group/></skill>')
    for bk,_en,_fr,_ic,subs in BRANCHES:
        a = attr_of_branch(bk)
        for code,_sen,_sfr,_tag,_kind,_fid,sicon,_efl,_ffl in subs:
            L.append(f'    <skill name="skillClass{code}" parent="{a}" name_key="dhsSkillClass{code}Name" desc_key="dhsSkillClass{code}Desc" icon="{sicon}"><effect_group/></skill>')
    L.append('  </append>')
    # Perks
    L.append('  <append xpath="/progression/perks">')
    # Classe de base "Survivant" (points de niveau, accessible a tous)
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
    # Perks des sous-classes (stats) + signatures (perks bonus + deblocage de craft)
    for code,_sen,_sfr,tag,kind,_fid,sicon,_efl,_ffl in SUBS:
        for (suf,_pen,_pfr,nm,op,v1,v5,scoped,_ed,_fd) in PERKS[kind]:
            L.append(f'    <perk name="perkClass{code}{suf}" parent="skillClass{code}" name_key="dhsPerk{code}{suf}Name" desc_key="dhsPerk{code}{suf}Desc" icon="{sicon}" max_level="5">')
            for i in range(5):
                L.append(f'      <level_requirements level="{i+1}"><requirement name="CVarCompare" cvar="{cvar(code)}" operation="Equals" value="1" desc_key="dhsReqClass{code}"/><requirement name="PlayerLevel" operation="GTE" value="{LVL[i]}"/></level_requirements>')
            tagattr = f' tags="{tag}"' if scoped else ''
            L.append(f'      <effect_group><passive_effect name="{nm}" operation="{op}" level="1,5" value="{v1},{v5}"{tagattr}/></effect_group>')
            L.append('    </perk>')
        s = sig(code)
        if s:
            # Perks bonus signature (5 niveaux, gates comme les perks de stats)
            for (suf,_pen,_pfr,nm,op,v1,v5,sgtag,_ed,_fd) in s["extra_perks"]:
                L.append(f'    <perk name="perkClass{code}{suf}" parent="skillClass{code}" name_key="dhsPerk{code}{suf}Name" desc_key="dhsPerk{code}{suf}Desc" icon="{sicon}" max_level="5">')
                for i in range(5):
                    L.append(f'      <level_requirements level="{i+1}"><requirement name="CVarCompare" cvar="{cvar(code)}" operation="Equals" value="1" desc_key="dhsReqClass{code}"/><requirement name="PlayerLevel" operation="GTE" value="{LVL[i]}"/></level_requirements>')
                tagattr = f' tags="{sgtag}"' if sgtag else ''
                L.append(f'      <effect_group><passive_effect name="{nm}" operation="{op}" level="1,5" value="{v1},{v5}"{tagattr}/></effect_group>')
                L.append('    </perk>')
            # Perk de deblocage de craft (max 1, gratuit ; octroye par livre+magazine ; visible)
            usuf,_uen,_ufr,uicon,utags,_ued,_ufd = s["unlock"]
            L.append(f'    <perk name="perkClass{code}{usuf}" parent="skillClass{code}" name_key="dhsPerk{code}{usuf}Name" desc_key="dhsPerk{code}{usuf}Desc" icon="{uicon}" max_level="1" base_skill_point_cost="0">')
            L.append(f'      <level_requirements level="1"><requirement name="CVarCompare" cvar="{cvar(code)}" operation="Equals" value="1" desc_key="dhsReqClass{code}"/></level_requirements>')
            L.append(f'      <effect_group><passive_effect name="RecipeTagUnlocked" operation="base_set" level="1" value="1" tags="{utags}"/></effect_group>')
            L.append('    </perk>')
    L.append('  </append>')
    L.append('</configs>')
    return "\n".join(L)+"\n"

# ---------- items.xml ----------
def gen_items():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- GENERE par tools/gen_axe1_classes.py — ne pas editer a la main. -->',
         '<configs>', '  <append xpath="/items">']
    for code,_sen,_sfr,_tag,kind,fid,_sicon,_efl,_ffl in SUBS:
        firstperk = f"perkClass{code}{PERKS[kind][0][0]}"
        s = sig(code)
        unlockperk = f"perkClass{code}{s['unlock'][0]}" if s else None
        # Livre de classe
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
        L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddProgressionLevel" progression_name="{firstperk}" level="1"/>')
        if unlockperk:  # le choix de classe debloque immediatement le craft signature
            L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddProgressionLevel" progression_name="{unlockperk}" level="1"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="GiveExp" exp="50"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="DeadHotSummer.MinEventActionDhsClassEvent, DeadHotSummer"/>')
        L.append('      </effect_group>')
        L.append('    </item>')
        # Magazine de classe
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
        L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddProgressionLevel" progression_name="{firstperk}" level="1"/>')
        if unlockperk:  # la sœur (debloquee par completion, sans livre) debloque le craft au 1er magazine
            L.append(f'        <triggered_effect trigger="onSelfPrimaryActionEnd" action="AddProgressionLevel" progression_name="{unlockperk}" level="1"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="GiveExp" exp="50"/>')
        L.append('        <triggered_effect trigger="onSelfPrimaryActionEnd" action="DeadHotSummer.MinEventActionDhsClassEvent, DeadHotSummer"/>')
        L.append('      </effect_group>')
        L.append('    </item>')
    # Items signature (apres les livres/magazines, meme bloc append)
    for code in [c for c,_e,_f,_t,_k,_fi,_i,_ef,_ff in SUBS]:
        s = sig(code)
        if not s: continue
        for it in s["items"]:
            L.append(it)
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
    # Categories (barre de catégories = Localization.Get(attribut.Name) -> Name en MINUSCULES)
    rows.append(("attclasscommon","Survivor","Survivant"))
    for bk,en,fr,_ic,_subs in BRANCHES:
        rows.append((attr_of_branch(bk).lower(), en, fr))
    # Cles name_key/desc_key des attributs (utilisees ailleurs dans l'UI)
    rows.append(("dhsAttClassCommonName","Survivor","Survivant"))
    rows.append(("dhsAttClassCommonDesc","Common skills for everyone","Compétences communes à tous"))
    for bk,en,fr,_ic,_subs in BRANCHES:
        a = attr_of_branch(bk)
        rows.append((f"dhs{a}Name", en, fr))
        rows.append((f"dhs{a}Desc", f"{en} branch", f"Branche {fr}"))
    # Classe de base
    rows += [
        ("dhsSkillClassCommonName","Survivor","Survivant"),
        ("dhsSkillClassCommonDesc","Common skills available to everyone","Compétences communes à tous"),
        ("dhsPerkCommonToughnessName","Toughness","Robustesse"),
        ("dhsPerkCommonToughnessDesc","Reduces physical damage taken.","Réduit les dégâts physiques subis."),
        ("dhsPerkCommonForagerName","Forager","Cueilleur"),
        ("dhsPerkCommonForagerDesc","Harvest more food from animals and wild plants.","Récolte plus de nourriture sur les animaux et plantes sauvages."),
        ("dhsPerkCommonEnduranceName","Endurance","Endurance"),
        ("dhsPerkCommonEnduranceDesc","Reduces stamina loss from actions.","Réduit la perte d'endurance des actions."),
    ]
    # Sous-classes : skills, req, livre, magazine, perks
    for code,en,fr,_tag,kind,_fid,_sicon,efl,ffl in SUBS:
        rows.append((f"dhsSkillClass{code}Name", en, fr))
        rows.append((f"dhsSkillClass{code}Desc", f"Specializes in {efl}.", f"Spécialisé dans {ffl}."))
        rows.append((f"dhsReqClass{code}", f"Requires the {en} class", f"Nécessite la classe {fr}"))
        rows.append((f"dhsBookClass{code}", f"Class Manual: {en}", f"Manuel de classe : {fr}"))
        rows.append((f"dhsBookClass{code}Desc",
                     f"Become a {en}: master {efl}. Reading it unlocks the {en} skill tree and grants a starting point.",
                     f"Devenez {fr} : maîtrisez {ffl}. La lecture débloque l'arbre {fr} et octroie un point de départ."))
        rows.append((f"dhsMag{code}", f"{en} Manual", f"Manuel : {fr}"))
        rows.append((f"dhsMag{code}Desc",
                     f"A {en} magazine. Reading it advances the {en} class. Useful only to members of this class.",
                     f"Un magazine de {fr}. Le lire fait progresser la classe {fr}. Utile uniquement à cette classe."))
        for (suf,pen,pfr,_nm,_op,_v1,_v5,_sc,ed,fd) in PERKS[kind]:
            rows.append((f"dhsPerk{code}{suf}Name", f"{en}: {pen}", f"{fr} : {pfr}"))
            rows.append((f"dhsPerk{code}{suf}Desc", ed, fd))
        # Signature : perks bonus + perk de deblocage + items/buffs
        s = sig(code)
        if s:
            for (suf,pen,pfr,_nm,_op,_v1,_v5,_sg,ed,fd) in s["extra_perks"]:
                rows.append((f"dhsPerk{code}{suf}Name", f"{en}: {pen}", f"{fr} : {pfr}"))
                rows.append((f"dhsPerk{code}{suf}Desc", ed, fd))
            usuf,uen,ufr,_uic,_ut,ued,ufd = s["unlock"]
            rows.append((f"dhsPerk{code}{usuf}Name", uen, ufr))
            rows.append((f"dhsPerk{code}{usuf}Desc", ued, ufd))
            for (k,e,f) in s["loc"]:
                rows.append((k, e, f))
    def esc(c):
        # Quoting CSV standard : entoure de guillemets si virgule/guillemet/saut de ligne.
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
    # supprime l'ancienne localisation .txt (V3.0 charge .csv)
    old = os.path.join(CFG, "Localization.txt")
    if os.path.exists(old):
        os.remove(old); print("supprimé Localization.txt (obsolète)")

if __name__ == "__main__":
    main()

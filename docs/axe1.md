# AXE 1 — Classes & spécialisations (conception complète)

## 1. Modèle de progression (validé / affiné le 2026-06-18)

### Deux tracks complémentaires
| Track | Source | Sert à |
|---|---|---|
| **Points de niveau** (natif, 1/niveau) | montée de niveau | Classe de **base** (commune) + ranger les **perks** de sa sous-classe perso |
| **Livres de classe** (magazines class-gated) | loot **uniquement** des classes débloquées | débloquer les **capacités/recettes signature** de la sous-classe (modèle magazine natif) |

- **Classe de base « Survivant »** : tout le monde l'a. Perks génériques (survie, port, endurance, combat de base) payés aux **points de niveau**. Pas de gate.
- **Sous-classe perso** : choisie via un **livre de classe** (item). Le lire pose `dhsCls<Code>=1`, octroie les perks de base de la voie + un **kit minimal**.
  - **Perks exclusifs** (points de niveau) : bonus passifs gatés `CVarCompare cvar="dhsCls<Code>"` → inaccessibles aux autres voies. **AUCUN prérequis bloquant** entre eux (ordre libre).
  - **Capacités/recettes signature** (magazines) : les magazines de la classe ne **droppent** (`LootProb` gaté cvar) et ne se **lisent** (effect_group `requirement` cvar) que si la classe est débloquée. Les lire débloque le gear/les recettes exclusives.
- **Arme/gear signature** : chaque sous-classe « possède » un créneau d'arme/outil avec des bonus **exclusifs** (même les classes support ont un créneau de combat).
- **Calibrage** : volume (nb de perks × rangs + nb de magazines) dimensionné pour **compléter une sous-classe vers le niveau 45-55**.

### Complétion & multi-classe
- **Complétion d'une sous-classe** = tous ses perks exclusifs au max **ET** tous ses magazines lus. Détecté en **C# (`ClassManager`)** → pose `dhsCls<Code>Done=1`.
- À la complétion :
  1. déblocage de la **sous-classe sœur** de la même branche principale (ses livres deviennent lootables/lisibles, ses perks achetables) ;
  2. `dhsClassSlotFree=1` → droit de **démarrer une sous-classe d'une autre branche** (nouveau livre de classe utilisable).
- Garde-fou : tant qu'une sous-classe « étrangère » est en cours et non complétée, on ne peut pas en démarrer une 3ᵉ (séquentiel entre branches ; la sœur de la branche déjà maîtrisée est offerte en bonus).

### CVars (persistants, préfixe `dhs`)
- `dhsCls<Code>` (0/1) : sous-classe débloquée (gate loot/lecture/perks). Ex. `dhsClsFarmAgri`.
- `dhsCls<Code>Done` (0/1) : sous-classe complétée.
- `dhsClassSlotFree` (0/1) : droit de démarrer une nouvelle branche.
- `dhsClassActiveForeign` (code) : sous-classe étrangère en cours (garde-fou séquentiel).
- `dhsClassDoneCount` (int) : nb de sous-classes complétées (stats/UI).

## 2. Classe de base — « Survivant » (commune, points de niveau)
Perks génériques, non exclusifs (skill `skillClassCommon`) : capacité de port, endurance/sprint,
récupération de vie, dépeçage/récolte de base, résistance environnement, vitesse de craft de base.
But : socle jouable early-game quelle que soit la classe (ne casse pas le early-game).

## 3. Les 14 sous-classes (identité + signature exclusive)

> Légende : **Signature** = arme/gear exclusif (bonus que SEULE cette classe obtient) · **Perks** = bonus passifs (points) · **Magazines** = capacités/recettes débloquées par lecture (class-gated).

### 1. Ingénieur
- **Mécanicien (`EngiMech`)** — robotique & véhicules.
  - Signature : **tourelles/drones de récup' + véhicules**. Bonus exclusifs robotiques & véhicule.
  - Perks : dégâts/portée tourelles, durée drone, vitesse/conso véhicule, réparations à moindre coût.
  - Magazines : recettes tourelle/drone améliorés, mods véhicule exclusifs.
- **Électricien (`EngiElec`)** — électricité & pièges.
  - Signature : **pièges électriques** (barbelés électrifiés, blade traps câblés) + matraque (stun).
  - Perks : dégâts pièges, efficacité énergie, portée fils, recharge batteries.
  - Magazines : recettes pièges/relais/solaire exclusives.

### 2. Médecin
- **Chirurgien (`MedicSurg`)** — soin & lames.
  - Signature : **lames/scalpel** (saignement) + soin.
  - Perks : efficacité soins, vitesse de pansement, retrait de debuffs, dégâts saignement lames.
  - Magazines : recettes trousses trauma / bandages avancés exclusives.
- **Chimiste/Pharmacien (`MedicChem`)** — chimie & jet.
  - Signature : **armes de jet chimiques** (cocktails, gaz, contact) + drogues.
  - Perks : durée/effet drogues, dégâts incendiaires/chimiques jetés, maîtrise station chimique.
  - Magazines : recettes stims de combat / drogues supérieures exclusives.

### 3. Soldat
- **Tireur d'élite (`SoldSnip`)** — fusils marksman.
  - Signature : **fusils (marksman/sniper)**.
  - Perks : dégâts/headshot, stabilité visée, vitesse rechargement, lunette.
  - Magazines : recettes munitions AP / fusil exclusif.
- **Assaut (`SoldAslt`)** — armes auto & explosifs.
  - Signature : **mitrailleuses (full-auto)** + grenades/explosifs.
  - Perks : contrôle recul, chargeurs tambour, dégâts explosifs, mobilité run-and-gun.
  - Magazines : recettes chargeurs/explosifs exclusives.

### 4. Survivaliste
- **Chasseur/Traqueur (`SurvHunt`)** — arcs & arbalètes.
  - Signature : **arcs/arbalètes** (l'exemple utilisateur) + chasse.
  - Perks : dégâts arc/arbalète, vitesse d'armement, pistage animaux, +viande/peaux.
  - Magazines : recettes **flèches/carreaux spéciaux** exclusifs, arc/arbalète signature.
- **Herboriste/Cueilleur (`SurvHerb`)** — plantes & lances.
  - Signature : **lances** (+ poison) + cueillette.
  - Perks : rendement cueillette, dégâts poison lances, résistances naturelles.
  - Magazines : recettes remèdes/tisanes/poisons exclusifs.

### 5. Bâtisseur
- **Architecte (`BuilArch`)** — fortifications. *(contact AXE 2 : augmente le score de défense de base)*
  - Signature : **masses (démolition)** + blocs renforcés.
  - Perks : +PV blocs, upgrade/réparation moins chers, dégâts masse.
  - Magazines : recettes blocs renforcés/défensifs exclusifs.
- **Artisan (`BuilArti`)** — ateliers & robotique mêlée.
  - Signature : **masse de récup' robotique (junk sledge)** + ateliers.
  - Perks : qualité de craft, vitesse ateliers, coûts réduits, stockage.
  - Magazines : recettes upgrades d'ateliers / mobilier exclusifs.

### 6. Éclaireur
- **Pisteur (`ScoutTrac`)** — mobilité & pistolets.
  - Signature : **pistolets (gunslinger)** + mobilité.
  - Perks : vitesse course/endurance, révélation carte, détection loot/trésor, dégâts pistolet.
  - Magazines : recettes pistolet/munitions exclusives.
- **Infiltrateur/Pilleur (`ScoutInfi`)** — furtivité & poings.
  - Signature : **armes de poing/knuckles** furtives + silencieux.
  - Perks : dégâts furtifs, discrétion, crochetage coffres, meilleur loot.
  - Magazines : recettes silencieux / outils de crochetage exclusifs.

### 7. Fermier
- **Agriculteur (`FarmAgri`)** — cultures & fusil à pompe.
  - Signature : **fusil à pompe (pump)** — l'exemple utilisateur — + agriculture.
  - Perks : rendement/croissance cultures, dégâts/portée pompe, recharge pompe.
  - Magazines : recettes **pompe signature + cartouches spéciales** exclusives, graines haut-rendement.
- **Cuisinier (`FarmCook`)** — cuisine & gourdins.
  - Signature : **gourdins/contondant** (« ustensiles ») + cuisine d'équipe.
  - Perks : qualité buffs nourriture (effets d'équipe), dégâts contondant, conservation aliments.
  - Magazines : recettes **repas uniques à buffs d'équipe** exclusifs.

## 4. Acquisition & gating (résumé technique)
- **Livre de classe** (item magazine) par sous-classe : lecture → `ModifyCVar dhsCls<Code>=1` + perks de base + kit. Le livre n'est obtenable qu'au choix de classe (quête de sélection / récompense), pas en loot libre.
- **Magazines de classe** : `LootProb` (loot.xml/items via passive_effect tags) gaté `CVarCompare dhsCls<Code>` → ne droppent que pour les classes débloquées ; effet de lecture gaté par le même cvar → lisibles seulement par la classe.
- **Perks exclusifs** : `level_requirements` = `CVarCompare dhsCls<Code> Equals 1` (+ éventuellement `PlayerLevel` pour le rythme, **jamais** de `ProgressionLevel` d'un autre perk → pas de blocage croisé).
- **Sélection initiale** : `game_first_spawn` (gameevent) → quête de sélection → octroi des livres de classe disponibles ; le joueur en lit un.
- **Complétion → slots** : `ClassManager` (C#) surveille perks max + magazines lus → pose `dhsCls<Code>Done`, débloque la sœur, `dhsClassSlotFree=1`.

## 5. Convention de scoping des bonus d'arme
Les `passive_effect` de combat sont scopés via les **tags d'arme prouvés par le vanilla**
(et non les tags de loot type `rifleSkill`) :
| Catégorie | Tag de scoping | | Catégorie | Tag de scoping |
|---|---|---|---|---|
| Fusils | `perkDeadEye` | | Mitrailleuses | `perkMachineGunner` |
| Fusils à pompe | `perkBoomstick` | | Pistolets | `perkGunslinger` |
| (les autres seront vérifiés par sous-classe au moment de l'implémentation) | | | | |

L'exclusivité vient du **gate `CVarCompare`** sur l'achat du perk, pas du tag.

## 6. Statut
- [x] Taxonomie + convention (J1.1)
- [x] Squelette progression (attClasses + skills) (J1.1)
- [x] Conception complète des 14 classes (J1.2, validé)
- [x] Classe de base « Survivant » : 3 perks (Robustesse, Cueilleur, Endurance) — points de niveau (J1.3)
- [x] Sous-classe exemplaire Soldat/Tireur : 4 perks gatés `CVarCompare` + livre de classe + magazine class-gated + localisation (J1.4a)
- [ ] J1.4b : loot-gating des magazines de classe (drop seulement pour la classe) + recette signature
- [ ] Réplication aux 13 autres
- [ ] Quête de sélection + `game_first_spawn`
- [ ] `ClassManager` C# (complétion → slots, séquentiel)

> Validation **runtime** (chargement serveur sans erreur de patch, comportement des gates) à faire à un jalon de test dédié.

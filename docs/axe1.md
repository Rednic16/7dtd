# AXE 1 — Classes & spécialisations

## Objectif
Donner au joueur une identité de départ et une progression orientée métier, avec des
compétences exclusives à sa voie, intégrée aux skill points + magazines natifs.

## Modèle de progression (option A hybride, validé)
- **Identité** : un « livre de classe » (item magazine consommable) par sous-branche. Le lire
  pose le cvar de classe, octroie les perks de base et un kit de départ minimal.
- **Moyen de progression** : **skill points natifs** (1/niveau). Les compétences exclusives sont
  des **perks** sous des skills custom, dont l'achat est **bloqué** tant que le cvar de classe
  n'est pas posé (`requirement name="CVarCompare"` dans `level_requirements` — confirmé
  fonctionnel par décompilation de `ProgressionFromXml` → `RequirementBase.ParseRequirementGroup`).
- **Prérequis croisés** : via `requirement name="ProgressionLevel" progression_name="perkX"`
  dans `level_requirements` (blocage dur à l'achat, peut se croiser : C exige A et/ou B).
- **Compétences communes** : perks accessibles à toutes les classes (pas de gate cvar).
- **Complétion 100 %** : toutes les compétences exclusives d'une classe au max → détecté en
  **C#** (`ClassManager`) → pose le cvar de complétion + libère un slot pour une 2ᵉ classe.
- **Séquentiel** : pas de progression simultanée ; la 2ᵉ classe ne s'ouvre qu'après complétion.

## Branches & sous-branches (codes internes)
| # | Branche | Sous-branche | Code sous-branche |
|---|---|---|---|
| 1 | Ingénieur | Mécanicien | `EngiMech` |
| 1 | Ingénieur | Électricien | `EngiElec` |
| 2 | Médecin | Chirurgien | `MedicSurg` |
| 2 | Médecin | Chimiste/Pharmacien | `MedicChem` |
| 3 | Soldat | Tireur d'élite | `SoldSnip` |
| 3 | Soldat | Assaut (close-combat) | `SoldAslt` |
| 4 | Survivaliste | Chasseur/Traqueur | `SurvHunt` |
| 4 | Survivaliste | Herboriste/Cueilleur | `SurvHerb` |
| 5 | Bâtisseur | Architecte (fortifications) | `BuilArch` |
| 5 | Bâtisseur | Artisan (ateliers/mobilier) | `BuilArti` |
| 6 | Éclaireur | Pisteur | `ScoutTrac` |
| 6 | Éclaireur | Infiltrateur/Pilleur | `ScoutInfi` |
| 7 | Fermier | Agriculteur | `FarmAgri` |
| 7 | Fermier | Cuisinier | `FarmCook` |

## Convention de nommage (préfixe `dhs` = Dead Hot Summer)

### Progression (progression.xml)
- Attribut hôte caché : `attClasses`.
- Skill commun : `skillClassCommon`.
- Skill par sous-branche : `skillClass<Code>` (ex. `skillClassSoldSnip`).
- Perks exclusifs : `perkClass<Code><Nom>` (ex. `perkClassSoldSnipDeadeye`).
- Perks communs : `perkClassCommon<Nom>`.

### CVars joueur (persistants → pas de préfixe `_`)
- Choix de classe (1 par sous-branche, 0/1) : `dhsCls<Code>` (ex. `dhsClsSoldSnip`).
  Posé à 1 par le livre de classe ; sert de gate `CVarCompare` aux perks exclusifs.
- Complétion d'une sous-branche (0/1) : `dhsCls<Code>Done` (posé par `ClassManager`).
- Nombre de classes complétées : `dhsClassDoneCount`.
- Slot libre pour une nouvelle classe (0/1) : `dhsClassSlotFree` (1 au départ ; remis à 1
  après complétion ; remis à 0 quand une classe est en cours).
- Classe en cours (code, pour le garde-fou séquentiel) : `dhsClassActive` (0 = aucune).

> Un perk exclusif est gaté par `CVarCompare cvar="dhsCls<Code>" operation="Equals" value="1"`,
> ce qui le rend inaccessible à toute autre voie. Comme le cvar reste à 1 même sur la 2ᵉ classe,
> les deux voies complétées restent jouables.

## Statut
- [x] Taxonomie + convention (ce doc)
- [ ] Squelette progression (attClasses + skills)
- [ ] Perks communs + exclusifs (gate cvar + prérequis croisés)
- [ ] Livres de classe + magazines + quête de sélection + kits
- [ ] `ClassManager` C# (complétion → slot, séquentiel)

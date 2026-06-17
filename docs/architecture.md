# Architecture — Dead Hot Summer

> Document vivant. Mis à jour à chaque jalon.

## Cible technique (vérifiée par décompilation de `Assembly-CSharp.dll`)

- Jeu : 7DTD **V3.0** (Unity 2022.3.62f2, Mono).
- DLL mod : **netstandard2.1**, chargée via `IModApi.InitMod(Mod)`.
- Patching : **HarmonyX** (`0Harmony.dll` fourni par `0_TFP_Harmony`).
- **EAC off requis** (DLL custom).

## Frontière XML vs C#

| | XML (Config XPath) | C# (DLL) |
|---|---|---|
| **AXE 1** | attributs/skills/perks de classe, gating `CVarCompare` en `level_requirements` (confirmé), livres/magazines de classe, quête de sélection, kits | détection complétion 100 % → cvar `class_complete`, garde-fou séquentiel multi-classe |
| **AXE 2** | classes bandits (`EntityBandit`), factions (`npc.xml`), groupes/spawners par gamestage, patrouilles errantes (`WanderingBandits`), refill sleeper | territoires, agro-en-territoire (injection Harmony), camps custom (spawn + `setHomeArea`), évaluation défense vs gamestage global, raids, refill camps custom |

## Points d'ancrage moteur confirmés

- **Gamestage** : `EntityPlayer.gameStage` = f(niveau, biome/région, jours sans mourir) ; agrégation `GameStageDefinition.CalcPartyLevel(List<int>)` (rendements décroissants). GS global = `CalcPartyLevel` sur tous les joueurs connectés.
- **Hooks** : `ModEvents.GameStartDone / PlayerSpawnedInWorld / GameUpdate / EntityKilled` (typés `ModEvent<SXxxData>`, handler `void H(ref SXxxData)`).
- **Territoire/leash** : `EntityAlive.setHomeArea(pos, maxDistance)`, `isWithinHomeDistance(...)`, tâche native `EAITerritorial`.
- **Ciblage** : `EAISetNearestEntityAsTarget` (override pour agro territoriale) ; `SetAttackTarget` / `SetInvestigatePosition`.
- **Bases joueurs** : `LandClaimBoundsHelper.GetEntryFromList(Vector3)`.
- **Spawn** : `EntityFactory.CreateEntity(...)` ; `SpawnManagerDynamic` (64–96 m d'un joueur, la nuit) pilote `WanderingBandits`.
- **Entités** : pillards = dérivés d'`EntityBandit : EntityHuman` (combattant). `EntitySurvivor` = NPC ami (non utilisé pour le combat).

## État (jalons)

- **J0 — Scaffold** ✅ : `.gitignore`, structure mod, `ModInfo.xml`, projet C# (`netstandard2.1`), bootstrap `ModApi` (Harmony + ModEvents), build OK → `Mods/DeadHotSummer/DeadHotSummer.dll`.
- J1 — AXE 1 (classes) : à venir.
- J2 — AXE 2 bandits/spawn (XML) : à venir.
- J3 — AXE 2 territoires/agro/raids (C#) : à venir.
- J4 — Contact AXE1↔AXE2 + équilibrage : à venir.
- J5 — Doc/polish : à venir.

## Build & déploiement

`cd src/DeadHotSummer && dotnet build -c Release` → sortie dans `Mods/DeadHotSummer/`.

> Note outillage : seul **`ilspycmd`** (décompilation, outil .NET 6) nécessite `DOTNET_ROLL_FORWARD=LatestMajor` avec le SDK 8 installé ; le **build** du mod (netstandard2.1) n'en a pas besoin.

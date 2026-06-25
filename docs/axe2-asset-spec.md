# AXE 2 — Cahier des charges des ASSETS (à produire/sourcer)

Cible technique : **7 Days to Die V3.0 (b257), Unity 2022.3.62f2**. Tout asset custom est
chargé via un **AssetBundle** du mod : `Mesh="#@modfolder:Resources/<bundle>.unity3d?<Prefab>"`.
Le rendu doit fonctionner **côté serveur sans GPU** (donc PAS le système SDCS du joueur ; un
renderer standard/Mecanim convient, comme zombies/marchands).

---
## 1) PERSONNAGES PILLARDS — priorité 1 (le bloquant)

### Quantité (option économique recommandée)
- **1 personnage humanoïde de base riggé** + **4 variantes d'apparence** (texture/tenue), une par
  faction/tier :
  - **Maraudeur** : haillons, bric-à-brac (look misérable).
  - **Bande motorisée** : cuir/blouson, lunettes (look motard/routard).
  - **Milice** : tenue militaire/tactique (gilet, treillis).
  - **Congrégation (secte)** : robe/capuche de culte, peintures.
- (4 modèles distincts complets = mieux mais 4× le travail. 1 base + 4 textures = idéal coût/effet.)
- Bonus facultatif : 1 variante femme (mesh) pour varier.

### Mesh
- Export **FBX**. Humanoïde biped, **échelle réelle (1 unité = 1 m), ~1,85 m de haut**, Y-up,
  face vers **+Z**, **A-pose** (ou T-pose).
- Budget polys : **8 000–20 000 tris** par perso (ennemi). 1 mesh skinné (sous-meshes OK).
- **LODs** souhaités : LOD0 (100 %), LOD1 (~50 %), LOD2 (~25 %). Sinon LOD0 seul accepté.

### Rig / squelette (POINT CLÉ — voir décision plus bas)
- **Rig Unity « Humanoid » (Mecanim)** → permet de **réutiliser les animations du jeu** (marche/
  course/attaque/mort) par retargeting, **sans avoir à animer**. C'est ce qui évite le plus de travail.
- Prévoir un **socket d'arme** sur la main droite (transform vide, ex. `Weapon_Joint`) pour que
  l'arme tenue s'affiche (pillards armés).
- Transforms d'attache d'équipement nommés : `head`, `body`, `hands`, `feet` (optionnel mais utile).

### Textures (PBR, par variante)
- Jeu de maps : **Albedo (RGBA)**, **Normal**, **Metallic+Smoothness** (smoothness dans alpha),
  **AO**. (Emissive optionnel pour la secte.)
- Résolution : **2048×2048** (héro) ou **1024×1024** (suffisant pour un ennemi).
- Source : **PNG ou TGA**. Matériaux assignés dans Unity (shader standard/URP à l'import).

### Mort / ragdoll
- Colliders + Rigidbodies sur les os principaux pour le **ragdoll à la mort** (ou setup ragdoll Unity
  standard). Sinon on tentera `HasRagdoll` + collapse simple.

### Livrable attendu (au choix)
- **A. Idéal** : un **AssetBundle `bandits.unity3d`** buildé dans **Unity 2022.3.62f2**, contenant les
  prefabs nommés **exactement** : `dhsBanditMarauder`, `dhsBanditMotor`, `dhsBanditMilitia`,
  `dhsBanditSect` (prefab = mesh + Animator/Avatar + colliders + sockets). À déposer dans
  `Mods/DeadHotSummer/Resources/`.
- **B. Acceptable** : **FBX + textures (+ Animator/Avatar configuré si possible)**. On assemblera le
  prefab et le bundle ensemble dans Unity.

---
## 2) DRAPEAU DE CAPTURE — J2.6 (priorité 2)
Item à poser qui convertit un camp nettoyé en avant-poste.
- **Icône d'item** : PNG avec alpha, **source 256×256** (carré), fond transparent.
- **Modèle monde (le drapeau planté)** : FBX simple (mât + drapeau), ~**1,5–2 m**, + texture
  (1024² suffit). Pivot au pied du mât. (À défaut, on réutilisera un bloc vanilla.)

---
## 3) ICÔNES DE FACTION / UI — J2.3 réputation (priorité 3)
Pour marqueurs (carte/boussole) + UI de réputation.
- **4 emblèmes** (Maraudeur / Motorisé / Milice / Secte) : PNG **avec alpha**, **128×128** (ou
  152×152), idéalement **silhouette blanche** (le jeu les teinte) — style des `ui_game_symbol_*`.

---
## 4) (FACULTATIF) AMBIANCE DE CAMP — plus tard
- Bannières/totems de faction (FBX + texture), pour différencier visuellement les camps.
  Réutilisation d'assets vanilla possible si non fournis.

---
## DÉCISIONS qui changent le rig (à trancher)
1. **Voie d'animation** :
   - (a) **Rig Humanoid Mecanim** + on retarge les anims du jeu (recommandé, moins de travail) ; OU
   - (b) **Framework communautaire SCore** (standard NPC 7DTD) : rig selon SCore, anims fournies par
     le framework, mais ajoute une dépendance.
   - (c) Rig sur le **squelette zombie** exact (réutilise direct les anims zombie ; attaques = griffes).
2. **Tu produis toi-même** (Blender/Unity), tu **sources un asset** (marketplace/CC0 humanoïde
   riggé), ou tu veux que je **rédige le guide pas-à-pas** du build de bundle d'abord ?

> Dès que j'ai les prefabs nommés `dhsBandit*` dans `Resources/bandits.unity3d`, le branchement
> côté mod = **1 ligne par tier** (Mesh + AvatarController) dans le générateur. Le reste du gameplay
> AXE 2 est/ sera déjà prêt.

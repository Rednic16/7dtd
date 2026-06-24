# AXE 2 — Pillards : pipeline d'assets 3D custom (V3.0 / Unity 2022.3.62f2)

## Pourquoi
V3.0 ne fournit AUCUN combattant humanoïde animé exploitable en XML :
- **SDCS** (anims complètes) = codé en dur pour le joueur (`EModelSDCS.Init` lit `playerProfile`) → inutilisable par `EntityBandit`.
- **Modèle Npc / prefab marchand** = pas d'anim de marche/attaque/mort (PNJ statique).
- **Seuls les zombies** ont un rig de combat complet → apparence zombie.

⇒ Pour de vrais pillards humains animés, il faut un **asset 3D custom**. **Ce travail se fait dans
Unity + Blender** (modélisation/rig/anim ou retargeting), PAS en XML/C#. L'agent code ne peut pas
produire de mesh/anim 3D ; il prépare le câblage et les systèmes.

## Approche recommandée : RÉUTILISER les animations du jeu (pas en créer)
Le plus rapide = un **mesh humain riggé sur le squelette humanoïde standard de 7DTD**, puis
**retarget des animations existantes** (Mecanim Humanoid). On évite ainsi de créer des animations.
Deux voies :
1. **Squelette zombie** (rig de combat complet : marche/attaque/mort) + mesh humain "propre" →
   anims fonctionnelles, look humain. Attaques = animations zombie (griffes) sauf travail
   supplémentaire pour les armes.
2. **Framework communautaire SCore** (standard de fait pour les NPC custom 7DTD) : fournit un
   `AvatarController` flexible + EAI pour NPC armés. Beaucoup de mods de bandits s'appuient dessus.
   À évaluer si on veut des pillards armés bien animés sans tout réécrire.

## Pipeline concret (asset → jeu)
1. **Unity 2022.3.62f2** + projet de mod 7DTD (NME / SDK TFP de la même version).
2. Importer le mesh + textures + matériaux. Rigger sur le squelette humanoïde cible (zombie/standard).
3. Configurer l'`Animator`/`Avatar` (Humanoid) ; brancher les états marche/attaque/mort attendus
   par l'`AvatarController` choisi.
4. Créer un **prefab** du personnage (avec colliders, transforms `head/body/hands/feet`).
5. **Builder un AssetBundle** (ex. `bandits.unity3d`) dans `Mods/DeadHotSummer/Resources/`.
6. Référencer dans `entityclasses.xml` (généré) :
   `Mesh="#@modfolder:Resources/bandits.unity3d?dhsBanditMarauder"` (+ `AvatarController` adapté).

## Ce que l'agent (code) prépare en parallèle — SANS bloquer sur l'art
- **Tout AXE 2 reste constructible sur `EntityBandit`** : factions/tiers (J2.1 ✅), camps POI (J2.2),
  réputation (J2.3), patrouilles (J2.4), raids+pillage (J2.5), capture (J2.6). Spawn + IA + pathing
  fonctionnent déjà. Les pillards à distance (pistolet/fusil) **tirent** même sans anim de mêlée.
- Quand l'AssetBundle existe, on remplace juste le `Mesh`/`AvatarController` dans le générateur —
  **plug-in en une ligne par tier**, le reste du gameplay est prêt.

## Décision
Le modèle 3D est un **chantier Unity séparé** (toi / un artiste / un asset communautaire compatible).
En attendant, on continue les **systèmes d'AXE 2** sur `EntityBandit` pour que le gameplay soit prêt
et que l'asset se branche à la fin. Modèle placeholder actuel = prefabs marchand (server-safe).

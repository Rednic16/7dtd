# Guide — Builder le bundle de pillards (modèles + anims tout faits) pour 7DTD V3.0

Objectif : transformer un **modèle 3D humanoïde acheté/téléchargé** + des **animations toutes
faites** en un **AssetBundle** que le mod charge comme pillard animé (marche/attaque/mort).

Cible : **Unity 2022.3.62f2** (impératif, doit matcher le jeu).

---
## 0. Prérequis
- **Unity Hub** + **Unity 2022.3.62f2** installé.
- Le **projet Unity de modding officiel TFP** pour 7DTD (il contient les *Animator Controllers* et le
  squelette du jeu à réutiliser). À défaut, on recrée un Animator Controller avec les paramètres
  listés au §4 — possible mais plus long.
- Ton modèle humanoïde (**FBX**) + ses animations (**FBX** ou clips), de préférence en **Humanoïde**
  (Mecanim) pour le retargeting.

---
## 1. Importer le modèle
1. Crée/ouvre le projet Unity de modding 7DTD (2022.3.62f2).
2. Glisse le **FBX du perso** dans `Assets/`.
3. Sélectionne le FBX → onglet **Rig** → **Animation Type = Humanoid** → **Avatar Definition =
   Create From This Model** → **Apply**. Vérifie le mapping des os (bouton **Configure…**, tout en vert).
4. Échelle : le perso doit faire **~1,85 m** dans la scène (ajuste *Scale Factor* si besoin).

## 2. Importer les animations
1. Glisse les **FBX d'animations** dans `Assets/`.
2. Pour chacun : onglet **Rig → Animation Type = Humanoid**, **Avatar = Copy From Other Avatar** →
   choisis l'avatar de ton perso (créé au §1). **Apply**.
3. Onglet **Animation** : coche **Loop Time** pour les boucles (marche/course/idle). Renomme les clips.
   Il te faut au minimum : **idle, walk, run, attaque(s), hit/réaction, mort**.

## 3. Réutiliser l'Animator du jeu (le plus simple) OU en construire un
- **Voie A (recommandée)** : dans le projet TFP, copie l'**Animator Controller** d'un humanoïde du jeu
  (zombie/standard) sur ton prefab, puis **remplace les clips** par les tiens dans chaque état. Les
  **paramètres sont déjà câblés** → le moteur pilote tout.
- **Voie B (from scratch)** : crée un **Animator Controller** et ajoute EXACTEMENT ces paramètres
  (le moteur les écrit via `AvatarController`) :
  - Float : `Move`, `Forward`, `Strafe`, `TurnRate`, `RotationPitch`, `AimPitch`, `AimYaw`,
    `MeleeAttackSpeed`, `IdleTime`, `WalkTypeBlend`, `AttackBlend`
  - Int : `WalkType`, `MovementState`, `HitBodyPart`, `WeaponCarry`, `SwimSelect`, `ItemUse`
  - Bool : `IsAiming`, `readyToFire`, `AttackReady`
  - Trigger : `Attack`, `AttackStart`, `Death`, `Hit`, `HitStart`, `Jump`, `Stun`, `Dig`,
    `BeginCorpseEat`, `EndCorpseEat`
  - États/transitions minimaux : **Locomotion** (blend tree piloté par `Move`/`Forward`/`Strafe`),
    **Attack** (trigger `Attack`), **Hit** (trigger `Hit`), **Death** (trigger `Death`).

## 4. Structure du prefab
1. Crée un **GameObject racine** (nom = `dhsBanditMarauder`), mets ton mesh dessous.
2. Ajoute un **Animator** sur la racine → **Controller** = celui du §3, **Avatar** = celui du §1.
3. **Socket d'arme** : crée un transform vide `Weapon_Joint` enfant de la **main droite** (pour
   afficher l'arme tenue).
4. **Ragdoll** (mort) : sur les os principaux, ajoute Colliders + Rigidbodies + CharacterJoints
   (menu Unity *GameObject → 3D Object → Ragdoll…* fait le câblage). Sinon collapse simple.
5. **Collider de hit** : un Capsule Collider sur la racine pour recevoir les tirs.
6. Glisse la racine dans `Assets/` → ça crée le **prefab**. Répète/duplique pour
   `dhsBanditMotor`, `dhsBanditMilitia`, `dhsBanditSect` (ou 1 prefab + 4 variantes de matériau).

## 5. Marquer pour l'AssetBundle
1. Sélectionne chaque prefab → en bas de l'Inspector, **AssetBundle** → crée/choisis le tag
   **`bandits`**.
2. (Mets aussi textures/matériaux dans le même tag s'ils ne sont pas auto-inclus.)

## 6. Builder le bundle
Crée `Assets/Editor/BuildBundles.cs` :
```csharp
using UnityEditor;
using System.IO;
public static class BuildBundles
{
    [MenuItem("7DTD/Build AssetBundles")]
    public static void Build()
    {
        string outDir = "Assets/_BuiltBundles";
        Directory.CreateDirectory(outDir);
        BuildPipeline.BuildAssetBundles(outDir,
            BuildAssetBundleOptions.None, BuildTarget.StandaloneLinux64); // Windows: StandaloneWindows64
    }
}
```
Menu **7DTD → Build AssetBundles** → récupère **`bandits`** (renomme en **`bandits.unity3d`**).
> Build pour la **plateforme du SERVEUR** (ici `StandaloneLinux64`). Si client Windows + serveur
> Linux, il faut un bundle par plateforme, ou un bundle compatible. (À valider selon ton hébergement.)

## 7. Installer dans le mod
- Copie `bandits.unity3d` dans `Mods/DeadHotSummer/Resources/`.
- Dis-le moi : je modifie le générateur pour pointer chaque tier vers le prefab :
  `Mesh="#@modfolder:Resources/bandits.unity3d?dhsBanditMarauder"` (+ `AvatarController` adapté à
  ton Animator). C'est **1 ligne par tier** côté code.

## 8. Tester
- Recharge une partie → `spawnentityat dhsBanditMarauder <x> <y> <z>` → vérifie marche/attaque/mort.
- Si figé : l'Animator n'a pas les bons paramètres/états (revois §3) ; envoie-moi le log + ce que tu
  vois, j'aide au diagnostic.

---
### Raccourci à considérer
Si le rig/animator « from scratch » est trop lourd, le mod communautaire **SCore** fournit un
`AvatarController` clé-en-main pour NPC humanoïdes : beaucoup de packs de bandits l'utilisent. On peut
basculer sur cette voie si la voie vanilla coince.

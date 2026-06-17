# Dead Hot Summer — Mod 7 Days to Die (V3.0)

Mod ajoutant deux systèmes majeurs à **7 Days to Die V3.0 « Dead Hot Summer »** :

- **AXE 1 — Classes & spécialisations** : 7 branches × ≥2 sous-branches, compétences communes/exclusives, prérequis croisés, progression multi-classe séquentielle (intégrée aux skill points + magazines natifs).
- **AXE 2 — Pillards humains** : factions territoriales, camps en POI, patrouilles, raids dynamiques sur les bases mal défendues, calibrés sur le gamestage global.

> ⚠️ **EAC doit être désactivé** (`serverconfig.xml` → `EACEnabled="false"`) : le mod embarque une DLL C#/Harmony.

## Structure du dépôt

Ce dépôt **est** un dossier d'installation serveur 7DTD. Seul le mod est versionné (voir `.gitignore`) :

| Chemin | Rôle |
|---|---|
| `Mods/DeadHotSummer/` | Mod déployé (ModInfo, DLL compilée, `Config/` XML) |
| `src/DeadHotSummer/` | Sources C# (projet .NET, Harmony + managers) |
| `docs/` | Documentation d'architecture, équilibrage, tests |

Le reste (jeu, `Data/` vanilla, binaires) est ignoré par git.

## Build

Prérequis : .NET SDK 8. Les DLL du jeu sont référencées localement (non versionnées).

```bash
cd src/DeadHotSummer
dotnet build -c Release
```

La DLL est produite directement dans `Mods/DeadHotSummer/DeadHotSummer.dll`.

## Documentation

Voir [docs/architecture.md](docs/architecture.md).

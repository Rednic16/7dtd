using System.Reflection;
using HarmonyLib;
using UnityEngine.Scripting;

namespace DeadHotSummer
{
    /// <summary>
    /// Point d'entrée du mod (appelé par le jeu via IModApi.InitMod).
    /// Jalon 0 : bootstrap Harmony + abonnement aux ModEvents (stubs pour l'instant).
    /// La logique des AXE 1 / AXE 2 viendra dans des managers dédiés aux jalons suivants.
    /// </summary>
    [Preserve]
    public class ModApi : IModApi
    {
        public const string ModId = "DeadHotSummer";

        public void InitMod(Mod _modInstance)
        {
            ModLog.Out("InitMod — initialisation du mod Dead Hot Summer (V3.0)");

            // 1) Harmony : applique tous les patches [HarmonyPatch] de cet assembly.
            var harmony = new Harmony(ModId);
            harmony.PatchAll(Assembly.GetExecutingAssembly());

            // 2) Hooks ModEvents (handlers = void H(ref SXxxData)).
            ModEvents.GameStartDone.RegisterHandler(OnGameStartDone);
            ModEvents.PlayerSpawnedInWorld.RegisterHandler(OnPlayerSpawnedInWorld);
            // Pas de hook GameUpdate : la logique de classe est ÉVÉNEMENTIELLE
            // (déclenchée par la lecture des livres/magazines via MinEventActionDhsClassEvent),
            // pas de job périodique qui tourne en permanence.

            ModLog.Out("InitMod terminé — Harmony + ModEvents enregistrés");
        }

        private static void OnGameStartDone(ref ModEvents.SGameStartDoneData _data)
        {
            int gs = BanditManager.GlobalGameStage();
            ModLog.Out($"GameStartDone — monde prêt (GS global pillards={gs}, tier={BanditManager.TierForGameStage(gs)})");
            // J2.2+ : CampManager / patrouilles / RaidManager s'appuieront sur BanditManager.
        }

        private static void OnPlayerSpawnedInWorld(ref ModEvents.SPlayerSpawnedInWorldData _data)
        {
            // AXE 1 : au 1er spawn -> ouvre un slot de classe + réconcilie les livres.
            ClassManager.OnPlayerSpawned(_data.EntityId);
        }
    }
}

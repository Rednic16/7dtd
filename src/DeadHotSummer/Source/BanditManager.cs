using System.Collections.Generic;
using UnityEngine.Scripting;

namespace DeadHotSummer
{
    /// <summary>
    /// AXE 2 — fondations des pillards (J2.1).
    ///
    /// Les pillards évoluent avec le GAMESTAGE GLOBAL (cumul des joueurs en ligne) : plus le
    /// monde progresse, plus le tier (équipement) et l'effectif des camps/embuscades/raids montent.
    ///   tier 0 = Maraudeur, 1 = Bande motorisée, 2 = Milice, 3 = Secte.
    /// Chaque tier a sa faction (toutes mutuellement hostiles + hostiles aux joueurs et zombies).
    ///
    /// Ce manager ne fait pour l'instant QUE fournir le calcul de tier (utilisé par les jalons
    /// suivants : camps J2.2, patrouilles J2.4, raids J2.5). Aucun job par frame.
    /// </summary>
    [Preserve]
    public static class BanditManager
    {
        // Seuils de GS global -> tier de base (réglables ; passeront en XML à l'équilibrage J2.7).
        private static readonly int[] TierThresholds = { 0, 30, 80, 160 };

        // Entités générées (cf BANDIT_TIERS dans le générateur).
        public static readonly string[] TierEntity =
            { "dhsBanditMarauder", "dhsBanditMotor", "dhsBanditMilitia", "dhsBanditSect" };

        public const int MaxTier = 3;

        /// <summary>GS global = CalcPartyLevel (somme à rendements décroissants) des joueurs vivants en ligne.</summary>
        public static int GlobalGameStage()
        {
            World world = GameManager.Instance?.World;
            if (world == null) return 0;
            List<int> stages = new List<int>();
            foreach (EntityPlayer p in world.Players.list)
                if (p != null && p.IsAlive())
                    stages.Add(p.gameStage);
            if (stages.Count == 0) return 0;
            return GameStageDefinition.CalcPartyLevel(stages);
        }

        /// <summary>Tier de pillard pour un GS donné, + offset de biome (biome dur = +1 tier).</summary>
        public static int TierForGameStage(int gameStage, int biomeOffset = 0)
        {
            int tier = 0;
            for (int i = 0; i < TierThresholds.Length; i++)
                if (gameStage >= TierThresholds[i]) tier = i;
            return Clamp(tier + biomeOffset);
        }

        /// <summary>Tier courant à partir du GS global (sans offset).</summary>
        public static int CurrentTier() => TierForGameStage(GlobalGameStage());

        public static string EntityForTier(int tier) => TierEntity[Clamp(tier)];

        private static int Clamp(int t) => t < 0 ? 0 : (t > MaxTier ? MaxTier : t);
    }
}

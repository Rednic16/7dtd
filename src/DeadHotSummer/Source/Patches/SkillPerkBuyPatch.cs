using HarmonyLib;
using UnityEngine.Scripting;

namespace DeadHotSummer
{
    /// <summary>
    /// AXE 1 — Pool de points de classe STRICT.
    ///
    /// Les magazines de classe octroient des "points de classe" (cvar dhsPts&lt;code&gt;, via
    /// ModifyCVar en XML). Ces points ne sont dépensables que dans les perks de LA classe
    /// concernée. Le bouton d'achat vanilla n'est PAS grisé par les points (il l'est seulement
    /// par le palier de niveau) ; seul btnBuy_OnPress vérifie le coût en points de niveau.
    ///
    /// On intercepte donc btnBuy_OnPress : pour un perk de classe, si le joueur a assez de
    /// points de classe, on "avance" le coût sur le pool de niveau (que vanilla déduit juste
    /// après) et on décompte le pool de classe. Net : pool de niveau inchangé, point de classe
    /// consommé. Les points de classe (restreints) sont dépensés EN PRIORITÉ ; sinon vanilla
    /// utilise les points de niveau. Le palier reste géré par les level_requirements.
    ///
    /// NB: logique côté client (UI). Correct en solo / hôte. Voir docs pour la persistance MP.
    /// </summary>
    [Preserve]
    [HarmonyPatch(typeof(XUiC_SkillPerkLevel), "btnBuy_OnPress")]
    public static class SkillPerkBuyPatch
    {
        [Preserve]
        public static void Prefix(XUiC_SkillPerkLevel __instance)
        {
            try
            {
                ProgressionValue skill = __instance.CurrentSkill;
                if (skill == null || skill.ProgressionClass == null) return;
                string code = ClassManager.CodeFromPerkName(skill.ProgressionClass.Name);
                if (code == null) return; // pas un perk de classe -> vanilla (points de niveau)

                EntityPlayerLocal player = __instance.xui?.playerUI?.entityPlayer;
                if (player == null || player.Buffs == null) return;

                int level = __instance.Level;
                int cost = skill.ProgressionClass.CalculatedCostForLevel(level);
                // On n'intervient que si l'achat RÉUSSIRA (miroir du garde vanilla, sans le test points).
                if (cost <= 0) return;
                if (skill.Level + 1 != level) return;
                if (skill.CalculatedMaxLevel(player) < level) return;
                if (!skill.CanPurchase(player, level)) return;

                // Priorité aux points de classe (restreints) sur les points de niveau (flexibles).
                float pts = player.Buffs.GetCustomVar("dhsPts" + code);
                if (pts >= cost)
                {
                    player.Progression.SkillPoints += cost;                 // avance le coût
                    player.Buffs.SetCustomVar("dhsPts" + code, pts - cost); // consomme le pool de classe
                    // vanilla déduit ensuite 'cost' du pool de niveau -> net niveau inchangé.
                }
                // sinon : pas assez de points de classe -> vanilla tentera les points de niveau.
            }
            catch (System.Exception e)
            {
                ModLog.Error("SkillPerkBuyPatch.Prefix: " + e.Message);
            }
        }
    }

    /// <summary>
    /// AXE 1 — Indicateur UI : ajoute "Points &lt;classe&gt; : N" à l'infobulle d'achat d'un
    /// perk de classe, pour que le joueur voie son pool de points de classe au moment d'acheter.
    /// </summary>
    [Preserve]
    [HarmonyPatch(typeof(XUiC_SkillPerkLevel), "GetBindingValueInternal")]
    public static class SkillPerkTooltipPatch
    {
        [Preserve]
        public static void Postfix(XUiC_SkillPerkLevel __instance, ref string _value, string _bindingName, bool __result)
        {
            try
            {
                if (!__result || _bindingName != "buytooltip") return;
                ProgressionValue skill = __instance.CurrentSkill;
                if (skill == null || skill.ProgressionClass == null) return;
                string code = ClassManager.CodeFromPerkName(skill.ProgressionClass.Name);
                if (code == null) return;
                EntityPlayerLocal player = __instance.xui?.playerUI?.entityPlayer;
                if (player == null || player.Buffs == null) return;

                int pts = (int)player.Buffs.GetCustomVar("dhsPts" + code);
                string label = Localization.Get("dhsClassPointsLabel");
                if (string.IsNullOrEmpty(label) || label == "dhsClassPointsLabel") label = "Class points";
                if (!string.IsNullOrEmpty(_value)) _value += "\n";
                _value += label + ": " + pts;
            }
            catch (System.Exception e)
            {
                ModLog.Error("SkillPerkTooltipPatch.Postfix: " + e.Message);
            }
        }
    }
}

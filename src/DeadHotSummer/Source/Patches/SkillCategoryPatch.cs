using System.Collections.Generic;
using HarmonyLib;
using UnityEngine.Scripting;

namespace DeadHotSummer
{
    /// <summary>
    /// AXE 1 — Masque les catégories d'attributs vanilla dans la fenêtre Compétences.
    ///
    /// Vanilla : XUiC_CategoryList.SetupCategoriesByWorkstation("skills") liste TOUS les
    /// attributs (IsAttribute) sans tenir compte de leur drapeau Hidden. On remplace cette
    /// branche pour ne laisser visibles QUE nos onglets de classe (attClass*) : les 5 attributs
    /// vanilla ET l'onglet "Compétences d'artisanat" (attCrafting) sont masqués. Les
    /// crafting_skills vanilla continuent de progresser via les magazines de butin (filet de
    /// sécurité) -> rien ne devient incraftable ; les crafts sans classe propre (armures,
    /// établis, mods, matériaux) sont en plus rattachés à la classe commune Survivant.
    /// </summary>
    [Preserve]
    [HarmonyPatch(typeof(XUiC_CategoryList), "SetupCategoriesByWorkstation")]
    public static class SkillCategoryPatch
    {
        [Preserve]
        public static bool Prefix(XUiC_CategoryList __instance, string _workstation, ref bool __result)
        {
            // On ne touche qu'à la vue "skills" ; le reste (crafting, trader…) suit la logique vanilla.
            if (_workstation != "skills")
            {
                return true;
            }
            // Même court-circuit que l'original (déjà configuré pour ce workstation).
            if (__instance.currentWorkstation == _workstation)
            {
                __result = false;
                return false;
            }
            __instance.currentWorkstation = _workstation;

            int num = 0;
            foreach (KeyValuePair<string, ProgressionClass> kvp in Progression.ProgressionClasses)
            {
                ProgressionClass pc = kvp.Value;
                if (!pc.IsAttribute) continue;
                // Allowlist : on n'affiche QUE nos catégories de classe (attClass*). Tout le reste
                // (5 attributs vanilla, attCrafting/Artisanat, General, Books) est masqué de la
                // fenêtre. NB: ProgressionClass.Name est en minuscules côté moteur.
                bool show = pc.Name != null && pc.Name.StartsWith("attclass");
                if (!show) continue;
                if (num >= __instance.CategoryButtons.Count) break; // sécurité (jamais hors slots)
                __instance.SetCategoryEntry(num, pc.Name, pc.Icon, Localization.Get(pc.Name));
                num++;
            }
            for (int j = num; j < __instance.CategoryButtons.Count; j++)
            {
                __instance.SetCategoryEmpty(j);
            }

            __result = true;
            return false; // on remplace l'implémentation vanilla pour "skills"
        }
    }
}

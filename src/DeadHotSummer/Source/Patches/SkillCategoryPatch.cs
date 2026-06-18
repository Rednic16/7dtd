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
    /// branche pour SAUTER les attributs marqués Hidden (les 5 attributs vanilla + General,
    /// mis en hidden via progression.xml), ne laissant visibles que notre catégorie "Classes"
    /// (attClasses) + Books + Crafting. Les perks vanilla restent définis (auto-accordés par
    /// ClassManager) pour ne pas casser le craft.
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
                if (!pc.IsAttribute || pc.Hidden)
                {
                    continue; // saute les attributs vanilla masqués
                }
                if (!XUiM_Recipes.CraftingProgression && pc.Name == "attcrafting")
                {
                    continue;
                }
                if (num >= __instance.CategoryButtons.Count)
                {
                    break; // sécurité : ne jamais dépasser le nombre de slots
                }
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

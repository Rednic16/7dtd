using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Scripting;

namespace DeadHotSummer
{
    /// <summary>
    /// AXE 1 — gestion serveur des classes :
    ///  - J1.6 : au tout premier spawn, ouvre un slot de classe (dhsClassSlotFree=1) et remet
    ///           les 14 livres de classe au joueur (il en lit un pour choisir sa voie).
    ///  - J1.7 : détection périodique de complétion (tous les perks exclusifs d'une sous-classe
    ///           au max) -> débloque la sous-classe sœur + un nouveau slot (séquentiel entre branches).
    /// CVars joueur via player.Buffs (persistants, sync client). Voir docs/axe1.md.
    /// </summary>
    [Preserve]
    public static class ClassManager
    {
        private const string CvInit = "dhsInit";
        private const string CvSlotFree = "dhsClassSlotFree";
        private const string CvDoneCount = "dhsClassDoneCount";
        private const string CvBooksOut = "dhsBooksOut"; // 1 = les livres de choix sont en circulation
        private const float CheckIntervalSec = 10f;

        // 14 sous-classes : code -> sous-classe sœur (même branche principale).
        private static readonly (string code, string sibling)[] Classes =
        {
            ("EngiMech","EngiElec"), ("EngiElec","EngiMech"),
            ("MedicSurg","MedicChem"), ("MedicChem","MedicSurg"),
            ("SoldSnip","SoldAslt"), ("SoldAslt","SoldSnip"),
            ("SurvHunt","SurvHerb"), ("SurvHerb","SurvHunt"),
            ("BuilArch","BuilArti"), ("BuilArti","BuilArch"),
            ("ScoutTrac","ScoutInfi"), ("ScoutInfi","ScoutTrac"),
            ("FarmAgri","FarmCook"), ("FarmCook","FarmAgri"),
        };

        private static float nextCheck;

        // ---- Premier spawn : init slot + réconciliation des livres ----
        public static void OnPlayerSpawned(int entityId)
        {
            World world = GameManager.Instance?.World;
            if (world == null) return;
            if (!(world.GetEntity(entityId) is EntityPlayer player)) return;

            if (player.Buffs.GetCustomVar(CvInit) < 1f)
            {
                player.Buffs.SetCustomVar(CvInit, 1f);
                player.Buffs.SetCustomVar(CvSlotFree, 1f);
                ModLog.Out($"Joueur {entityId}: 1er spawn -> slot de classe ouvert");
            }
            ReconcileBooks(player);
        }

        // Slot libre -> les livres de choix sont disponibles ; slot consommé -> on supprime
        // les livres restants (inutilisables). Idempotent via le cvar dhsBooksOut.
        private static void ReconcileBooks(EntityPlayer player)
        {
            if (player == null || player.Buffs == null || player.bag == null) return;
            bool slotFree = player.Buffs.GetCustomVar(CvSlotFree) >= 1f;
            bool booksOut = player.Buffs.GetCustomVar(CvBooksOut) >= 1f;
            if (slotFree && !booksOut)
            {
                GiveClassBooks(player);
                player.Buffs.SetCustomVar(CvBooksOut, 1f);
            }
            else if (!slotFree && booksOut)
            {
                RemoveClassBooks(player);
                player.Buffs.SetCustomVar(CvBooksOut, 0f);
                ModLog.Out($"Joueur {player.entityId}: livres de classe inutilisables supprimés");
            }
        }

        private static void GiveClassBooks(EntityPlayer player)
        {
            GameManager gm = GameManager.Instance;
            if (gm == null) return;
            foreach ((string code, string _) in Classes)
            {
                if (player.Buffs.GetCustomVar("dhsCls" + code) >= 1f) continue; // classe déjà débloquée
                ItemValue iv = ItemClass.GetItem("dhsBookClass" + code);
                if (iv == null || iv.IsEmpty()) continue;
                gm.ItemDropServer(new ItemStack(iv, 1), player.position, new Vector3(0.6f, 0.3f, 0.6f), player.entityId, 300f);
            }
        }

        private static void RemoveClassBooks(EntityPlayer player)
        {
            foreach ((string code, string _) in Classes)
            {
                ItemValue iv = ItemClass.GetItem("dhsBookClass" + code);
                if (iv == null || iv.IsEmpty()) continue;
                player.bag.DecItem(iv, 999);
            }
        }

        // ---- Tick throttlé : détection de complétion pour les joueurs en ligne ----
        public static void OnGameUpdate()
        {
            if (Time.time < nextCheck) return;
            nextCheck = Time.time + CheckIntervalSec;

            World world = GameManager.Instance?.World;
            if (world == null) return;
            List<EntityPlayer> players = world.Players.list;
            for (int i = 0; i < players.Count; i++)
            {
                CheckCompletion(players[i]);
                ReconcileBooks(players[i]); // donne/supprime les livres selon l'état du slot
            }
        }

        private static void CheckCompletion(EntityPlayer player)
        {
            if (player == null || player.Buffs == null) return;
            foreach ((string code, string sibling) in Classes)
            {
                if (player.Buffs.GetCustomVar("dhsCls" + code) < 1f) continue;          // pas cette classe
                if (player.Buffs.GetCustomVar("dhsCls" + code + "Done") >= 1f) continue; // déjà complétée
                if (!AllPerksMaxed(player, code)) continue;

                player.Buffs.SetCustomVar("dhsCls" + code + "Done", 1f);
                player.Buffs.SetCustomVar("dhsCls" + sibling, 1f);   // débloque la sœur (perks + magazines)
                player.Buffs.SetCustomVar(CvSlotFree, 1f);           // autorise une sous-classe d'une autre branche
                player.Buffs.SetCustomVar(CvDoneCount, player.Buffs.GetCustomVar(CvDoneCount) + 1f);
                ModLog.Out($"Joueur {player.entityId}: classe {code} complétée -> sœur {sibling} débloquée + slot libre");
            }
        }

        private static bool AllPerksMaxed(EntityPlayer player, string code)
        {
            string skill = "skillClass" + code;
            bool any = false;
            foreach (KeyValuePair<string, ProgressionClass> kvp in Progression.ProgressionClasses)
            {
                ProgressionClass pc = kvp.Value;
                if (pc.ParentName != skill) continue;
                any = true;
                ProgressionValue pv = player.Progression.GetProgressionValue(pc.Name);
                if (pv == null || pv.Level < pc.MaxLevel) return false;
            }
            return any;
        }
    }
}

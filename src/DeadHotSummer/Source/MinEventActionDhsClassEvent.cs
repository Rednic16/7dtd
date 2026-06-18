using UnityEngine.Scripting;

namespace DeadHotSummer
{
    /// <summary>
    /// AXE 1 — action de triggered_effect (événementielle) déclenchée DIRECTEMENT au moment où
    /// le joueur lit un livre/magazine de classe (sur la chaîne de l'action, pas via un poll).
    ///
    /// Référencée en XML par nom assembly-qualifié :
    ///   action="DeadHotSummer.MinEventActionDhsClassEvent, DeadHotSummer"
    /// Résolution : MinEventActionBase.ParseAction -> ReflectionHelpers.GetTypeWithPrefix échoue
    /// sur le préfixe puis retombe sur Type.GetType(nom) qui résout notre type.
    ///
    /// Effet : réconcilie les livres (supprime les inutilisables / redonne si slot libre) et
    /// vérifie la complétion de classe — instantanément à la sélection/lecture, sans job permanent.
    /// </summary>
    [Preserve]
    public class MinEventActionDhsClassEvent : MinEventActionBase
    {
        public override void Execute(MinEventParams _params)
        {
            if (_params != null && _params.Self is EntityPlayer player)
            {
                ClassManager.OnClassEvent(player);
            }
        }
    }
}

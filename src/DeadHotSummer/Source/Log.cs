namespace DeadHotSummer
{
    /// <summary>
    /// Wrapper de logging préfixé pour repérer facilement nos lignes dans output_log.
    /// </summary>
    internal static class ModLog
    {
        private const string Prefix = "[DHS] ";

        public static void Out(string msg) => global::Log.Out(Prefix + msg);
        public static void Warning(string msg) => global::Log.Warning(Prefix + msg);
        public static void Error(string msg) => global::Log.Error(Prefix + msg);
    }
}

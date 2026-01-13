using LCARSFramework.Theme;
using System.Data;
using System.Windows.Media;
using System.Collections.Generic;

namespace LCARSFramework.LCARS.Theme
{
    public static class ThemeManager
    {
        private static Color[] GetOrFallback<TKey>(Dictionary<TKey, Color[]> dict, TKey key, Color[] fallback) where TKey : notnull
        {
            if (dict == null) return fallback;
            return dict.TryGetValue(key, out var cols) ? cols : fallback;
        }

        public static Color[] GetColors(Faction faction, Era? era = null, Role? role = null)
        {
            // safe default
            var defaultFed = LCARSPalette.Federation[Era.Era24];

            return faction switch
            {
                Faction.Federation => GetOrFallback(LCARSPalette.Federation, era ?? Era.Era24, defaultFed),
                Faction.Romulan => GetOrFallback(LCARSPalette.Romulan, role ?? Role.Tactical, defaultFed),
                Faction.Klingon => GetOrFallback(LCARSPalette.Klingon, role ?? Role.Command, defaultFed),
                Faction.Cardassian => GetOrFallback(LCARSPalette.CardassianEra, era ?? Era.Era24, defaultFed),
                _ => defaultFed
            };
        }

        public static SolidColorBrush Brush(Color c) => new SolidColorBrush(c);
    }
}

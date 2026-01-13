using LCARSFramework.Theme;
using System.Collections.Generic;
using System.Data;
using System.Windows.Media;

namespace LCARSFramework.LCARS.Theme
{
    public static class LCARSPalette
    {
        private static Color H(string hex) => (Color)ColorConverter.ConvertFromString(hex);

        public static readonly Dictionary<LCARSFramework.Theme.Era, Color[]> Federation = new()
        {
            { LCARSFramework.Theme.Era.Era22, new[] { H("#607D8B"), H("#90A4AE"), H("#B0BEC5"), H("#263238"), H("#CFD8DC"), H("#FFB300") } },
            { LCARSFramework.Theme.Era.Era23, new[] { H("#FFB300"), H("#1976D2"), H("#388E3C"), H("#E53935"), H("#FBC02D"), H("#212121") } },
            { LCARSFramework.Theme.Era.Era24, new[] { H("#FF9900"), H("#663399"), H("#3399FF"), H("#33CCFF"), H("#FF33CC"), H("#111111") } },
            { LCARSFramework.Theme.Era.Era25, new[] { H("#FFC107"), H("#7E57C2"), H("#29B6F6"), H("#26C6DA"), H("#00ACC1"), H("#0B0B0B") } },
            { LCARSFramework.Theme.Era.Era26, new[] { H("#FFA000"), H("#8E24AA"), H("#1E88E5"), H("#00ACC1"), H("#00E5FF"), H("#0A0A0A") } },
            { LCARSFramework.Theme.Era.Era27, new[] { H("#FF8F00"), H("#6A1B9A"), H("#1565C0"), H("#00B8D4"), H("#00C853"), H("#090909") } },
            { LCARSFramework.Theme.Era.Era28, new[] { H("#FFE082"), H("#8E44AD"), H("#2E86C1"), H("#17A589"), H("#F4F6F7"), H("#000000") } },
            { LCARSFramework.Theme.Era.Era29, new[] { H("#FFD54F"), H("#9B59B6"), H("#3498DB"), H("#16A085"), H("#ECF0F1"), H("#000000") } },
            { LCARSFramework.Theme.Era.Era30, new[] { H("#FFD180"), H("#A569BD"), H("#5DADE2"), H("#1ABC9C"), H("#FDFEFE"), H("#000000") } },
        };

        // Romulan palettes kept per Role (interface-focused shapes), but also provide era fallback
        public static readonly Dictionary<LCARSFramework.Theme.Role, Color[]> Romulan = new()
        {
            { LCARSFramework.Theme.Role.Tactical,  new[] { H("#00CC66"), H("#006633"), H("#00994D"), H("#00B377"), H("#1ABC9C"), H("#0B0B0B") } },
            { LCARSFramework.Theme.Role.Stealth,   new[] { H("#333333"), H("#222222"), H("#444444"), H("#555555"), H("#666666"), H("#00CC66") } },
            { LCARSFramework.Theme.Role.Interface, new[] { H("#99CC99"), H("#66AA88"), H("#88CCAA"), H("#77BBA0"), H("#557766"), H("#111111") } },
        };

        // Klingon palettes kept per Role but also provide era fallback if needed
        public static readonly Dictionary<LCARSFramework.Theme.Role, Color[]> Klingon = new()
        {
            { LCARSFramework.Theme.Role.Command,   new[] { H("#B71C1C"), H("#D32F2F"), H("#FFA000"), H("#4E342E"), H("#E53935"), H("#0B0B0B") } },
            { LCARSFramework.Theme.Role.Tactical,  new[] { H("#8D6E63"), H("#6D4C41"), H("#BF360C"), H("#D84315"), H("#795548"), H("#121212") } },
            { LCARSFramework.Theme.Role.Interface, new[] { H("#9E9E9E"), H("#757575"), H("#616161"), H("#424242"), H("#FF6F00"), H("#000000") } },
        };

        // Cardassian: provide era-based palettes (Cardassian look varies by era)
        public static readonly Dictionary<LCARSFramework.Theme.Era, Color[]> CardassianEra = new()
        {
            { LCARSFramework.Theme.Era.Era22, new[] { H("#5D4037"), H("#8D6E63"), H("#A1887F"), H("#3E2723"), H("#BCAAA4"), H("#252525") } },
            { LCARSFramework.Theme.Era.Era23, new[] { H("#6A1B9A"), H("#8E24AA"), H("#9575CD"), H("#4A148C"), H("#CE93D8"), H("#111111") } },
            { LCARSFramework.Theme.Era.Era24, new[] { H("#4E342E"), H("#6D4C41"), H("#8D6E63"), H("#3E2723"), H("#D7CCC8"), H("#000000") } },
            { LCARSFramework.Theme.Era.Era25, new[] { H("#3E2723"), H("#5D4037"), H("#795548"), H("#2E1B17"), H("#BCAAA4"), H("#0B0B0B") } },
            { LCARSFramework.Theme.Era.Era26, new[] { H("#6D4C41"), H("#4E342E"), H("#3E2723"), H("#2B1B17"), H("#A1887F"), H("#090909") } },
            { LCARSFramework.Theme.Era.Era27, new[] { H("#7B1E3A"), H("#880E4F"), H("#AD1457"), H("#4C0F23"), H("#EF9A9A"), H("#070707") } },
            { LCARSFramework.Theme.Era.Era28, new[] { H("#8D6E63"), H("#A1887F"), H("#D7CCC8"), H("#5D4037"), H("#FFFFFF"), H("#000000") } },
            { LCARSFramework.Theme.Era.Era29, new[] { H("#6A1B9A"), H("#4527A0"), H("#283593"), H("#1A237E"), H("#C5CAE9"), H("#000000") } },
            { LCARSFramework.Theme.Era.Era30, new[] { H("#4A148C"), H("#6A1B9A"), H("#8E24AA"), H("#311B92"), H("#E1BEE7"), H("#000000") } },
        };

        // Keep original role-based Cardassian mapping for compatibility (optional)
        public static readonly Dictionary<LCARSFramework.Theme.Role, Color[]> Cardassian = new()
        {
            { LCARSFramework.Theme.Role.Ops,       new[] { H("#BDBDBD"), H("#9E9E9E"), H("#757575"), H("#424242"), H("#FBC02D"), H("#0A0A0A") } },
            { LCARSFramework.Theme.Role.Security,  new[] { H("#9FA8A3"), H("#6D7275"), H("#41464B"), H("#212529"), H("#C0A96E"), H("#000000") } },
            { LCARSFramework.Theme.Role.Interface, new[] { H("#C5C6C7"), H("#8D8E90"), H("#5B5C5E"), H("#2E3033"), H("#E0C085"), H("#0B0B0B") } },
        };
    }
}

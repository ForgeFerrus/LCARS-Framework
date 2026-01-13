using System.Windows;
using System.Windows.Media;
using LCARSFramework.Theme;

namespace LCARSFramework.LCARS.Theme
{
    public static class ThemeApplier
    {
        // Apply primary palette colors into application resources for dynamic UI updates
        public static void ApplyTheme(Faction faction, Era era)
        {
            var colors = ThemeManager.GetColors(faction, era);
            if (colors == null || colors.Length == 0) return;

            // Primary, secondary
            var primary = new SolidColorBrush(colors[0]);
            var secondary = new SolidColorBrush(colors.Length > 1 ? colors[1] : colors[0]);
            var accent = new SolidColorBrush(colors[^1]);

            Application.Current.Resources["LCARS.Orange"] = primary;
            Application.Current.Resources["LCARS.Purple"] = secondary;
            Application.Current.Resources["LCARS.Accent"] = accent;

            // Update gradient used by buttons
            var g = new LinearGradientBrush();
            g.StartPoint = new System.Windows.Point(0, 0);
            g.EndPoint = new System.Windows.Point(0, 1);
            g.GradientStops.Add(new GradientStop(colors[0], 0));
            var mid = colors.Length > 2 ? colors[2] : colors[0];
            g.GradientStops.Add(new GradientStop(mid, 0.6));
            g.GradientStops.Add(new GradientStop(colors[^1], 1));
            Application.Current.Resources["LCARS.ButtonGradient"] = g;
        }
    }
}
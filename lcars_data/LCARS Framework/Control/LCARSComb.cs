using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using LCARSFramework.Theme;

namespace LCARSFramework.Control
{
    public partial class LCARSComb : UserControl
    {
        public LCARSComb()
        {
            InitializeComponent();
        }

        public static readonly DependencyProperty FactionProperty =
            DependencyProperty.Register(nameof(Faction), typeof(Faction), typeof(LCARSComb), new PropertyMetadata(Faction.Romulan, OnThemeChanged));

        public Faction Faction
        {
            get => (Faction)GetValue(FactionProperty);
            set => SetValue(FactionProperty, value);
        }

        public static readonly DependencyProperty RoleProperty =
            DependencyProperty.Register(nameof(Role), typeof(Role), typeof(LCARSComb), new PropertyMetadata(Role.Interface, OnThemeChanged));

        public Role Role
        {
            get => (Role)GetValue(RoleProperty);
            set => SetValue(RoleProperty, value);
        }

        private static void OnThemeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is LCARSComb c) c.UpdateTheme();
        }

        private void UpdateTheme()
        {
            var colors = LCARSFramework.LCARS.Theme.ThemeManager.GetColors(Faction, null, Role);
            CombBorder.Background = new SolidColorBrush(colors[1]);
            CombBorder.BorderBrush = new SolidColorBrush(colors[^1]);
            CombLabel.Text = $"{Faction} {Role}";
        }
    }
}
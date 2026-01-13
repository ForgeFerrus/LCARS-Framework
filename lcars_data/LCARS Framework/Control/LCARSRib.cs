using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using LCARSFramework.Theme;

namespace LCARSFramework.Control
{
    public partial class LCARSRib : UserControl
    {
        public LCARSRib()
        {
            InitializeComponent();
        }

        public static readonly DependencyProperty FactionProperty =
            DependencyProperty.Register(nameof(Faction), typeof(Faction), typeof(LCARSRib), new PropertyMetadata(Faction.Klingon, OnThemeChanged));

        public Faction Faction
        {
            get => (Faction)GetValue(FactionProperty);
            set => SetValue(FactionProperty, value);
        }

        public static readonly DependencyProperty RoleProperty =
            DependencyProperty.Register(nameof(Role), typeof(Role), typeof(LCARSRib), new PropertyMetadata(Role.Tactical, OnThemeChanged));

        public Role Role
        {
            get => (Role)GetValue(RoleProperty);
            set => SetValue(RoleProperty, value);
        }

        private static void OnThemeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is LCARSRib r) r.UpdateTheme();
        }

        private void UpdateTheme()
        {
            var colors = LCARSFramework.LCARS.Theme.ThemeManager.GetColors(Faction, null, Role);
            RibBorder.Background = new SolidColorBrush(colors[1]);
            RibBorder.BorderBrush = new SolidColorBrush(colors[^1]);
            RibLabel.Text = $"{Faction}\n{Role}";
        }
    }
}
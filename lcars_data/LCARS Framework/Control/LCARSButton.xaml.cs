using LCARSFramework.LCARS.Theme;
using LCARSFramework.Theme;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.ComponentModel;
using System.Windows.Media.Animation;

namespace LCARSFramework.Control
{
    public partial class LCARSButton : UserControl
    {
        private readonly ScaleTransform _scale = new ScaleTransform(1,1);

        public LCARSButton()
        {
            InitializeComponent();
            // Don't run theme logic in the XAML designer to avoid design-time exceptions
            if (!DesignerProperties.GetIsInDesignMode(this))
                UpdateTheme();

            // apply transform for simple animations
            ButtonBorder.RenderTransformOrigin = new Point(0.5, 0.5);
            ButtonBorder.RenderTransform = _scale;
        }

        public static readonly DependencyProperty LabelProperty =
            DependencyProperty.Register(nameof(Label), typeof(string), typeof(LCARSButton),
                new PropertyMetadata("BUTTON"));

        public string Label
        {
            get => (string)GetValue(LabelProperty);
            set => SetValue(LabelProperty, value);
        }

        public static readonly DependencyProperty FactionProperty =
            DependencyProperty.Register(nameof(Faction), typeof(Faction), typeof(LCARSButton),
                new PropertyMetadata(Faction.Federation, OnThemeChanged));

        public Faction Faction
        {
            get => (Faction)GetValue(FactionProperty);
            set => SetValue(FactionProperty, value);
        }

        public static readonly DependencyProperty EraProperty =
            DependencyProperty.Register(nameof(Era), typeof(Era), typeof(LCARSButton),
                new PropertyMetadata(Era.Era24, OnThemeChanged));

        public Era Era
        {
            get => (Era)GetValue(EraProperty);
            set => SetValue(EraProperty, value);
        }

        private static void OnThemeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is LCARSButton b && !DesignerProperties.GetIsInDesignMode(b)) b.UpdateTheme();
        }

        private void UpdateTheme()
        {
            try
            {
                var colors = ThemeManager.GetColors(Faction, Era);
                if (colors != null && colors.Length > 0)
                {
                    ButtonBorder.Background = new SolidColorBrush(colors[0]);
                    ButtonBorder.BorderBrush = new SolidColorBrush(colors[^1]);
                }
            }
            catch
            {
                // swallow design-time or palette errors to avoid breaking the designer
            }
        }

        private void InnerButton_Click(object sender, RoutedEventArgs e)
        {
            // Raise a routed click event so parent can handle
            var args = new RoutedEventArgs(ButtonClickEvent, this);
            RaiseEvent(args);
        }

        // Expose a routed event for click
        public static readonly RoutedEvent ButtonClickEvent = EventManager.RegisterRoutedEvent(
            "Click", RoutingStrategy.Bubble, typeof(RoutedEventHandler), typeof(LCARSButton));

        public event RoutedEventHandler Click
        {
            add => AddHandler(ButtonClickEvent, value);
            remove => RemoveHandler(ButtonClickEvent, value);
        }

        // animations
        private void AnimateScale(double to)
        {
            var da = new DoubleAnimation(to, TimeSpan.FromMilliseconds(120)) { EasingFunction = new QuadraticEase() };
            _scale.BeginAnimation(ScaleTransform.ScaleXProperty, da);
            _scale.BeginAnimation(ScaleTransform.ScaleYProperty, da);
        }

        private void InnerButton_PreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            ButtonBorder.Opacity = 0.85;
            AnimateScale(0.96);
        }

        private void InnerButton_PreviewMouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            ButtonBorder.Opacity = 1.0;
            AnimateScale(1.0);
        }

        private void InnerButton_MouseEnter(object sender, MouseEventArgs e)
        {
            ButtonBorder.Effect = new System.Windows.Media.Effects.DropShadowEffect { Color = Colors.Black, BlurRadius = 10, ShadowDepth = 0 };
            AnimateScale(1.03);
        }

        private void InnerButton_MouseLeave(object sender, MouseEventArgs e)
        {
            ButtonBorder.Effect = null;
            AnimateScale(1.0);
        }
    }
}

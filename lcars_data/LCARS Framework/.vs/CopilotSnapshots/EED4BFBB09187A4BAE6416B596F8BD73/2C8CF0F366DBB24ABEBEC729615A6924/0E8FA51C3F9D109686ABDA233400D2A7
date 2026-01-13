using LCARSFramework.Control;
using LCARSFramework.Theme;
using System.Data;
using System.Windows;
using System.Windows.Controls;

namespace LCARSWorkbench
{
    public partial class MainWindow : Window
    {
        private Faction _currentFaction = Faction.Federation;
        private Era _currentEra = Era.Era24;

        public MainWindow()
        {
            InitializeComponent();

            // Initialize preview with defaults
            UpdateAllControls();

            // Wire activate button to LCARS modal
            ActivateButton.Click += OnActivate;
        }

        private void OnActivate(object sender, RoutedEventArgs e)
        {
            // Use LCARS modal instead of MessageBox
            var modal = new LCARSModalWindow { Owner = this };
            modal.TitleText = "ACTIVATE";
            modal.MessageText = $"Activated: {_currentFaction} / {_currentEra}";
            modal.ShowDialog();
        }

        private void FactionButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is LCARSButton b && System.Enum.TryParse<Faction>(b.Label, out var f))
            {
                _currentFaction = f;
                UpdateAllControls();
            }
        }

        private void EraButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is LCARSButton b && System.Enum.TryParse<Era>(b.Label, out var era))
            {
                _currentEra = era;
                UpdateAllControls();
            }
        }

        private void UpdateAllControls()
        {
            // Apply theme globally
            LCARSFramework.LCARS.Theme.ThemeApplier.ApplyTheme(_currentFaction, _currentEra);

            ActivateButton.Faction = _currentFaction;
            ActivateButton.Era = _currentEra;

            SamplePanel.Faction = _currentFaction;
            SamplePanel.Era = _currentEra;

            // For rib/comb roles use defaults
            SampleRib.Faction = _currentFaction;
            SampleRib.Role = Role.Tactical;

            SampleComb.Faction = _currentFaction;
            SampleComb.Role = Role.Interface;

            PreviewMenu.RenderPreview(_currentFaction, _currentEra);
        }

        private void OnOpenLauncher(object sender, RoutedEventArgs e)
        {
            var dlg = new LauncherWindow();
            if (dlg.ShowDialog() == true)
            {
                _currentFaction = dlg.SelectedFaction;
                _currentEra = dlg.SelectedEra;
                UpdateAllControls();
            }
        }
    }
}
using System.Configuration;
using System.Data;
using System.Windows;

namespace LCARSFramework
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Open the launcher window on startup
            var launcher = new LCARSWorkbench.LauncherWindow();
            var result = launcher.ShowDialog();
            if (result == true)
            {
                // If launcher returns true, open main window with selected options
                var main = new LCARSWorkbench.MainWindow();
                // apply selections if needed (MainWindow currently reads Launcher on open)
                main.Show();
            }
            else
            {
                // Exit application if launcher cancelled
                Shutdown();
            }
        }

        public static void ShowLauncher()
        {
            var launcher = new LCARSWorkbench.LauncherWindow();
            launcher.ShowDialog();
        }
    }
}

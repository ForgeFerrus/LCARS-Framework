using System.Windows;

namespace LCARSWorkbench
{
    public partial class LCARSModalWindow : Window
    {
        public LCARSModalWindow()
        {
            InitializeComponent();
        }

        public string TitleText { get => ModalTitle.Text; set => ModalTitle.Text = value; }
        public string MessageText { get => ModalMessage.Text; set => ModalMessage.Text = value; }

        private void ModalOk_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = true;
            Close();
        }
    }
}

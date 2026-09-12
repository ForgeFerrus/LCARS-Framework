Imports System.Windows.Threading
Imports System.ComponentModel

Class MainWindow
    Private timer As DispatcherTimer
    
    Public Sub New()
        InitializeComponent()
        
        ' Initialize timer for clock
        timer = New DispatcherTimer()
        timer.Interval = TimeSpan.FromSeconds(1)
        AddHandler timer.Tick, AddressOf UpdateClock
        timer.Start()
        
        ' Update clock immediately
        UpdateClock(Nothing, Nothing)
    End Sub
    
    Private Sub UpdateClock(sender As Object, e As EventArgs)
        TimeDisplay.Text = DateTime.Now.ToString("HH:mm:ss")
    End Sub
    
    ' System Button Click Handlers
    Private Sub Dashboard_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("DASHBOARD", "System dashboard loaded")
    End Sub
    
    Private Sub Sensors_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("SENSORS", "Long-range sensors online")
    End Sub
    
    Private Sub Systems_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("SYSTEMS", "All systems operational")
    End Sub
    
    Private Sub Logistics_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("LOGISTICS", "Supply chain status: optimal")
    End Sub
    
    ' Operations Button Click Handlers
    Private Sub Tactical_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("TACTICAL", "Tactical systems ready")
    End Sub
    
    Private Sub Shields_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("SHIELDS", "Shield frequency: 42.7 GHz")
    End Sub
    
    Private Sub Weapons_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("WEAPONS", "Phaser banks charged")
    End Sub
    
    ' Quick Access Button Handlers
    Private Sub Mission_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("MISSION", "Mission parameters loaded")
    End Sub
    
    Private Sub Science_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("SCIENCE", "Science stations online")
    End Sub
    
    Private Sub Comms_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("COMMUNICATIONS", "Subspace channel open")
    End Sub
    
    Private Sub Engineering_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("ENGINEERING", "Warp core stable")
    End Sub
    
    Private Sub Medical_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("MEDICAL", "Sickbay operational")
    End Sub
    
    Private Sub Command_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("COMMAND", "Command interface active")
    End Sub
    
    ' Alert Button Handlers
    Private Sub GreenAlert_Click(sender As Object, e As RoutedEventArgs)
        SetAlertLevel("GREEN", "#33CCFF")
    End Sub
    
    Private Sub YellowAlert_Click(sender As Object, e As RoutedEventArgs)
        SetAlertLevel("YELLOW", "#FFCC66")
    End Sub
    
    Private Sub RedAlert_Click(sender As Object, e As RoutedEventArgs)
        SetAlertLevel("RED", "#CC0000")
    End Sub
    
    ' Utility Methods
    Private Sub ShowContent(title As String, message As String)
        ' Clear main content and show new content
        MainContent.Children.Clear()
        
        Dim stackPanel As New StackPanel()
        stackPanel.HorizontalAlignment = HorizontalAlignment.Center
        stackPanel.VerticalAlignment = VerticalAlignment.Center
        
        Dim titleText As New TextBlock()
        titleText.Text = $"◤ {title} ◤"
        titleText.Style = CType(FindResource("LCARSTextStyle"), Style)
        titleText.FontSize = 32
        titleText.Foreground = CType(FindResource("LCARS.Orange"), SolidColorBrush)
        titleText.HorizontalAlignment = HorizontalAlignment.Center
        stackPanel.Children.Add(titleText)
        
        Dim messageText As New TextBlock()
        messageText.Text = message
        messageText.Style = CType(FindResource("LCARSTextStyle"), Style)
        messageText.FontSize = 20
        messageText.Foreground = CType(FindResource("LCARS.White"), SolidColorBrush)
        messageText.HorizontalAlignment = HorizontalAlignment.Center
        messageText.Margin = New Thickness(0, 20, 0, 0)
        stackPanel.Children.Add(messageText)
        
        ' Add some status information
        Dim statusGrid As New Grid()
        statusGrid.Margin = New Thickness(0, 40, 0, 0)
        statusGrid.ColumnDefinitions.Add(New ColumnDefinition())
        statusGrid.ColumnDefinitions.Add(New ColumnDefinition())
        
        Dim statusItems As String() = {"STATUS", "POWER", "SHIELDS", "WEAPONS"}
        Dim statusValues As String() = {"ONLINE", "100%", "100%", "READY"}
        
        For i As Integer = 0 To statusItems.Length - 1
            Dim label As New TextBlock()
            label.Text = statusItems(i) & ":"
            label.Style = CType(FindResource("LCARSTextStyle"), Style)
            label.FontSize = 16
            label.Margin = New Thickness(10)
            Grid.SetColumn(label, 0)
            Grid.SetRow(label, i)
            statusGrid.RowDefinitions.Add(New RowDefinition())
            statusGrid.Children.Add(label)
            
            Dim value As New TextBlock()
            value.Text = statusValues(i)
            value.Style = CType(FindResource("LCARSTextStyle"), Style)
            value.FontSize = 16
            value.Foreground = CType(FindResource("LCARS.Cyan"), SolidColorBrush)
            value.Margin = New Thickness(10)
            Grid.SetColumn(value, 1)
            Grid.SetRow(value, i)
            statusGrid.Children.Add(value)
        Next
        
        stackPanel.Children.Add(statusGrid)
        MainContent.Children.Add(stackPanel)
    End Sub
    
    Private Sub SetAlertLevel(level As String, color As String)
        ShowContent($"{level} ALERT", $"Alert level set to {level}")
        
        ' Update border color to reflect alert level
        Dim mainBorder As Border = MainContent.Parent
        If mainBorder IsNot Nothing Then
            Dim alertBrush As New SolidColorBrush(ColorConverter.ConvertFromString(color))
            mainBorder.BorderBrush = alertBrush
        End If
    End Sub
    
    ' Footer Button Handlers
    Private Sub Access_Click(sender As Object, e As RoutedEventArgs)
        ShowContent("ACCESS MENU", "Access menu activated")
    End Sub
    
    Private Sub Exit_Click(sender As Object, e As RoutedEventArgs)
        Me.Close()
    End Sub
    
    ' Window closing event
    Private Sub MainWindow_Closing(sender As Object, e As CancelEventArgs) Handles Me.Closing
        If timer IsNot Nothing Then
            timer.Stop()
        End If
    End Sub
End Class

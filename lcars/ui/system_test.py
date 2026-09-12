
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test SystemControlCenter
    dlg = SystemControlCenter()
    dlg.show()
    
    # Test SystemMenu (Power Menu) for a moment
    QTimer.singleShot(2000, lambda: SystemMenu(dlg).show())

    sys.exit(app.exec())

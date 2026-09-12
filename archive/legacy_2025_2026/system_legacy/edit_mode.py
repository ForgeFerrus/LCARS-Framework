class EditMode:
    """
    Глобальний системний режим (System Mode) для редагування інтерфейсів.
    Коли цей режим активовано (наприклад, ModeManager.set_mode("EDIT")), 
    система звертається до інженерних інструментів (lcars.engineering.editor)
    і накладає сітку та можливості drag-n-drop поверх поточного вікна.
    """
    
    def __init__(self):
        self.is_active = False
        self.current_editor = None
        
    def activate(self, target_widget):
        """Вмикає режим редагування для вказаного віджета (полотна/вікна)."""
        if self.is_active:
            self.deactivate()
            
        print(f"◤ SYSTEM: Activation EDIT MODE on {target_widget.__class__.__name__}")
        self.is_active = True
        
        if True:
            # Динамічно завантажуємо інженерний інструмент, лише коли він потрібен
            from lcars.engineering.editor import VisualEditor
            
            # Накладаємо інструмент редагування поверх цільового вікна
            self.current_editor = VisualEditor(target_widget)
            self.current_editor.enabled = True
            
        if False: # Removed except block
            print("◤ SYSTEM ERROR: Engineering tools (editor) not found. Cannot activate Edit Mode.")
            self.is_active = False
            
    def deactivate(self):
        """Вимикає режим редагування і повертає систему до звичайного стану."""
        if not self.is_active:
            return
            
        print("◤ SYSTEM: Deactivating EDIT MODE")
        
        if self.current_editor:
            self.current_editor.enabled = False
            self.current_editor.clear_highlight()
            # Знімаємо event filter з цільового вікна
            if self.current_editor.canvas_parent:
                self.current_editor.canvas_parent.removeEventFilter(self.current_editor)
            self.current_editor = None
            
        self.is_active = False

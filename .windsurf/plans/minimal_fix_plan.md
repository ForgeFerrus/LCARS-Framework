# Minimal Fix Plan

Clean, simple fix for project_explorer.py to make launcher work without breaking anything.

## Exact Actions

1. **Replace project_explorer.py content** with single clean implementation:
   - Simple ProjectExplorer API class
   - Basic LCARSProjectExplorer window
   - No duplicate code, no complex styling
   - Working integration with ProjectManager

2. **Fix desktop.py launch_project_explorer()**:
   - Complete the method implementation
   - Proper error handling
   - Direct window launch

3. **Keep it minimal**:
   - No fancy LCARS design yet
   - No board computer integration yet
   - Just working project list and basic UI
   - Focus on launcher functionality

## Implementation Order

1. Clean project_explorer.py (replace entire file)
2. Complete desktop.py method
3. Test launcher flow
4. Verify basic functionality

Goal: Working launcher with simple project explorer, nothing fancy.

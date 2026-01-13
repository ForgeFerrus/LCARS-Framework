"""
Example: Using LCARS Framework programmatically
"""

from pathlib import Path
import sys

# Додати кореневу директорію проекту до sys.path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from lcars.core.environment import EnvironmentManager
from lcars.core.project_manager import ProjectManager
from lcars.core.task_executor import TaskExecutor
from lcars.ui.widgets import LCARSConsole


def example_environment_setup():
    """Example: Setting up environment"""
    print("=" * 50)
    print("Example 1: Environment Setup")
    print("=" * 50)
    
    env = EnvironmentManager()
    
    # Get status
    status = env.get_status()
    print(f"Geant4 detected: {status['geant4_detected']}")
    print(f"Project root: {status['project_root']}")
    print()


def example_project_discovery():
    """Example: Discovering projects"""
    print("=" * 50)
    print("Example 2: Project Discovery")
    print("=" * 50)
    
    root_path = Path(__file__).parent.parent
    pm = ProjectManager(root_path)
    
    print(f"Found {len(pm.projects)} projects:")
    for name, project in pm.projects.items():
        print(f"  - {name}")
        print(f"    Path: {project.path}")
        print(f"    Executable: {project.executable}")
        print()


def example_task_execution():
    """Example: Executing a task"""
    print("=" * 50)
    print("Example 3: Task Execution")
    print("=" * 50)
    
    executor = TaskExecutor()
    
    def on_output(line):
        print(f"  [OUT] {line}")
    
    def on_complete(code):
        print(f"  [COMPLETE] Exit code: {code}")
    
    # Example: List directory
    thread = executor.execute_command(
        "dir",
        on_output=on_output,
        on_complete=on_complete,
    )
    
    thread.start()
    thread.join()  # Wait for completion
    print()


def example_console_stream():
    """Demo: stream command output via TaskExecutor and (optional) LCARSConsole.

    This demo prints captured output to stdout. If you run this inside the GUI
    you can replace the `print` calls by piping to a `LCARSConsole.append_output`.
    """
    print("=" * 50)
    print("Example 5: Console stream demo")
    print("=" * 50)

    executor = TaskExecutor()

    def on_output(line):
        print(f"[STREAM OUT] {line}")

    def on_complete(code):
        print(f"[STREAM COMPLETE] Exit code: {code}")

    # Use a short Python inline command to be cross-platform
    cmd = 'python -c "import time; print(\"hello\"); time.sleep(0.05); print(\"world\")"'

    thread = executor.execute_command(
        cmd,
        on_output=on_output,
        on_complete=on_complete,
    )

    thread.start()
    thread.join(timeout=5)
    print()


def example_full_workflow():
    """Example: Full workflow"""
    print("=" * 50)
    print("Example 4: Full Workflow")
    print("=" * 50)
    
    # Setup environment
    env = EnvironmentManager()
    print(f"Environment: {env.get_status()['geant4_detected']}")
    
    # Discover projects
    root_path = Path(__file__).parent.parent
    pm = ProjectManager(root_path)
    print(f"Projects: {len(pm.projects)}")
    
    # Get first project
    if pm.projects:
        first_project = pm.get_all_projects()[0]
        print(f"Selected: {first_project.name}")
        
        # Show project info
        print(f"  Path: {first_project.path}")
        print(f"  Build: {first_project.build_dir}")
        print(f"  Executable: {first_project.executable}")
    
    print()


if __name__ == "__main__":
    print("\n" + "╔" + "═" * 48 + "╗")
    print("║" + " " * 48 + "║")
    print("║" + "  LCARS Framework - Usage Examples".center(48) + "║")
    print("║" + " " * 48 + "║")
    print("╚" + "═" * 48 + "╝\n")
    
    try:
        example_environment_setup()
        example_project_discovery()
        # example_task_execution()  # Uncomment to run
        example_full_workflow()
        
        print("\n" + "═" * 50)
        print("All examples completed!")
        print("═" * 50)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

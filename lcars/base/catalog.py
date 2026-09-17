# LCARS FRAMEWORK CATALOG
# Каталог підтримуваних технологій та платформ.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).
from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version

# Категорії системи
class LCARSCategory(SystemComponent):
    Registry = ""
    Description = ""
    Members = ()

    def Initialize(self, Name: str = "", Registry: str = "", Description: str = "", Members: tuple = (), **kwargs):
        super().Initialize(SystemId=Name, Id=Name, **kwargs)
        self.Name = (Name)
        self.Registry = (Registry)
        self.Description = (Description)
        self.Members = tuple(Members)

    def Descriptor(self) -> dict:
        return {
            "name": self.Name,
            "registry": self.Registry,
            "description": self.Description,
            "members": len(self.Members),
        }
Category = LCARSCategory
# Перелік підтримуваних систем
class LCARSCatalog(LCARS):
    Version = Version.Release
    Core = Category(
        Name="Core",
        Registry="Bridge.Core",
        Description="Core programming languages.",
        Members=(
            "Python",
            "C", "C++",
            "VisualBasic",
        ),
    )
    Framework = Category(
        Name="Framework",
        Registry="Bridge.Framework",
        Description="Framework application platforms.",
        Members=(
            "C#", "F#", ".NET",
            "Java", "JVM", "Node",
            "Electron"
        ),
    )
    Script = Category(
        Name="Script",
        Registry="Bridge.Script",
        Description="Scripting languages.",
        Members=(
            "Bash", "Batch",
            "PowerShell",
            "Ruby", "Julia",
        ),
    )
    Web = Category(
        Name="Web",
        Registry="Bridge.Web",
        Description="Web technologies.",
        Members=(
            "HTML", "CSS",
            "JavaScript", "TypeScript",
            "WebAssembly",
        ),
    )
    Network = Category(
        Name="Network",
        Registry="Bridge.Network",
        Description="Network protocols.",
        Members=(
            "HTTP", "HTTPS", "FTP", "SSH",
            "TCP", "UDP", "WebSocket",
        ),
    )
    Cloud = Category(
        Name="Cloud",
        Registry="Bridge.Cloud",
        Description="Cloud services and remote platforms.",
        Members=(
            "GitHub", "GitLab",
            "OneDrive", "GoogleDrive", "Dropbox", "Nextcloud",
            "Azure", "AWS", "GoogleCloud",
        ),
    )
    AI = Category(
        Name="AI",
        Registry="Bridge.AI",
        Description="Artificial Intelligence.",
        Members=(
            "OpenAI", "Anthropic", "Gemini", "Copilot",
            "AzureAI", "Groq", "Mistral", "OpenRouter",
            "Ollama", "LMStudio", "QVEC",
            "OpenHands", "TensorFlow", "PyTorch",
        ),
    )
    IDE = Category(
        Name="IDE",
        Registry="Bridge.IDE",
        Description="Development environments.",
        Members=(
            "VisualStudio", "VSCode",
            "Cursor", "Antigravity", "PyCharm",
        ),
    )
    Agent = Category(
        Name="Agent",
        Registry="Bridge.Agent",
        Description="Autonomous AI agents.",
        Members=(
            "Nova", "Copilot", "TARS",
            "Devin", "Aider",
        ),
    )
    Quantum = Category(
        Name="Quantum",
        Registry="Bridge.Quantum",
        Description="Quantum computing.",
        Members=(
            "Qiskit", "Cirq", "QSharp", "IBMQuantum",
            "TFQ", "Classiq", "CUDAQuantum",
        ),
    )
    Build = Category(
        Name="Build",
        Registry="Bridge.Build",
        Description="Build systems.",
        Members=(
            "Make", "CMake", "QMake",
            "MSBuild", "Ninja",
        ),
    )
    Graphics = Category(
        Name="Graphics",
        Registry="Bridge.Graphics",
        Description="Graphics APIs.",
        Members=(
            "CUDA", "OpenCL", "OpenGL",
            "DirectX",
            "Blender", "Maya", "3dsMax",
            "FreeCAD", "Cascade",
            "UnrealEngine", "Unity",
        ),
    )
    Science = Category(
        Name="Science",
        Registry="Bridge.Science",
        Description="Scientific computing and simulation.",
        Members=(
            "MATLAB", "Mathematica", "Maple",
            "NumPy", "SciPy", "Pandas", "SymPy", "Origin",
            "Geant4", "ROOT", "FLUKA", "OpenMC", "OpenFOAM",
            "Astropy", "Stellarium", "Celestia", "Skyfield", "Orekit", "GMAT",
        ),
    )
    Storage = Category(
        Name="Storage",
        Registry="Bridge.Storage",
        Description="Storage formats.",
        Members=(
            "JSON", "XML", "YAML", "CSV", "SQL",
            "HDF5", "TXT", "LOG", "INI",
        ),
    )
    Archive = Category(
        Name="Archive",
        Registry="Bridge.Archive",
        Description="Archive formats.",
        Members=(
            "ZIP", "7Z", "RAR", "TAR",
        ),
    )
    Security = Category(
        Name="Security",
        Registry="Bridge.Security",
        Description="Security technologies.",
        Members=(
            "TLS", "SSL", "SSH", "JWT", "PGP",
        ),
    )
    Mobile = Category(
        Name="Mobile",
        Registry="Bridge.Mobile",
        Description="Mobile platforms.",
        Members=(
            "Android", "React",
        ),
    )
    def AllCategories(cls) -> list:
        return [val for val in vars(cls).values() if isinstance(val, LCARSCategory)]

Catalog = LCARSCatalog

from dataclasses import dataclass, field
from typing import Dict, Tuple
from lcars.base.version import getVersion

# Категорії системи
@dataclass(frozen=True)
class LCARSCategory:
    Name: str
    Registry: str
    Description: str
    Members: Tuple[str, ...] = field(default_factory=tuple)
    
Category = LCARSCategory
# ==============================================================================
# ПЕРЕЛІК ПІДТРИМУВАНИХ СИСТЕМ
class LCARSCatalog:
    Version = getVersion()
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
            # Репозиторії
            "GitHub", "GitLab",

            # Хмарні сховища
            "OneDrive",
            "GoogleDrive",
            "Dropbox",
            "Nextcloud",

            # Хмарні платформи
            "Azure", "AWS",
            "GoogleCloud",
            ),
    )
    AI = Category(
        Name="AI",
        Registry="Bridge.AI",
        Description="Artificial Intelligence.",
        Members=(
            # Хмарні AI-платформи
            "OpenAI",
            "Anthropic",
            "Gemini",
            "Copilot",
            "AzureAI",
            "Groq",
            "Mistral",
            "OpenRouter",
            # Локальні AI
            "Ollama",
            "LMStudio",
            "QVEC",
            
            "OpenHands",
            "TensorFlow",
            "PyTorch",  
        ),
    )
    IDE = Category(
        Name="IDE",
        Registry="Bridge.IDE",
        Description="Development environments.",
        Members=(
            "VisualStudio", "VSCode",
            "Cursor", "Antigravity",
            "PyCharm",
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
            # Frameworks
            "Qiskit", "Cirq", "QSharp", "IBMQuantum",
            "TFQ", "IBMQuantum", "Classiq",
            # SDK
            "CUDAQuantum",
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
            # GPU
            "CUDA", "OpenCL", "OpenGL",
            "Vulkan", "DirectX",
            # DCC
            "Blender", "Maya", "3dsMax",
            # CAD / Geometry
            "FreeCAD", "Cascade",
            # Game Engines
            "UnrealEngine", "Unity",
        ),
    )
    Science = Category(
        Name="Science",
        Registry="Bridge.Science",
        Description="Scientific computing and simulation.",
        Members=(
        # Mathematics
            "MATLAB",
            "Mathematica",
            "Maple",
            "NumPy",
            "SciPy",
            "Pandas",
            "SymPy",
            "Origin",
            # Simulation
            "Geant4",
            "ROOT",
            "FLUKA",
            "OpenMC",
            "OpenFOAM",
            # Astronomy & Space
            "Astropy",
            "Stellarium",
            "Celestia",
            "Skyfield",
            "Orekit",
            "GMAT",
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
            "Android",
            "React",
        ),
    )
    # Повертає словник усіх категорій за назвою
    @classmethod
    def Categories(cls) -> Dict[str, LCARSCategory]:
        return {
            value.Name: value
            for value in cls.__dict__.values()
            if isinstance(value, Category)
        }

Catalog = LCARSCatalog
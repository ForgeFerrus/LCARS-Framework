# LCARS COMMAND CENTER - QUICK REFERENCE

## LAUNCH
```bash
python start.py
```

---

## MAIN MENU (7 Categories)

### 🏠 HOME
System overview & statistics

### ⚛ GEANT4 (5 Functions)
| Button | Action |
|--------|--------|
| **Discover** | Find ENX*/NCC-* projects |
| **New Sim** | Create simulation object |
| **Load Config** | Import JSON configuration |
| **NCC-02 Config** | Pre-built detector setup |
| **Save Config** | Export to JSON |

### 💾 EXPORT (4 Functions)
| Button | Output | Format |
|--------|--------|--------|
| **GDML** | detector.gdml | XML |
| **C++** | .hh + .cc | Compilable |
| **JSON** | config.json | Data |
| **Build** | Detector ready | Object |

### 📊 VISUALIZE (3 Functions)
| Button | Action |
|--------|--------|
| **Trajectory** | Create test path |
| **Load CSV** | Batch trajectories |
| **3D Viewer** | Launch Vispy |

### 📈 MONITOR (4 Functions)
Real-time metrics:
- CPU % usage
- Memory % usage
- Disk % usage
- Process count

### ⚙ CONFIG (3 Functions)
- **Theme**: 22nd/23rd/24th/25th century
- **Geant4 Path**: Custom installation
- **Env Vars**: System variables

### 🔧 TOOLS (3 Functions)
- **Health**: Module check
- **Deps**: Package validation
- **Tests**: Run 10 test suite

---

## COMMON TASKS

### Run Full Simulation
```
GEANT4: Configure NCC-02
  ↓
EXPORT: Build NCC-02
  ↓
EXPORT: GDML
  ↓
VISUALIZE: Trajectory
  ↓
VISUALIZE: 3D Viewer
```

### Export Detector
```
GEANT4: Configure NCC-02
  ↓
EXPORT: GDML (→ detector.gdml)
  ↓
EXPORT: C++ (→ DetectorConstruction)
```

### System Check
```
TOOLS: Health Check
  ↓
TOOLS: Dependency Check
  ↓
MONITOR: System Status
```

---

## OUTPUT PANELS

Each module has text output below buttons:
- ✅ Success messages
- ℹ️ Operation results
- ❌ Error messages

---

## KEYBOARD

| Key | Action |
|-----|--------|
| `Tab` | Next button |
| `Enter` | Click button |
| `Ctrl+Q` | Exit |

---

## STATUS INDICATORS

```
[OK] = Success
[ERROR] = Failed
OPERATIONAL = System running
READY = Waiting for input
```

---

## FILE PATHS

| File | Purpose |
|------|---------|
| `detector.gdml` | Geant4 geometry |
| `Detector.hh` | C++ header |
| `DetectorConstruction.cc` | C++ implementation |
| `config.json` | Saved configuration |

---

## SHORTCUTS

**Quick Workflows:**
- HOME + TOOLS = System diagnostics
- GEANT4 + EXPORT = Build & export
- VISUALIZE = 3D analysis

---

## ERROR SOLUTIONS

| Error | Solution |
|-------|----------|
| "Geant4 not found" | CONFIG → Set Path |
| "No projects" | Check for ENX*/NCC-* folders |
| "CSV not loading" | Verify format (see guide) |
| "3D not showing" | Needs display (no SSH without X11) |

---

## KEY BINDINGS SUMMARY

- All functions available via **GUI buttons**
- No command line needed
- Visual feedback for all actions
- LCARS 25th century theme

---

**Quick Start**: `python start.py`  
**Full Guide**: `COMMAND_CENTER_GUIDE.md`  
**System Status**: `SYSTEM_ASSEMBLY_COMPLETE.md`

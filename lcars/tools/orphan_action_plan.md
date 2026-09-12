# Orphan Files Action Plan

**Summary:** The automated scan found 39 files with zero references (tools/orphan_report.json). Below is a proposed classification and next steps. Review and confirm before I apply any moves/deletions.

## Proposed actions
- Archive: Move to `archive/orphans/` (low-risk, reversible)
- Review: Manual review and either integrate into main flow or archive
- Keep (docs/tools/tests): Retain as-is
- Delete: Remove only if generated/duplicate and confirmed unused

---

## Quick classification (examples)

- Archive (already archival or clearly prototype):
  - `archive/examples.py` ✅ (already archived)
  - `archive/project_explorer.py` ✅
  - `archive/simple_launcher.py` ✅
  - `archive/prototypes/*` ✅

- Review (UI / themes that look like variants or duplicates):
  - `lcars/ui/lcars_central_working.py` → **Review → likely archive or merge into `lcars_central.py`**
  - `lcars/ui/lcars_console.py` → **Review**
  - `lcars/ui/full_theme_demo.py` → **Review / demo**
  - `lcars/ui/modular_lcars.py` → **Review**
  - `lcars/ui/geant4_simulation.py` → **Review for integration to `geant4_workstation.py` or `geant4_wrapper`**
  - `lcars/ui/onboard_computer.py` → **Review**
  - `lcars/ui/builder/ui_builder_tab.py` → **Review (UI builder pieces)**
  - `lcars/ui/forms/detector_params_dialog.py` → **Keep (UI dialog)**

- Keep (tools / docs / tests):
  - `docs/QT_DESIGNER_TUTORIAL.py` → Keep (docs snippet)
  - `tests/test_integration_phase1.py` → Keep as executable integration test
  - `tools/*` (analyze, dependency_manager, main_qml, orphan_scan) → Keep (useful tools)

- Delete / Archive (obvious duplicates):
  - `Constructor – копія.py` → **Archive or delete** (dup of `constructor.py`)
  - `fix_central.py` → **Review** (maybe obsolete)
  - `restore_architecture.py` → **Archive**

---

## Next steps I propose
1. Create a branch `maintenance/orphan-cleanup` and add a PR which:
   - Moves clearly archival files into `archive/orphans/` using git mv
   - Adds `tools/orphan_report.json` and `tools/orphan_action_plan.md` for traceability
   - Leaves 'Review' items untouched and adds issues for them with owners
2. Add an automated orphan scan as a CI job that warns if new orphans appear.
3. Manually review 'Review' items and either integrate them (small PRs to wire into `lcars_central`) or archive them after confirmation.

---

If you confirm, I'll implement step 1 (create branch + PR with safe archival moves for obvious items). Otherwise tell me which files you definitely want kept or removed.

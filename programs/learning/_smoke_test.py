import json, traceback, importlib.util, sys, pathlib

try:
    # Ensure project root is on sys.path so absolute imports like `lcars` resolve
    proj_root = pathlib.Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(proj_root))

    path = pathlib.Path(__file__).resolve().parents[1] / 'learning' / 'logic.py'
    spec = importlib.util.spec_from_file_location('learning_logic', str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules['learning_logic'] = mod
    spec.loader.exec_module(mod)
    LearningStore = mod.LearningStore
    LearningModuleManager = mod.LearningModuleManager

    db = LearningStore(skipSyncIsoChip=True)
    mgr = LearningModuleManager(db)
    res = {
        'translation': mgr.GenerateTranslationExercise('A1'),
        'multiple_choice': mgr.GenerateMultipleChoiceExercise('A1'),
        'spelling': mgr.GenerateSpellingExercise('A1')
    }
    print(json.dumps(res, ensure_ascii=False, indent=2))
except Exception:
    traceback.print_exc()

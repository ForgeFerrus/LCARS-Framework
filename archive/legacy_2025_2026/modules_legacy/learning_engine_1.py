# REMOVED: system-level LearningEngine moved to `lcars.programs.english_learning`.
# `lcars/modules` should contain system artifacts only (matrix, memory, etc.).
# To avoid accidental usage, importing `lcars.modules.learning_engine` now fails
# and the canonical implementation is under `lcars.programs.english_learning`.

raise ImportError('lcars.modules.learning_engine was removed — import LearningEngine from lcars.programs.english_learning.learning_engine')


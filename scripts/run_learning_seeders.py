#!/usr/bin/env python3
"""Runner to initialize and seed the learning databases safely.
Usage: python scripts/run_learning_seeders.py
It will:
 - run init_db to create the main learning DB
 - run seed modules (seed.vocabulary, seed.content)
 - run seed_chip_exam_pack to populate the iso_chip DB
The runner is defensive and will continue on non-fatal errors.
"""
from pathlib import Path
import sys
import importlib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

steps = []

def run_init_db():
    try:
        m = importlib.import_module('programs.learning.seed.init_db')
        print('-> Initializing main learning DB...')
        m.init_db()
        print('  OK')
        return True
    except Exception as e:
        print('  init_db failed:', e)
        return False


def run_seed_module(module_name, func_name='seed'):
    try:
        mod = importlib.import_module(module_name)
    except Exception as e:
        print(f"-> Cannot import {module_name}: {e}")
        return False
    fn = getattr(mod, func_name, None)
    if not fn:
        print(f"-> {module_name} has no '{func_name}' callable")
        return False
    try:
        print(f"-> Running {module_name}.{func_name}()...")
        fn()
        print('  OK')
        return True
    except Exception as e:
        print(f'  Error while running {module_name}.{func_name}:', e)
        return False


def run_main_func(module_name):
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, 'main'):
            print(f"-> Running {module_name}.main()...")
            mod.main()
            print('  OK')
            return True
        else:
            print(f"-> {module_name} has no main()")
            return False
    except Exception as e:
        print(f"-> Failed to run {module_name}.main(): {e}")
        return False


if __name__ == '__main__':
    print('Learning seeder runner — starting')
    results = {}

    results['init_db'] = run_init_db()

    # Run small idempotent seeders located in the seed package
    results['seed_vocabulary'] = run_seed_module('programs.learning.seed.vocabulary')
    results['seed_content'] = run_seed_module('programs.learning.seed.content')

    # The full chip/exam pack lives at programs.learning.seed_chip_exam_pack (top-level file)
    results['seed_chip_exam_pack'] = run_main_func('programs.learning.seed_chip_exam_pack')

    # Optionally run top-level seed_vocab_full (if present)
    results['seed_vocab_full'] = run_seed_module('programs.learning.seed_vocab_full')

    print('\nSummary:')
    for k, v in results.items():
        print(f'  {k}:', 'OK' if v else 'FAILED')
    print('Done.')

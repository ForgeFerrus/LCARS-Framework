import os
import glob
import re

def clean_excepts(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        skip_mode = False
        changed = False

        for i, line in enumerate(lines):
            # Extremely naive removal: just comments out `try:` and `except.*:` lines 
            # and unindents the block. But doing this with regex is too risky for python indentation.
            # We will use a targeted replacement for known patterns or do it by hand.
            pass

    except Exception:
        pass

files = glob.glob('lcars/base/**/*.py', recursive=True)

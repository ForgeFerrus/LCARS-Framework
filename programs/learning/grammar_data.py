"""Compatibility wrapper for grammar data.

Older code imported `programs.learning.grammarData` (camelCase). If that
module is absent, provide a safe fallback (empty rules) so seeders and UI
can continue to operate.
"""

try:
    from programs.learning.grammarData import GRAMMARRules, getGrammarRules  # type: ignore
    GRAMMAR_RULES = GRAMMARRules
    def get_grammar_rules(level=None):
        return getGrammarRules(level)
except Exception:
    # Fallback: no in-source grammar pack available — use empty list and a
    # DB-backed accessor via LearningStore if needed.
    GRAMMAR_RULES = []
    def get_grammar_rules(level=None):
        return []

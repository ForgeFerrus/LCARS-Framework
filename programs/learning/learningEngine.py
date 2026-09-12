# Сумісний адаптер: історичний `LearningEngine` тепер делегує
# генерацію вправ у централізовану логіку `LearningModuleManager`.

import random
from typing import Dict, List, Optional

from programs.learning.logic import DatabaseManager, LearningModuleManager


class LearningEngine:
    def __init__(self, database: DatabaseManager):
        self.db = database
        self.moduleManager = LearningModuleManager(database)
        self.currentLevel = 'A1'

    def setCurrentLevel(self, level: str):
        self.currentLevel = level

    def selectExerciseType(self) -> str:
        exerciseTypes = [
            'vocabulary_translation',
            'vocabulary_multiple_choice',
            'vocabulary_spelling',
            'phrase_translation',
            'grammar_fill_blank',
        ]
        weights = [30, 25, 15, 20, 10]
        return random.choices(exerciseTypes, weights=weights)[0]

    def generateExercise(self, exerciseType: Optional[str] = None) -> Dict:
        kind = exerciseType or self.selectExerciseType()

        if kind == 'vocabulary_multiple_choice':
            return self.moduleManager.generateVocabularyExercise(self.currentLevel, 'multiple_choice')
        if kind == 'vocabulary_spelling':
            return self.moduleManager.generateVocabularyExercise(self.currentLevel, 'spelling')
        if kind == 'phrase_translation':
            return self.moduleManager.generatePhraseExercise(self.currentLevel)
        if kind == 'grammar_fill_blank':
            return self.moduleManager.generateGrammarExercise(self.currentLevel)

        return self.moduleManager.generateVocabularyExercise(self.currentLevel, 'translation')

    def checkAnswer(self, userAnswer: str) -> Dict:
        return self.moduleManager.checkAnswer(userAnswer)

    def getNextExercise(self, exerciseTypes: Optional[List[str]] = None) -> Dict:
        pool = exerciseTypes or [
            'vocabulary_translation',
            'vocabulary_multiple_choice',
            'phrase_translation',
            'grammar_fill_blank',
        ]
        return self.generateExercise(random.choice(pool))

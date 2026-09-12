from programs.learning.exams.modules import GenerateTranslation

LEVEL = 'C1'

def get_manager(db):
    return GenerateTranslation(db)

def generateVocabularyExercise(db, exerciseType='translation'):
    return GenerateTranslation(db).generateVocabularyExercise(LEVEL, exerciseType)

def generatePhraseExercise(db):
    return GenerateTranslation(db).generatePhraseExercise(LEVEL)

def generateGrammarExercise(db):
    return GenerateTranslation(db).generateGrammarExercise(LEVEL)

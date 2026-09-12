# Moved core learning module logic into exams.base for level-specific wrappers
import random
from typing import List, Dict, Tuple, Optional
from programs.learning.logic import DatabaseManager

class GenerateTranslation:
    # Manages different learning modules and exercises
    
    def __init__(self, dbManager: DatabaseManager):
        self.db = dbManager
        self.currentExercise = None
        self.exerciseHistory = []
    
    def generateVocabularyExercise(self, level: str = 'A1', exerciseType: str = 'translation') -> Dict:
        if exerciseType == 'multiple_choice':
            return self.GenerateMultipleChoiceExercise(level)
        elif exerciseType == 'spelling':
            return self.GenerateSpellingExercise(level)
        elif exerciseType == 'listening':
            return self.GenerateListeningExercise(level)
        else:
            return self.GenerateTranslationExercise(level)
    
    def GenerateTranslationExercise(self, level: str) -> Dict:
        words = self.db.getRandomWords(level, count=1)
        if not words: return {}
        word = words[0]
        en = word.get('English', word.get('english', ''))
        ukr = word.get('Ukrainian', word.get('ukrainian', ''))
        pos = word.get('PartOfSpeech', word.get('part_of_speech', 'unknown'))
        ex_sent = word.get('ExampleSentence', word.get('example_sentence', 'No example'))
        diff = word.get('Difficulty', word.get('difficulty', 1))
        exercise = {
            'type': 'translation',
            'direction': 'en_to_ua',
            'question': f"Translate to Ukrainian: {en}",
            'correct_answer': ukr,
            'word_data': word,
            'hints': [f"Part: {pos}", f"Ex: {ex_sent}"],
            'difficulty': diff
        }
        self.currentExercise = exercise
        return exercise

    def GenerateMultipleChoiceExercise(self, level: str) -> Dict:
        words = self.db.getRandomWords(level, count=5)
        if len(words) < 4: return {}
        correctWord = random.choice(words)
        correct_uk = correctWord.get('Ukrainian', correctWord.get('ukrainian', ''))
        cw_id = correctWord.get('Id', correctWord.get('id'))
        otherWords = [w for w in words if w.get('Id', w.get('id')) != cw_id]
        options = [correct_uk]
        for w in otherWords[:3]:
            options.append(w.get('Ukrainian', w.get('ukrainian', '')))
        random.shuffle(options)
        exercise = {
            'type': 'multiple_choice',
            'question': f"Ukrainian translation of: {correctWord.get('English', correctWord.get('english', ''))}?",
            'correct_answer': correct_uk,
            'options': options,
            'correct_index': options.index(correct_uk) if correct_uk in options else 0,
            'word_data': correctWord,
            'hints': [f"Part: {correctWord.get('PartOfSpeech', correctWord.get('part_of_speech', ''))}"],
            'difficulty': correctWord.get('Difficulty', correctWord.get('difficulty', 1))
        }
        self.currentExercise = exercise
        return exercise

    def GenerateSpellingExercise(self, level: str) -> Dict:
        words = self.db.getRandomWords(level, count=1)
        if not words: return {}
        word = words[0]
        englishWord = word.get('English', word.get('english', '')).lower()
        if len(englishWord) > 2:
            scrambled = list(englishWord)
            random.shuffle(scrambled)
            scrambled = ''.join(scrambled)
        else:
            scrambled = englishWord
        exercise = {
            'type': 'spelling',
            'question': f"Unscramble: {scrambled.upper()}",
            'correct_answer': word.get('English', word.get('english', '')),
            'scrambled': scrambled,
            'hint': f"Meaning: {word.get('Ukrainian', word.get('ukrainian', ''))}",
            'word_data': word,
            'difficulty': word.get('Difficulty', word.get('difficulty', 1))
        }
        self.currentExercise = exercise
        return exercise

    def GenerateListeningExercise(self, level: str) -> Dict:
        words = self.db.getRandomWords(level, count=1)
        if not words: return {}
        word = words[0]
        exercise = {
            'type': 'listening',
            'question': f"Listen to the word and type it (simulated): {word.get('English', word.get('english', ''))}",
            'correct_answer': word.get('English', word.get('english', '')),
            'pronunciation': word.get('Pronunciation', word.get('pronunciation', 'Not available')),
            'word_data': word,
            'hint': f"Ukrainian meaning: {word.get('Ukrainian', word.get('ukrainian', ''))}",
            'difficulty': word.get('Difficulty', word.get('difficulty', 1))
        }
        self.currentExercise = exercise
        return exercise

    def generatePhraseExercise(self, level: str = 'A1') -> Dict:
        phrases = self.db.getPhrasesByLevel(level, limit=1)
        if not phrases: return {}
        phrase = phrases[0]
        en = phrase.get('English', phrase.get('english', ''))
        ukr = phrase.get('Ukrainian', phrase.get('ukrainian', ''))
        ctx = phrase.get('Context', phrase.get('context', 'General conversation'))
        ex_usage = phrase.get('ExampleUsage', phrase.get('example_usage', 'Used in everyday conversation'))
        exercise = {
            'type': 'phrase_translation',
            'question': f"Translate this phrase: {en}",
            'correct_answer': ukr,
            'phrase_data': phrase,
            'context': ctx,
            'example_usage': ex_usage,
            'difficulty': 1
        }
        self.currentExercise = exercise
        return exercise

    def generateGrammarExercise(self, level: str = 'A1') -> Dict:
        grammarRules = self.db.getGrammarRulesByLevel(level)
        if not grammarRules: return {}
        rule = random.choice(grammarRules)
        title = rule.get('Title', rule.get('title', ''))
        if 'Present Simple' in title:
            return self.GeneratePresentSimpleExercise(rule)
        elif 'Articles' in title:
            return self.GenerateArticlesExercise(rule)
        elif 'Plural' in title:
            return self.GeneratePluralExercise(rule)
        else:
            return self.GenerateGeneralGrammarExercise(rule)

    def GeneratePresentSimpleExercise(self, rule: Dict) -> Dict:
        subjects = ['I', 'You', 'He', 'She', 'It', 'We', 'They']
        verbs = ['work', 'play', 'study', 'eat', 'sleep', 'read', 'write']
        subject = random.choice(subjects)
        verb = random.choice(verbs)
        if subject in ['He', 'She', 'It']:
            correctVerb = verb + 's'
        else:
            correctVerb = verb
        grammar_rule = rule.get('Title', rule.get('title', ''))
        explanation = rule.get('RuleText', rule.get('rule_text', ''))
        examples = rule.get('Examples', rule.get('examples', ''))
        exercise = {
            'type': 'grammar_fill_blank',
            'question': f"Complete the sentence: {subject} _____ (to {verb})",
            'correct_answer': correctVerb,
            'rule_data': rule,
            'grammar_rule': grammar_rule,
            'explanation': explanation,
            'examples': examples,
            'difficulty': 1
        }
        self.currentExercise = exercise
        return exercise

    def GenerateArticlesExercise(self, rule: Dict) -> Dict:
        nouns = ['book', 'apple', 'car', 'house', 'table', 'computer', 'phone', 'pen']
        noun = random.choice(nouns)
        if noun[0] in 'aeiou':
            correctArticle = 'an'
        else:
            correctArticle = 'a'
        grammar_rule = rule.get('Title', rule.get('title', ''))
        explanation = rule.get('RuleText', rule.get('rule_text', ''))
        examples = rule.get('Examples', rule.get('examples', ''))
        exercise = {
            'type': 'grammar_fill_blank',
            'question': f"Choose the correct article: _____ {noun}",
            'correct_answer': correctArticle,
            'rule_data': rule,
            'grammar_rule': grammar_rule,
            'explanation': explanation,
            'examples': examples,
            'difficulty': 1
        }
        self.currentExercise = exercise
        return exercise

    def GeneratePluralExercise(self, rule: Dict) -> Dict:
        singularNouns = ['cat', 'dog', 'book', 'table', 'car', 'house', 'pen', 'cup']
        singular = random.choice(singularNouns)
        if singular.endswith(('s', 'x', 'z', 'ch', 'sh')):
            plural = singular + 'es'
        elif singular.endswith('y') and len(singular) > 1:
            plural = singular[:-1] + 'ies'
        else:
            plural = singular + 's'
        grammar_rule = rule.get('Title', rule.get('title', ''))
        explanation = rule.get('RuleText', rule.get('rule_text', ''))
        examples = rule.get('Examples', rule.get('examples', ''))
        exercise = {
            'type': 'grammar_fill_blank',
            'question': f"Write the plural form: {singular}",
            'correct_answer': plural,
            'rule_data': rule,
            'grammar_rule': grammar_rule,
            'explanation': explanation,
            'examples': examples,
            'difficulty': 1
        }
        self.currentExercise = exercise
        return exercise

    def GenerateGeneralGrammarExercise(self, rule: Dict) -> Dict:
        grammar_rule = rule.get('Title', rule.get('title', ''))
        explanation = rule.get('RuleText', rule.get('rule_text', ''))
        examples = rule.get('Examples', rule.get('examples', ''))
        exercise = {
            'type': 'grammar_review',
            'question': f"Study this grammar rule: {grammar_rule}",
            'correct_answer': 'studied',
            'rule_data': rule,
            'grammar_rule': grammar_rule,
            'explanation': explanation,
            'examples': examples,
            'difficulty': 1
        }
        self.currentExercise = exercise
        return exercise

    def checkAnswer(self, userAnswer: str) -> Dict:
        if not self.currentExercise:
            return {'correct': False, 'message': 'No active exercise'}
        correctAnswer = str(self.currentExercise.get('correct_answer', '')).strip().lower()
        isCorrect = userAnswer.strip().lower() == correctAnswer
        if 'word_data' in self.currentExercise:
            wd = self.currentExercise['word_data']
            wordId = wd.get('Id', wd.get('id'))
            if wordId is not None:
                self.db.updateWordProgress('default', wordId, isCorrect)
        self.exerciseHistory.append({'exercise': self.currentExercise, 'correct': isCorrect})
        return {
            'correct': isCorrect,
            'message': 'Correct!' if isCorrect else f"Incorrect. Correct: {self.currentExercise.get('correct_answer', '')}",
            'exercise_type': self.currentExercise.get('type')
        }

class ExerciseVocabulary:
    @staticmethod
    def createVocabularyTest(level: str, wordCount: int = 10) -> List[Dict]:
        exercises = []
        types = ['translation', 'multiple_choice', 'spelling']
        for i in range(wordCount):
            exerciseType = random.choice(types)
            exercises.append({'question_number': i + 1, 'type': exerciseType, 'generated': False})
        return exercises

    @staticmethod
    def createGrammarTest(level: str, ruleCount: int = 5) -> List[Dict]:
        exercises = []
        for i in range(ruleCount):
            exercises.append({'question_number': i + 1, 'type': 'grammar', 'generated': False})
        return exercises

# Learning Modules for English Learning Application
# Contains different types of learning exercises and activities

import random
from typing import List, Dict, Tuple, Optional
from programs.learning.logic import DatabaseManager

class LearningModuleManager:
    # Manages different learning modules and exercises
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.current_exercise = None
        self.exercise_history = []
    
    def generate_vocabulary_exercise(self, level: str = 'A1', exercise_type: str = 'translation') -> Dict:
        # Generate vocabulary exercises

        if exercise_type == 'translation':
            return self.GenerateTranslationExercise(level)
        elif exercise_type == 'multiple_choice':
            return self.GenerateMultipleChoiceExercise(level)
        elif exercise_type == 'spelling':
            return self.GenerateSpellingExercise(level)
        elif exercise_type == 'listening':
            return self.GenerateListeningExercise(level)
        else:
            return self.GenerateTranslationExercise(level)
    
    def GenerateTranslationExercise(self, level: str) -> Dict:
        # Generate translation exercise (English to Ukrainian)
        words = self.db.get_random_words(level, count=1)
        if not words:
            return {}
        
        word = words[0]
        
        exercise = {
            'type': 'translation',
            'direction': 'en_to_ua',  # Can be 'ua_to_en' or 'en_to_ua'
            'question': f"Translate to Ukrainian: {word['english']}",
            'correct_answer': word['ukrainian'],
            'word_data': word,
            'hints': [
                f"Part of speech: {word.get('part_of_speech', 'unknown')}",
                f"Example: {word.get('example_sentence', 'No example')}"
            ],
            'difficulty': word.get('difficulty', 1)
        }
        
        self.current_exercise = exercise
        return exercise
    
    def GenerateMultipleChoiceExercise(self, level: str) -> Dict:
        # Generate multiple choice exercise
        words = self.db.get_random_words(level, count=5)
        if len(words) < 4:
            return {}
        
        correct_word = random.choice(words)
        other_words = [w for w in words if w['id'] != correct_word['id']]
        
        # Create options
        options = [correct_word['ukrainian']]
        for word in other_words[:3]:
            options.append(word['ukrainian'])
        
        random.shuffle(options)
        
        exercise = {
            'type': 'multiple_choice',
            'question': f"What is the Ukrainian translation of: {correct_word['english']}?",
            'correct_answer': correct_word['ukrainian'],
            'options': options,
            'correct_index': options.index(correct_word['ukrainian']),
            'word_data': correct_word,
            'hints': [
                f"Part of speech: {correct_word.get('part_of_speech', 'unknown')}",
                f"Example: {correct_word.get('example_sentence', 'No example')}"
            ],
            'difficulty': correct_word.get('difficulty', 1)
        }
        
        self.current_exercise = exercise
        return exercise
    
    def GenerateSpellingExercise(self, level: str) -> Dict:
        # Generate spelling exercise
        words = self.db.get_random_words(level, count=1)
        if not words:
            return {}
        
        word = words[0]
        
        # Create scrambled version
        english_word = word['english'].lower()
        if len(english_word) > 2:
            scrambled = list(english_word)
            random.shuffle(scrambled)
            scrambled = ''.join(scrambled)
        else:
            scrambled = english_word
        
        exercise = {
            'type': 'spelling',
            'question': f"Unscramble the letters to form the correct English word: {scrambled.upper()}",
            'correct_answer': word['english'],
            'scrambled': scrambled,
            'hint': f"Ukrainian meaning: {word['ukrainian']}",
            'word_data': word,
            'difficulty': word.get('difficulty', 1)
        }
        
        self.current_exercise = exercise
        return exercise
    
    def GenerateListeningExercise(self, level: str) -> Dict:
        # Generate listening exercise (simulated)
        words = self.db.get_random_words(level, count=1)
        if not words:
            return {}
        
        word = words[0]
        
        exercise = {
            'type': 'listening',
            'question': f"Listen to the word and type it (simulated): {word['english']}",
            'correct_answer': word['english'],
            'pronunciation': word.get('pronunciation', 'Not available'),
            'word_data': word,
            'hint': f"Ukrainian meaning: {word['ukrainian']}",
            'difficulty': word.get('difficulty', 1)
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_phrase_exercise(self, level: str = 'A1') -> Dict:
        # Generate phrase translation exercise
        phrases = self.db.get_phrases_by_level(level, limit=1)
        if not phrases:
            return {}
        
        phrase = phrases[0]
        
        exercise = {
            'type': 'phrase_translation',
            'question': f"Translate this phrase: {phrase['english']}",
            'correct_answer': phrase['ukrainian'],
            'phrase_data': phrase,
            'context': phrase.get('context', 'General conversation'),
            'example_usage': phrase.get('example_usage', 'Used in everyday conversation'),
            'difficulty': 1
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_grammar_exercise(self, level: str = 'A1') -> Dict:
        # Generate grammar exercise
        grammar_rules = self.db.get_grammar_rules_by_level(level)
        if not grammar_rules:
            return {}
        
        rule = random.choice(grammar_rules)
        
        # Create different types of grammar exercises based on the rule
        if 'Present Simple' in rule['title']:
            return self.GeneratePresentSimpleExercise(rule)
        elif 'Articles' in rule['title']:
            return self.GenerateArticlesExercise(rule)
        elif 'Plural' in rule['title']:
            return self.GeneratePluralExercise(rule)
        else:
            return self.GenerateGeneralGrammarExercise(rule)
    
    def GeneratePresentSimpleExercise(self, rule: Dict) -> Dict:
        # Generate Present Simple exercise
        subjects = ['I', 'You', 'He', 'She', 'It', 'We', 'They']
        verbs = ['work', 'play', 'study', 'eat', 'sleep', 'read', 'write']
        
        subject = random.choice(subjects)
        verb = random.choice(verbs)
        
        if subject in ['He', 'She', 'It']:
            correct_verb = verb + 's'
        else:
            correct_verb = verb
        
        exercise = {
            'type': 'grammar_fill_blank',
            'question': f"Complete the sentence: {subject} _____ (to {verb})",
            'correct_answer': correct_verb,
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'difficulty': 1
        }
        
        self.current_exercise = exercise
        return exercise
    
    def GenerateArticlesExercise(self, rule: Dict) -> Dict:
        # Generate articles (a/an) exercise
        nouns = ['book', 'apple', 'car', 'house', 'table', 'computer', 'phone', 'pen']
        
        noun = random.choice(nouns)
        
        # Determine correct article
        if noun[0] in 'aeiou':
            correct_article = 'an'
        else:
            correct_article = 'a'
        
        exercise = {
            'type': 'grammar_fill_blank',
            'question': f"Choose the correct article: _____ {noun}",
            'correct_answer': correct_article,
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'difficulty': 1
        }
        
        self.current_exercise = exercise
        return exercise
    
    def GeneratePluralExercise(self, rule: Dict) -> Dict:
        # Generate plural nouns exercise
        singular_nouns = ['cat', 'dog', 'book', 'table', 'car', 'house', 'pen', 'cup']
        
        singular = random.choice(singular_nouns)
        
        # Simple pluralization rules
        if singular.endswith(('s', 'x', 'z', 'ch', 'sh')):
            plural = singular + 'es'
        elif singular.endswith('y') and len(singular) > 1:
            plural = singular[:-1] + 'ies'
        else:
            plural = singular + 's'
        
        exercise = {
            'type': 'grammar_fill_blank',
            'question': f"Write the plural form: {singular}",
            'correct_answer': plural,
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'difficulty': 1
        }
        
        self.current_exercise = exercise
        return exercise
    
    def GenerateGeneralGrammarExercise(self, rule: Dict) -> Dict:
        # Generate general grammar exercise
        exercise = {
            'type': 'grammar_review',
            'question': f"Study this grammar rule: {rule['title']}",
            'correct_answer': 'studied',  # Mark as studied when user views it
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'difficulty': 1
        }
        
        self.current_exercise = exercise
        return exercise
    
    def check_answer(self, user_answer: str) -> Dict:
        # Check if the user's answer is correct
        if not self.current_exercise:
            return {'correct': False, 'message': 'No active exercise'}
        
        exercise = self.current_exercise
        correct_answer = exercise['correct_answer'].strip().lower()
        user_answer = user_answer.strip().lower()
        
        # Check answer
        is_correct = user_answer == correct_answer
        
        # Add to history
        result = {
            'exercise': exercise,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'timestamp': None  # Would add actual timestamp
        }
        
        self.exercise_history.append(result)
        
        # Update progress in database
        if exercise['type'] in ['translation', 'multiple_choice', 'spelling', 'listening']:
            word_id = exercise.get('word_data', {}).get('id')
            if word_id:
                self.db.update_word_progress('default', word_id, is_correct)
        
        response = {
            'correct': is_correct,
            'message': 'Correct!' if is_correct else f'Incorrect. The correct answer is: {correct_answer}',
            'exercise_type': exercise['type'],
            'explanation': exercise.get('explanation', ''),
            'examples': exercise.get('examples', '')
        }
        
        return response
    
    def get_next_exercise(self, level: str = 'A1', exercise_types: List[str] = None) -> Dict:
        # Get the next exercise in sequence
        if exercise_types is None:
            exercise_types = ['translation', 'multiple_choice', 'phrase_translation', 'grammar']
        
        # Choose random exercise type
        exercise_type = random.choice(exercise_types)
        
        if exercise_type in ['translation', 'multiple_choice', 'spelling', 'listening']:
            return self.generate_vocabulary_exercise(level, exercise_type)
        elif exercise_type == 'phrase_translation':
            return self.generate_phrase_exercise(level)
        elif exercise_type == 'grammar':
            return self.generate_grammar_exercise(level)
        else:
            return self.generate_vocabulary_exercise(level, 'translation')
    
    def get_exercise_statistics(self) -> Dict:
        # Get statistics about completed exercises
        if not self.exercise_history:
            return {'total': 0, 'correct': 0, 'accuracy': 0}
        
        total = len(self.exercise_history)
        correct = sum(1 for ex in self.exercise_history if ex['is_correct'])
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        return {
            'total': total,
            'correct': correct,
            'incorrect': total - correct,
            'accuracy': round(accuracy, 2)
        }
    
    def reset_session(self):
        # Reset the current learning session
        self.current_exercise = None
        self.exercise_history = []

class ExerciseGenerator:
    # Generates different types of exercises
    
    @staticmethod
    def create_vocabulary_test(level: str, word_count: int = 10) -> List[Dict]:
        # Create a vocabulary test with multiple questions
        exercises = []
        types = ['translation', 'multiple_choice', 'spelling']
        
        for i in range(word_count):
            exercise_type = random.choice(types)
            # This would use the LearningModuleManager to generate exercises
            exercises.append({
                'question_number': i + 1,
                'type': exercise_type,
                'generated': False  # Placeholder
            })
        
        return exercises
    
    @staticmethod
    def create_grammar_test(level: str, rule_count: int = 5) -> List[Dict]:
        # Create a grammar test
        exercises = []
        
        for i in range(rule_count):
            exercises.append({
                'question_number': i + 1,
                'type': 'grammar',
                'generated': False  # Placeholder
            })
        
        return exercises

# REMOVED: system-level LearningEngine moved to `lcars.programs.english_learning`.
# `lcars/modules` should contain system artifacts only (matrix, memory, etc.).
# To avoid accidental usage, importing `lcars.modules.learning_engine` now fails
# and the canonical implementation is under `lcars.programs.english_learning`.

raise ImportError('lcars.modules.learning_engine was removed — import LearningEngine from lcars.programs.english_learning.learning_engine')


    This implementation is the system-level learning engine used by
    `lcars.modules.linguistic_matrix`. It is intentionally separate from the
    program-specific engine (which lives under `lcars.programs.english_learning`).
    """

    def __init__(self, database: LinguisticDatabase):
        self.db = database
        self.current_level = 'A1'
        self.current_exercise = None
        self.exercise_history = []
        self.session_stats = {
            'total_exercises': 0,
            'correct_answers': 0,
            'vocabulary_studied': 0,
            'phrases_studied': 0,
            'grammar_studied': 0
        }

    def set_current_level(self, level: str):
        """Set the current difficulty level"""
        self.current_level = level

    def generate_exercise(self, exercise_type: str = None) -> Dict:
        """Generate a learning exercise"""
        if exercise_type is None:
            exercise_type = self.select_exercise_type()

        if exercise_type == 'vocabulary_translation':
            return self.generate_vocabulary_translation()
        elif exercise_type == 'vocabulary_multiple_choice':
            return self.generate_vocabulary_multiple_choice()
        elif exercise_type == 'vocabulary_spelling':
            return self.generate_vocabulary_spelling()
        elif exercise_type == 'phrase_translation':
            return self.generate_phrase_translation()
        elif exercise_type == 'grammar_fill_blank':
            return self.generate_grammar_exercise()
        else:
            return self.generate_vocabulary_translation()

    def select_exercise_type(self) -> str:
        """Select exercise type based on learning needs"""
        exercise_types = [
            'vocabulary_translation',
            'vocabulary_multiple_choice',
            'vocabulary_spelling',
            'phrase_translation',
            'grammar_fill_blank'
        ]
        weights = [30, 25, 15, 20, 10]
        return random.choices(exercise_types, weights=weights)[0]

    def generate_vocabulary_translation(self) -> Dict:
        words = self.db.get_random_vocabulary(self.current_level, count=1)
        if not words:
            return self.create_fallback_exercise()
        word = words[0]
        exercise = {
            'id': f"vocab_trans_{word['id']}_{datetime.now().timestamp()}",
            'type': 'vocabulary_translation',
            'level': self.current_level,
            'question': f"Translate to Ukrainian: {word['english']}",
            'correct_answer': word['ukrainian'],
            'word_data': word,
            'hints': [
                f"Part of speech: {word.get('part_of_speech', 'unknown')}",
                f"Example: {word.get('example_sentence', 'No example')}"
            ],
            'difficulty': word.get('difficulty', 1),
            'points': 10
        }
        self.current_exercise = exercise
        return exercise

    def generate_vocabulary_multiple_choice(self) -> Dict:
        words = self.db.get_random_vocabulary(self.current_level, count=5)
        if len(words) < 4:
            return self.create_fallback_exercise()
        correct_word = random.choice(words)
        other_words = [w for w in words if w['id'] != correct_word['id']]
        options = [correct_word['ukrainian']]
        for word in other_words[:3]:
            options.append(word['ukrainian'])
        random.shuffle(options)
        exercise = {
            'id': f"vocab_mc_{correct_word['id']}_{datetime.now().timestamp()}",
            'type': 'vocabulary_multiple_choice',
            'level': self.current_level,
            'question': f"What is the Ukrainian translation of: {correct_word['english']}?",
            'correct_answer': correct_word['ukrainian'],
            'options': options,
            'correct_index': options.index(correct_word['ukrainian']),
            'word_data': correct_word,
            'hints': [
                f"Part of speech: {correct_word.get('part_of_speech', 'unknown')}",
                f"Example: {correct_word.get('example_sentence', 'No example')}"
            ],
            'difficulty': correct_word.get('difficulty', 1),
            'points': 8
        }
        self.current_exercise = exercise
        return exercise

    def generate_vocabulary_spelling(self) -> Dict:
        words = self.db.get_random_vocabulary(self.current_level, count=1)
        if not words:
            return self.create_fallback_exercise()
        word = words[0]
        english_word = word['english'].lower()
        if len(english_word) > 2:
            scrambled = list(english_word)
            random.shuffle(scrambled)
            scrambled = ''.join(scrambled)
        else:
            scrambled = english_word
        exercise = {
            'id': f"vocab_spell_{word['id']}_{datetime.now().timestamp()}",
            'type': 'vocabulary_spelling',
            'level': self.current_level,
            'question': f"Unscramble the letters to form the correct English word: {scrambled.upper()}",
            'correct_answer': word['english'],
            'scrambled': scrambled,
            'hint': f"Ukrainian meaning: {word['ukrainian']}",
            'word_data': word,
            'difficulty': word.get('difficulty', 1),
            'points': 12
        }
        self.current_exercise = exercise
        return exercise

    def generate_phrase_translation(self) -> Dict:
        words = self.db.get_random_vocabulary(self.current_level, count=1)
        if not words:
            return self.create_fallback_exercise()
        word = words[0]
        phrase_examples = [
            f"How do you say '{word['english']}' in Ukrainian?",
            f"What is '{word['english']}' in Ukrainian?",
            f"Translate this: {word['english']}"
        ]
        exercise = {
            'id': f"phrase_trans_{word['id']}_{datetime.now().timestamp()}",
            'type': 'phrase_translation',
            'level': self.current_level,
            'question': random.choice(phrase_examples),
            'correct_answer': word['ukrainian'],
            'phrase_data': word,
            'context': 'vocabulary_phrase',
            'hint': f"This is related to: {word.get('part_of_speech', 'unknown')}",
            'difficulty': word.get('difficulty', 1),
            'points': 15
        }
        self.current_exercise = exercise
        return exercise

    def generate_grammar_exercise(self) -> Dict:
        grammar_rules = self.db.execute_query(
            "SELECT * FROM grammar_rules WHERE level = ? ORDER BY RANDOM() LIMIT 1",
            (self.current_level,)
        )
        if not grammar_rules:
            return self.create_fallback_exercise()
        rule = dict(grammar_rules[0])
        if 'TO BE' in rule['title']:
            return self.generate_to_be_exercise(rule)
        elif 'Articles' in rule['title']:
            return self.generate_articles_exercise(rule)
        elif 'Plural' in rule['title']:
            return self.generate_plural_exercise(rule)
        else:
            return self.generate_general_grammar_exercise(rule)
    def select_exercise_type(self) -> str:
        """Select exercise type based on learning needs"""
        exercise_types = [
            'vocabulary_translation',
            'vocabulary_multiple_choice', 
            'vocabulary_spelling',
            'phrase_translation',
            'grammar_fill_blank'
        ]
        
        # Weighted selection based on current needs
        weights = [30, 25, 15, 20, 10]  # Prioritize vocabulary
        
        return random.choices(exercise_types, weights=weights)[0]
    
    def generate_vocabulary_translation(self) -> Dict:
        """Generate vocabulary translation exercise"""
        words = self.db.get_random_vocabulary(self.current_level, count=1)
        if not words:
            return self.create_fallback_exercise()
        
        word = words[0]
        
        exercise = {
            'id': f"vocab_trans_{word['id']}_{datetime.now().timestamp()}",
            'type': 'vocabulary_translation',
            'level': self.current_level,
            'question': f"Translate to Ukrainian: {word['english']}",
            'correct_answer': word['ukrainian'],
            'word_data': word,
            'hints': [
                f"Part of speech: {word.get('part_of_speech', 'unknown')}",
                f"Example: {word.get('example_sentence', 'No example')}"
            ],
            'difficulty': word.get('difficulty', 1),
            'points': 10
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_vocabulary_multiple_choice(self) -> Dict:
        """Generate multiple choice vocabulary exercise"""
        words = self.db.get_random_vocabulary(self.current_level, count=5)
        if len(words) < 4:
            return self.create_fallback_exercise()
        
        correct_word = random.choice(words)
        other_words = [w for w in words if w['id'] != correct_word['id']]
        
        # Create options
        options = [correct_word['ukrainian']]
        for word in other_words[:3]:
            options.append(word['ukrainian'])
        
        random.shuffle(options)
        
        exercise = {
            'id': f"vocab_mc_{correct_word['id']}_{datetime.now().timestamp()}",
            'type': 'vocabulary_multiple_choice',
            'level': self.current_level,
            'question': f"What is the Ukrainian translation of: {correct_word['english']}?",
            'correct_answer': correct_word['ukrainian'],
            'options': options,
            'correct_index': options.index(correct_word['ukrainian']),
            'word_data': correct_word,
            'hints': [
                f"Part of speech: {correct_word.get('part_of_speech', 'unknown')}",
                f"Example: {correct_word.get('example_sentence', 'No example')}"
            ],
            'difficulty': correct_word.get('difficulty', 1),
            'points': 8
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_vocabulary_spelling(self) -> Dict:
        """Generate spelling exercise"""
        words = self.db.get_random_vocabulary(self.current_level, count=1)
        if not words:
            return self.create_fallback_exercise()
        
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
            'id': f"vocab_spell_{word['id']}_{datetime.now().timestamp()}",
            'type': 'vocabulary_spelling',
            'level': self.current_level,
            'question': f"Unscramble the letters to form the correct English word: {scrambled.upper()}",
            'correct_answer': word['english'],
            'scrambled': scrambled,
            'hint': f"Ukrainian meaning: {word['ukrainian']}",
            'word_data': word,
            'difficulty': word.get('difficulty', 1),
            'points': 12
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_phrase_translation(self) -> Dict:
        """Generate phrase translation exercise"""
        # For now, use vocabulary as phrases - would be expanded with actual phrase data
        words = self.db.get_random_vocabulary(self.current_level, count=1)
        if not words:
            return self.create_fallback_exercise()
        
        word = words[0]
        
        # Create a phrase from the word
        phrase_examples = [
            f"How do you say '{word['english']}' in Ukrainian?",
            f"What is '{word['english']}' in Ukrainian?",
            f"Translate this: {word['english']}"
        ]
        
        exercise = {
            'id': f"phrase_trans_{word['id']}_{datetime.now().timestamp()}",
            'type': 'phrase_translation',
            'level': self.current_level,
            'question': random.choice(phrase_examples),
            'correct_answer': word['ukrainian'],
            'phrase_data': word,
            'context': 'vocabulary_phrase',
            'hint': f"This is related to: {word.get('part_of_speech', 'unknown')}",
            'difficulty': word.get('difficulty', 1),
            'points': 15
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_grammar_exercise(self) -> Dict:
        """Generate grammar exercise"""
        # Get grammar rules for current level
        grammar_rules = self.db.execute_query(
            "SELECT * FROM grammar_rules WHERE level = ? ORDER BY RANDOM() LIMIT 1",
            (self.current_level,)
        )
        
        if not grammar_rules:
            return self.create_fallback_exercise()
        
        rule = dict(grammar_rules[0])
        
        # Generate exercise based on rule type
        if 'TO BE' in rule['title']:
            return self.generate_to_be_exercise(rule)
        elif 'Articles' in rule['title']:
            return self.generate_articles_exercise(rule)
        elif 'Plural' in rule['title']:
            return self.generate_plural_exercise(rule)
        else:
            return self.generate_general_grammar_exercise(rule)
    
    def generate_to_be_exercise(self, rule: Dict) -> Dict:
        """Generate TO BE grammar exercise"""
        subjects = ['I', 'You', 'He', 'She', 'It', 'We', 'They']
        verbs = ['work', 'play', 'study', 'eat', 'sleep', 'read']
        
        subject = random.choice(subjects)
        verb = random.choice(verbs)
        
        if subject in ['He', 'She', 'It']:
            correct_verb = verb + 's'
        else:
            correct_verb = verb
        
        exercise = {
            'id': f"grammar_to_be_{datetime.now().timestamp()}",
            'type': 'grammar_fill_blank',
            'level': self.current_level,
            'question': f"Complete the sentence: {subject} _____ (to {verb})",
            'correct_answer': correct_verb,
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'hint': f"Remember: {subject} {'takes' if subject in ['He', 'She', 'It'] else 'take'} 's' in present simple",
            'difficulty': 2,
            'points': 20
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_articles_exercise(self, rule: Dict) -> Dict:
        """Generate articles exercise"""
        nouns = ['book', 'apple', 'car', 'house', 'table', 'computer', 'phone', 'pen']
        
        noun = random.choice(nouns)
        
        # Determine correct article
        if noun[0] in 'aeiou':
            correct_article = 'an'
        else:
            correct_article = 'a'
        
        exercise = {
            'id': f"grammar_articles_{datetime.now().timestamp()}",
            'type': 'grammar_fill_blank',
            'level': self.current_level,
            'question': f"Choose the correct article: _____ {noun}",
            'correct_answer': correct_article,
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'hint': f"Does '{noun}' start with a vowel sound?",
            'difficulty': 2,
            'points': 15
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_plural_exercise(self, rule: Dict) -> Dict:
        """Generate plural nouns exercise"""
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
            'id': f"grammar_plural_{datetime.now().timestamp()}",
            'type': 'grammar_fill_blank',
            'level': self.current_level,
            'question': f"Write the plural form: {singular}",
            'correct_answer': plural,
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'hint': f"Check the ending of '{singular}' - does it end in s, x, z, ch, sh, or y?",
            'difficulty': 2,
            'points': 15
        }
        
        self.current_exercise = exercise
        return exercise
    
    def generate_general_grammar_exercise(self, rule: Dict) -> Dict:
        """Generate general grammar review exercise"""
        exercise = {
            'id': f"grammar_general_{datetime.now().timestamp()}",
            'type': 'grammar_review',
            'level': self.current_level,
            'question': f"Study this grammar rule: {rule['title']}",
            'correct_answer': 'studied',
            'rule_data': rule,
            'grammar_rule': rule['title'],
            'explanation': rule['rule_text'],
            'examples': rule['examples'],
            'hint': 'Read the rule and examples carefully',
            'difficulty': 1,
            'points': 5
        }
        
        self.current_exercise = exercise
        return exercise
    
    def create_fallback_exercise(self) -> Dict:
        """Create fallback exercise when database is empty"""
        fallback_words = [
            ('hello', 'привіт'),
            ('book', 'книга'),
            ('water', 'вода'),
            ('study', 'вчитися'),
            ('friend', 'друг')
        ]
        
        english, ukrainian = random.choice(fallback_words)
        
        exercise = {
            'id': f"fallback_{datetime.now().timestamp()}",
            'type': 'vocabulary_translation',
            'level': self.current_level,
            'question': f"Translate to Ukrainian: {english}",
            'correct_answer': ukrainian,
            'word_data': {'english': english, 'ukrainian': ukrainian},
            'hints': ['Basic vocabulary word'],
            'difficulty': 1,
            'points': 5
        }
        
        self.current_exercise = exercise
        return exercise
    
    def check_answer(self, user_answer: str) -> Dict:
        """Check if the user's answer is correct"""
        if not self.current_exercise:
            return {
                'correct': False,
                'message': 'No active exercise',
                'score': 0
            }
        
        exercise = self.current_exercise
        correct_answer = exercise['correct_answer'].strip().lower()
        user_answer = user_answer.strip().lower()
        
        # Check answer with some flexibility
        is_correct = self.check_answer_similarity(user_answer, correct_answer)
        
        # Update session statistics
        self.session_stats['total_exercises'] += 1
        if is_correct:
            self.session_stats['correct_answers'] += 1
        
        # Update exercise type statistics
        if exercise['type'].startswith('vocabulary'):
            self.session_stats['vocabulary_studied'] += 1
        elif exercise['type'].startswith('phrase'):
            self.session_stats['phrases_studied'] += 1
        elif exercise['type'].startswith('grammar'):
            self.session_stats['grammar_studied'] += 1
        
        # Add to history
        result = {
            'exercise': exercise,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'timestamp': datetime.now().isoformat(),
            'points_earned': exercise['points'] if is_correct else 0
        }
        
        self.exercise_history.append(result)
        
        # Update database progress
        if 'word_data' in exercise and 'id' in exercise['word_data']:
            self.db.update_progress('default', 'vocabulary', exercise['word_data']['id'], is_correct)
        
        # Calculate response
        response = {
            'correct': is_correct,
            'message': self.generate_feedback_message(is_correct, correct_answer),
            'exercise_type': exercise['type'],
            'explanation': exercise.get('explanation', ''),
            'examples': exercise.get('examples', ''),
            'score': self.calculate_session_score(),
            'points_earned': exercise['points'] if is_correct else 0
        }
        
        return response
    
    def check_answer_similarity(self, user_answer: str, correct_answer: str) -> bool:
        """Check answer similarity with some flexibility"""
        # Exact match
        if user_answer == correct_answer:
            return True
        
        # Remove common punctuation and check again
        user_clean = user_answer.strip('.,!?;:')
        correct_clean = correct_answer.strip('.,!?;:')
        
        if user_clean == correct_clean:
            return True
        
        # For short answers, be more strict
        if len(correct_answer) <= 3:
            return user_answer == correct_answer
        
        # For longer answers, allow minor differences
        if len(user_answer) >= len(correct_answer) * 0.8:
            return user_clean == correct_clean
        
        return False
    
    def generate_feedback_message(self, is_correct: bool, correct_answer: str) -> str:
        """Generate appropriate feedback message"""
        if is_correct:
            messages = [
                "✓ Correct! Well done!",
                "✓ Excellent! That's right!",
                "✓ Perfect! You got it!",
                "✓ Great job! Correct answer!",
                "✓ Outstanding! That's correct!"
            ]
            return random.choice(messages)
        else:
            return f"✗ Incorrect. The correct answer is: {correct_answer}"
    
    def calculate_session_score(self) -> float:
        """Calculate current session score"""
        if self.session_stats['total_exercises'] == 0:
            return 0.0
        
        return (self.session_stats['correct_answers'] / self.session_stats['total_exercises']) * 100
    
    def get_session_statistics(self) -> Dict:
        """Get current session statistics"""
        return {
            'total_exercises': self.session_stats['total_exercises'],
            'correct_answers': self.session_stats['correct_answers'],
            'incorrect_answers': self.session_stats['total_exercises'] - self.session_stats['correct_answers'],
            'accuracy': self.calculate_session_score(),
            'vocabulary_studied': self.session_stats['vocabulary_studied'],
            'phrases_studied': self.session_stats['phrases_studied'],
            'grammar_studied': self.session_stats['grammar_studied'],
            'total_points': sum(ex.get('points_earned', 0) for ex in self.exercise_history)
        }
    
    def reset_session(self):
        """Reset the current learning session"""
        self.current_exercise = None
        self.exercise_history = []
        self.session_stats = {
            'total_exercises': 0,
            'correct_answers': 0,
            'vocabulary_studied': 0,
            'phrases_studied': 0,
            'grammar_studied': 0
        }
    
    def get_next_exercise(self, exercise_types: List[str] = None) -> Dict:
        """Get the next exercise in sequence"""
        if exercise_types is None:
            exercise_types = ['vocabulary_translation', 'vocabulary_multiple_choice', 
                           'phrase_translation', 'grammar_fill_blank']
        
        exercise_type = random.choice(exercise_types)
        return self.generate_exercise(exercise_type)
    
    def create_custom_exercise(self, exercise_config: Dict) -> Dict:
        """Create a custom exercise based on configuration"""
        exercise_type = exercise_config.get('type', 'vocabulary_translation')
        level = exercise_config.get('level', self.current_level)
        
        # Temporarily set level for this exercise
        original_level = self.current_level
        self.current_level = level
        
        exercise = self.generate_exercise(exercise_type)
        
        # Restore original level
        self.current_level = original_level
        
        # Apply custom configuration
        exercise.update(exercise_config)
        
        return exercise

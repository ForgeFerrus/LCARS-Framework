"""
Linguistic Matrix Progress Tracker
Advanced progress tracking and achievement system
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal

# progress tracker expects a database interface; use DatabaseManager
from .database_manager import DatabaseManager as LinguisticDatabase

class ProgressTracker(QObject):
    """Advanced progress tracking for Linguistic Matrix"""
    
    # Signals
    progress_updated = pyqtSignal()
    achievement_unlocked = pyqtSignal(str)  # achievement name
    level_up = pyqtSignal(str)  # new level
    milestone_reached = pyqtSignal(str)  # milestone description
    
    def __init__(self, database: LinguisticDatabase):
        super().__init__()
        self.db = database
        self.current_session_id = None
        self.session_start_time = None
        self.achievements = []
        
        # Learning thresholds and milestones
        self.level_thresholds = {
            'A1': {'vocabulary': 50, 'accuracy': 60, 'sessions': 3, 'points': 100},
            'A2': {'vocabulary': 200, 'accuracy': 65, 'sessions': 10, 'points': 500},
            'B1': {'vocabulary': 600, 'accuracy': 70, 'sessions': 25, 'points': 1500},
            'B2': {'vocabulary': 1200, 'accuracy': 75, 'sessions': 50, 'points': 3000},
            'C1': {'vocabulary': 2500, 'accuracy': 80, 'sessions': 100, 'points': 6000},
            'C2': {'vocabulary': 4000, 'accuracy': 85, 'sessions': 200, 'points': 10000}
        }
        
        # Achievement definitions
        self.achievement_definitions = {
            'first_word': {
                'name': 'First Steps',
                'description': 'Learn your first vocabulary word',
                'icon': '🎯',
                'points': 10
            },
            'vocabulary_collector': {
                'name': 'Vocabulary Collector',
                'description': 'Learn 10 vocabulary words',
                'icon': '📚',
                'points': 50
            },
            'word_master': {
                'name': 'Word Master',
                'description': 'Learn 100 vocabulary words',
                'icon': '🏆',
                'points': 200
            },
            'perfect_session': {
                'name': 'Perfect Session',
                'description': 'Complete a session with 100% accuracy',
                'icon': '⭐',
                'points': 100
            },
            'consistent_learner': {
                'name': 'Consistent Learner',
                'description': 'Study for 7 consecutive days',
                'icon': '📅',
                'points': 150
            },
            'grammar_expert': {
                'name': 'Grammar Expert',
                'description': 'Master 10 grammar rules',
                'icon': '📝',
                'points': 100
            },
            'phrase_master': {
                'name': 'Phrase Master',
                'description': 'Learn 25 phrases',
                'icon': '💬',
                'points': 75
            },
            'speed_learner': {
                'name': 'Speed Learner',
                'description': 'Complete 50 exercises in one session',
                'icon': '⚡',
                'points': 125
            },
            'accuracy_master': {
                'name': 'Accuracy Master',
                'description': 'Achieve 90% accuracy over 100 exercises',
                'icon': '🎯',
                'points': 200
            },
            'level_champion': {
                'name': 'Level Champion',
                'description': 'Complete a level with all requirements',
                'icon': '👑',
                'points': 300
            }
        }
        
        # Milestones
        self.milestones = {
            'first_session': 'Complete your first learning session',
            'week_warrior': 'Study for 7 days in a row',
            'month_dedicated': 'Study for 30 days in a row',
            'vocabulary_century': 'Learn 100 vocabulary words',
            'grammar_ninja': 'Master 20 grammar rules',
            'exercise_marathon': 'Complete 100 exercises',
            'accuracy_perfection': 'Achieve 95% accuracy in a session'
        }
    
    def start_session(self, user_id: str = 'default'):
        """Start a new learning session"""
        self.current_session_id = self.create_session(user_id)
        self.session_start_time = datetime.now()
    
    def create_session(self, user_id: str) -> int:
        """Create a new session record in database"""
        query = """
        INSERT INTO learning_sessions 
        (user_id, session_date, duration_minutes, vocabulary_studied, 
         phrases_studied, grammar_studied, exercises_completed, accuracy_score, level)
        VALUES (?, datetime('now'), 0, 0, 0, 0, 0, 0.0, 'A1')
        """
        
        if self.db.execute_update(query, (user_id,)):
            return self.db.connection.lastrowid
        return 0
    
    def end_session(self, duration_minutes: int, session_stats: Dict = None):
        """End the current learning session"""
        if not self.current_session_id:
            return
        
        if session_stats is None:
            session_stats = {
                'vocabulary_studied': 0,
                'phrases_studied': 0,
                'grammar_studied': 0,
                'exercises_completed': 0,
                'accuracy_score': 0.0
            }
        
        query = """
        UPDATE learning_sessions 
        SET duration_minutes = ?, vocabulary_studied = ?, phrases_studied = ?, 
            grammar_studied = ?, exercises_completed = ?, accuracy_score = ?
        WHERE id = ?
        """
        
        self.db.execute_update(query, (
            duration_minutes,
            session_stats.get('vocabulary_studied', 0),
            session_stats.get('phrases_studied', 0),
            session_stats.get('grammar_studied', 0),
            session_stats.get('exercises_completed', 0),
            session_stats.get('accuracy_score', 0.0),
            self.current_session_id
        ))
        
        # Check for session-based achievements
        self.check_session_achievements(session_stats)
        
        self.current_session_id = None
        self.session_start_time = None
        
        # Emit progress update
        self.progress_updated.emit()
    
    def get_overall_progress(self) -> float:
        """Calculate overall progress percentage"""
        summary = self.db.get_progress_summary()
        
        if 'vocabulary' not in summary:
            return 0.0
        
        vocab_stats = summary['vocabulary']
        total_vocabulary = vocab_stats.get('total_vocabulary', 0)
        learned_vocabulary = vocab_stats.get('learned_vocabulary', 0)
        
        if total_vocabulary == 0:
            return 0.0
        
        return (learned_vocabulary / total_vocabulary) * 100
    
    def get_current_level(self) -> str:
        """Determine user's current level based on progress"""
        summary = self.db.get_progress_summary()
        
        if 'vocabulary' not in summary:
            return 'A1'
        
        vocab_stats = summary['vocabulary']
        learned_vocabulary = vocab_stats.get('learned_vocabulary', 0)
        accuracy = vocab_stats.get('vocabulary_accuracy', 0) * 100
        
        # Check each level from highest to lowest
        for level in ['C2', 'C1', 'B2', 'B1', 'A2', 'A1']:
            threshold = self.level_thresholds[level]
            
            if (learned_vocabulary >= threshold['vocabulary'] and 
                accuracy >= threshold['accuracy']):
                return level
        
        return 'A1'
    
    def get_level_progress(self, level: str) -> Dict:
        """Get detailed progress for a specific level"""
        threshold = self.level_thresholds.get(level, {})
        summary = self.db.get_progress_summary()
        
        if 'vocabulary' not in summary:
            return {'percentage': 0, 'completed': 0, 'required': 0}
        
        vocab_stats = summary['vocabulary']
        learned_vocabulary = vocab_stats.get('learned_vocabulary', 0)
        accuracy = vocab_stats.get('vocabulary_accuracy', 0) * 100
        
        # Calculate progress for each requirement
        vocab_progress = min(100, (learned_vocabulary / threshold.get('vocabulary', 1)) * 100) if threshold.get('vocabulary') else 0
        accuracy_progress = min(100, (accuracy / threshold.get('accuracy', 1)) * 100) if threshold.get('accuracy') else 0
        
        # Session progress would need session tracking
        session_progress = 0  # Placeholder
        
        # Points progress
        total_points = self.get_total_points()
        points_progress = min(100, (total_points / threshold.get('points', 1)) * 100) if threshold.get('points') else 0
        
        # Overall level progress
        overall_progress = (vocab_progress + accuracy_progress + session_progress + points_progress) / 4
        
        return {
            'percentage': round(overall_progress, 2),
            'vocabulary': {
                'completed': learned_vocabulary,
                'required': threshold.get('vocabulary', 0),
                'progress': round(vocab_progress, 2)
            },
            'accuracy': {
                'completed': round(accuracy, 1),
                'required': threshold.get('accuracy', 0),
                'progress': round(accuracy_progress, 2)
            },
            'sessions': {
                'completed': 0,  # Would calculate from session data
                'required': threshold.get('sessions', 0),
                'progress': session_progress
            },
            'points': {
                'completed': total_points,
                'required': threshold.get('points', 0),
                'progress': round(points_progress, 2)
            }
        }
    
    def get_total_points(self) -> int:
        """Calculate total points earned"""
        # This would sum points from achievements and exercises
        # For now, return achievement points
        total = 0
        for achievement_id in self.achievements:
            if achievement_id in self.achievement_definitions:
                total += self.achievement_definitions[achievement_id]['points']
        
        return total
    
    def check_achievements(self):
        """Check and unlock achievements based on current progress"""
        summary = self.db.get_progress_summary()
        
        # Check various achievements
        self.check_vocabulary_achievements(summary)
        self.check_session_achievements()
        self.check_consistency_achievements()
        self.check_milestone_achievements()
    
    def check_vocabulary_achievements(self, summary: Dict):
        """Check vocabulary-related achievements"""
        if 'vocabulary' not in summary:
            return
        
        vocab_stats = summary['vocabulary']
        learned_vocabulary = vocab_stats.get('learned_vocabulary', 0)
        
        # First word
        if learned_vocabulary >= 1 and 'first_word' not in self.achievements:
            self.unlock_achievement('first_word')
        
        # Vocabulary collector (10 words)
        if learned_vocabulary >= 10 and 'vocabulary_collector' not in self.achievements:
            self.unlock_achievement('vocabulary_collector')
        
        # Word master (100 words)
        if learned_vocabulary >= 100 and 'word_master' not in self.achievements:
            self.unlock_achievement('word_master')
        
        # Vocabulary century milestone
        if learned_vocabulary >= 100:
            self.check_milestone('vocabulary_century')
    
    def check_session_achievements(self, session_stats: Dict = None):
        """Check session-based achievements"""
        if session_stats is None:
            return
        
        exercises_completed = session_stats.get('exercises_completed', 0)
        accuracy_score = session_stats.get('accuracy_score', 0)
        
        # Perfect session
        if accuracy_score >= 100 and 'perfect_session' not in self.achievements:
            self.unlock_achievement('perfect_session')
        
        # Speed learner
        if exercises_completed >= 50 and 'speed_learner' not in self.achievements:
            self.unlock_achievement('speed_learner')
        
        # Exercise marathon
        if exercises_completed >= 100:
            self.check_milestone('exercise_marathon')
        
        # Accuracy perfection
        if accuracy_score >= 95:
            self.check_milestone('accuracy_perfection')
    
    def check_consistency_achievements(self):
        """Check consistency-based achievements"""
        # This would require tracking daily activity
        # For now, placeholder implementation
        recent_sessions = self.db.execute_query("""
            SELECT COUNT(DISTINCT date(session_date)) as study_days
            FROM learning_sessions 
            WHERE user_id = 'default' 
            AND session_date >= date('now', '-7 days')
        """)
        
        if recent_sessions:
            study_days = recent_sessions[0]['study_days']
            if study_days >= 7 and 'consistent_learner' not in self.achievements:
                self.unlock_achievement('consistent_learner')
            
            if study_days >= 7:
                self.check_milestone('week_warrior')
    
    def check_milestone_achievements(self):
        """Check milestone achievements"""
        # This would track various milestones
        pass
    
    def check_milestone(self, milestone_key: str):
        """Check and emit milestone reached"""
        if milestone_key in self.milestones:
            self.milestone_reached.emit(self.milestones[milestone_key])
    
    def unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        if achievement_id in self.achievement_definitions:
            achievement = self.achievement_definitions[achievement_id]
            
            # Add to achievements list
            self.achievements.append(achievement_id)
            
            # Store in database
            self.db.execute_update(
                "INSERT OR REPLACE INTO achievements (user_id, achievement_code, achievement_name, description, unlocked_at) VALUES (?, ?, ?, ?, ?)",
                ('default', achievement_id, achievement['name'], achievement['description'], datetime.now().isoformat())
            )
            
            # Emit signal
            self.achievement_unlocked.emit(achievement['name'])
            
            # Emit progress update
            self.progress_updated.emit()
    
    def get_achievements(self) -> List[Dict]:
        """Get all achievements with unlock status"""
        achievements = []
        
        for achievement_id, definition in self.achievement_definitions.items():
            achievements.append({
                'id': achievement_id,
                'name': definition['name'],
                'description': definition['description'],
                'icon': definition['icon'],
                'points': definition['points'],
                'unlocked': achievement_id in self.achievements,
                'unlocked_at': self.get_achievement_unlock_time(achievement_id)
            })
        
        return achievements
    
    def get_achievement_unlock_time(self, achievement_id: str) -> Optional[str]:
        """Get when an achievement was unlocked"""
        result = self.db.execute_single(
            "SELECT unlocked_at FROM achievements WHERE user_id = ? AND achievement_code = ?",
            ('default', achievement_id)
        )
        
        return result['unlocked_at'] if result else None
    
    def get_learning_statistics(self) -> Dict:
        """Get comprehensive learning statistics"""
        summary = self.db.get_progress_summary()
        
        # Add achievement statistics
        achievements = self.get_achievements()
        unlocked_achievements = [a for a in achievements if a['unlocked']]
        total_achievement_points = sum(a['points'] for a in unlocked_achievements)
        
        # Add session statistics
        session_stats = self.db.execute_single("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(duration_minutes) as total_minutes,
                AVG(accuracy_score) as avg_accuracy,
                SUM(exercises_completed) as total_exercises
            FROM learning_sessions 
            WHERE user_id = 'default'
        """)
        
        stats = {
            'vocabulary': summary.get('vocabulary', {}),
            'achievements': {
                'total': len(achievements),
                'unlocked': len(unlocked_achievements),
                'points': total_achievement_points
            },
            'sessions': dict(session_stats) if session_stats else {},
            'current_level': self.get_current_level(),
            'overall_progress': self.get_overall_progress(),
            'total_points': self.get_total_points()
        }
        
        return stats
    
    def get_next_level_requirements(self) -> Dict:
        """Get requirements for the next level"""
        current_level = self.get_current_level()
        level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        
        current_index = level_order.index(current_level)
        if current_index < len(level_order) - 1:
            next_level = level_order[current_index + 1]
            return {
                'next_level': next_level,
                'requirements': self.level_thresholds[next_level],
                'current_progress': self.get_level_progress(current_level)
            }
        
        return {
            'next_level': 'C2',
            'requirements': self.level_thresholds['C2'],
            'current_progress': self.get_level_progress(current_level)
        }
    
    def get_weekly_progress(self) -> Dict:
        """Get progress for the past week"""
        result = self.db.execute_single("""
            SELECT 
                COUNT(*) as session_count,
                SUM(duration_minutes) as total_minutes,
                SUM(vocabulary_studied) as total_vocabulary,
                SUM(phrases_studied) as total_phrases,
                SUM(grammar_studied) as total_grammar,
                SUM(exercises_completed) as total_exercises,
                AVG(accuracy_score) as avg_accuracy
            FROM learning_sessions 
            WHERE user_id = 'default' 
            AND session_date >= date('now', '-7 days')
        """)
        
        return dict(result) if result else {}
    
    def get_monthly_progress(self) -> Dict:
        """Get progress for the past month"""
        result = self.db.execute_single("""
            SELECT 
                COUNT(*) as session_count,
                SUM(duration_minutes) as total_minutes,
                SUM(vocabulary_studied) as total_vocabulary,
                SUM(phrases_studied) as total_phrases,
                SUM(grammar_studied) as total_grammar,
                SUM(exercises_completed) as total_exercises,
                AVG(accuracy_score) as avg_accuracy
            FROM learning_sessions 
            WHERE user_id = 'default' 
            AND session_date >= date('now', '-30 days')
        """)
        
        return dict(result) if result else {}
    
    def export_progress_data(self) -> Dict:
        """Export all progress data"""
        return {
            'user_id': 'default',
            'export_date': datetime.now().isoformat(),
            'current_level': self.get_current_level(),
            'overall_progress': self.get_overall_progress(),
            'achievements': self.get_achievements(),
            'statistics': self.get_learning_statistics(),
            'weekly_progress': self.get_weekly_progress(),
            'monthly_progress': self.get_monthly_progress(),
            'next_level_requirements': self.get_next_level_requirements()
        }


from typing import Dict, List, Optional
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal
from .database_manager import DatabaseManager

class ProgressTracker(QObject):
    """Tracks and manages user learning progress"""
    
    # Signals
    progress_updated = pyqtSignal()
    achievement_unlocked = pyqtSignal(str)  # achievement name
    level_up = pyqtSignal(str)  # new level
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.current_session_id = None
        self.session_start_time = None
        self.achievements = []
        
        # Learning thresholds for levels
        self.level_thresholds = {
            'A1': {'words': 100, 'accuracy': 70, 'sessions': 5},
            'A2': {'words': 300, 'accuracy': 75, 'sessions': 15},
            'B1': {'words': 800, 'accuracy': 80, 'sessions': 30},
            'B2': {'words': 1500, 'accuracy': 85, 'sessions': 50},
            'C1': {'words': 2500, 'accuracy': 90, 'sessions': 80},
            'C2': {'words': 4000, 'accuracy': 95, 'sessions': 120}
        }
        
        # Achievement definitions
        self.achievement_definitions = {
            'first_word': {'name': 'First Steps', 'description': 'Learn your first word'},
            'ten_words': {'name': 'Word Collector', 'description': 'Learn 10 words'},
            'hundred_words': {'name': 'Vocabulary Master', 'description': 'Learn 100 words'},
            'perfect_session': {'name': 'Perfect Session', 'description': 'Complete a session with 100% accuracy'},
            'week_streak': {'name': 'Week Warrior', 'description': 'Study for 7 consecutive days'},
            'month_streak': {'name': 'Dedicated Learner', 'description': 'Study for 30 consecutive days'},
            'grammar_expert': {'name': 'Grammar Expert', 'description': 'Master 10 grammar rules'},
            'phrase_master': {'name': 'Phrase Master', 'description': 'Learn 50 phrases'}
        }
    
    def start_session(self):
        """Start a new learning session"""
        self.current_session_id = self.db.start_learning_session()
        self.session_start_time = datetime.now()
    
    def end_session(self, duration_minutes: int):
        """End the current learning session"""
        if self.current_session_id:
            # Get session statistics
            session_stats = self.get_session_statistics()
            
            # Update session in database
            self.db.update_session(
                self.current_session_id,
                duration_minutes,
                session_stats.get('words_learned', 0),
                session_stats.get('phrases_learned', 0),
                session_stats.get('grammar_rules_learned', 0),
                session_stats.get('exercises_completed', 0),
                session_stats.get('score', 0)
            )
            
            self.current_session_id = None
            self.session_start_time = None
            
            # Check for achievements
            self.check_achievements()
            
            # Emit progress update
            self.progress_updated.emit()
    
    def record_word_learned(self, word_id: int, correct: bool):
        """Record that a word was practiced"""
        self.db.update_word_progress('default', word_id, correct)
        
        # Check for achievements
        self.check_word_achievements()
        
        # Emit progress update
        self.progress_updated.emit()
    
    def record_phrase_learned(self, phrase_id: int, correct: bool):
        """Record that a phrase was practiced"""
        # Similar to word learning but for phrases
        self.progress_updated.emit()
    
    def record_grammar_learned(self, grammar_rule_id: int):
        """Record that a grammar rule was studied"""
        # Mark grammar rule as learned
        self.progress_updated.emit()
    
    def get_overall_progress(self) -> float:
        """Calculate overall progress percentage"""
        stats = self.get_learning_statistics()
        
        if not stats or 'words' not in stats:
            return 0.0
        
        words_stats = stats['words']
        total_words = words_stats.get('total_words', 0)
        learned_words = words_stats.get('learned_words', 0)
        
        if total_words == 0:
            return 0.0
        
        return (learned_words / total_words) * 100
    
    def get_current_level(self) -> str:
        """Determine user's current level based on progress"""
        stats = self.get_learning_statistics()
        
        if not stats or 'words' not in stats:
            return 'A1'
        
        words_stats = stats['words']
        learned_words = words_stats.get('learned_words', 0)
        accuracy = words_stats.get('accuracy_rate', 0) * 100
        
        # Check each level from highest to lowest
        for level in ['C2', 'C1', 'B2', 'B1', 'A2', 'A1']:
            threshold = self.level_thresholds[level]
            
            if (learned_words >= threshold['words'] and 
                accuracy >= threshold['accuracy']):
                return level
        
        return 'A1'
    
    def get_level_progress(self, level: str) -> Dict:
        """Get progress for a specific level"""
        threshold = self.level_thresholds.get(level, {})
        stats = self.get_learning_statistics()
        
        if not stats or 'words' not in stats:
            return {'percentage': 0, 'words_learned': 0, 'words_required': threshold.get('words', 0)}
        
        words_stats = stats['words']
        learned_words = words_stats.get('learned_words', 0)
        accuracy = words_stats.get('accuracy_rate', 0) * 100
        recent_sessions = stats.get('recent_activity', {}).get('recent_sessions', 0)
        
        # Calculate progress percentage for this level
        words_progress = min(100, (learned_words / threshold.get('words', 1)) * 100) if threshold.get('words') else 0
        accuracy_progress = min(100, (accuracy / threshold.get('accuracy', 1)) * 100) if threshold.get('accuracy') else 0
        sessions_progress = min(100, (recent_sessions / threshold.get('sessions', 1)) * 100) if threshold.get('sessions') else 0
        
        overall_progress = (words_progress + accuracy_progress + sessions_progress) / 3
        
        return {
            'percentage': round(overall_progress, 2),
            'words_learned': learned_words,
            'words_required': threshold.get('words', 0),
            'accuracy': round(accuracy, 2),
            'accuracy_required': threshold.get('accuracy', 0),
            'sessions': recent_sessions,
            'sessions_required': threshold.get('sessions', 0)
        }
    
    def get_learning_statistics(self) -> Dict:
        """Get comprehensive learning statistics"""
        return self.db.get_learning_statistics()
    
    def get_session_statistics(self) -> Dict:
        """Get statistics for the current session"""
        # This would track current session data
        # For now, return placeholder data
        return {
            'words_learned': 0,
            'phrases_learned': 0,
            'grammar_rules_learned': 0,
            'exercises_completed': 0,
            'score': 0
        }
    
    def get_words_for_review(self, level: str = 'A1') -> List[Dict]:
        """Get words that need review"""
        return self.db.get_words_for_review('default', level)
    
    def get_weekly_progress(self) -> Dict:
        """Get progress for the past week"""
        return self.db.get_session_stats('default', days=7)
    
    def get_monthly_progress(self) -> Dict:
        """Get progress for the past month"""
        return self.db.get_session_stats('default', days=30)
    
    def check_achievements(self):
        """Check and unlock achievements"""
        stats = self.get_learning_statistics()
        
        # Check various achievements
        self.check_first_word_achievement(stats)
        self.check_word_count_achievements(stats)
        self.check_session_achievements(stats)
        self.check_streak_achievements(stats)
    
    def check_first_word_achievement(self, stats: Dict):
        """Check if first word achievement should be unlocked"""
        if 'first_word' not in self.achievements:
            words_stats = stats.get('words', {})
            if words_stats.get('learned_words', 0) >= 1:
                self.unlock_achievement('first_word')
    
    def check_word_count_achievements(self, stats: Dict):
        """Check word count achievements"""
        words_stats = stats.get('words', {})
        learned_words = words_stats.get('learned_words', 0)
        
        if learned_words >= 10 and 'ten_words' not in self.achievements:
            self.unlock_achievement('ten_words')
        
        if learned_words >= 100 and 'hundred_words' not in self.achievements:
            self.unlock_achievement('hundred_words')
    
    def check_session_achievements(self, stats: Dict):
        """Check session-related achievements"""
        # This would check for perfect sessions, etc.
        pass
    
    def check_streak_achievements(self, stats: Dict):
        """Check learning streak achievements"""
        # This would check consecutive days
        pass
    
    def check_word_achievements(self):
        """Check word-specific achievements"""
        # This is called when a word is learned
        pass
    
    def unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        if achievement_id in self.achievement_definitions:
            achievement = self.achievement_definitions[achievement_id]
            self.achievements.append(achievement_id)
            self.achievement_unlocked.emit(achievement['name'])
    
    def get_achievements(self) -> List[Dict]:
        """Get all achievements"""
        achievements = []
        for achievement_id, definition in self.achievement_definitions.items():
            achievements.append({
                'id': achievement_id,
                'name': definition['name'],
                'description': definition['description'],
                'unlocked': achievement_id in self.achievements
            })
        return achievements
    
    def get_next_level_requirements(self) -> Dict:
        """Get requirements for the next level"""
        current_level = self.get_current_level()
        level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        
        current_index = level_order.index(current_level)
        if current_index < len(level_order) - 1:
            next_level = level_order[current_index + 1]
            return {
                'next_level': next_level,
                'requirements': self.level_thresholds[next_level]
            }
        
        return {'next_level': 'C2', 'requirements': self.level_thresholds['C2']}
    
    def reset_progress(self):
        """Reset all progress (for testing)"""
        # This would reset the user's progress
        self.achievements = []
        self.progress_updated.emit()
    
    def export_progress(self) -> Dict:
        """Export progress data"""
        return {
            'current_level': self.get_current_level(),
            'overall_progress': self.get_overall_progress(),
            'achievements': self.get_achievements(),
            'statistics': self.get_learning_statistics(),
            'weekly_progress': self.get_weekly_progress(),
            'monthly_progress': self.get_monthly_progress()
        }

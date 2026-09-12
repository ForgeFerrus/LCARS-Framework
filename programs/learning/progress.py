# Linguistic Matrix Progress Tracker
# Advanced progress tracking and achievement system

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta

# progress tracker expects a database interface; use DatabaseManager
from programs.learning.logic import DatabaseManager

class Signal:
    'Simple callback signal for progress events.'
    def __init__(self):
        self.Slots = []

    def connect(self, callback):
        if callable(callback) and callback not in self.Slots:
            self.Slots.append(callback)

    def disconnect(self, callback):
        self.Slots = [slot for slot in self.Slots if slot != callback]

    def emit(self, *args, **kwargs):
        for slot in list(self.Slots):
            slot(*args, **kwargs)


class ProgressTracker:
    # Advanced progress tracking for Linguistic Matrix

    def __init__(self, database: DatabaseManager, userId: str = 'default'):
        self.db = database
        self.userId = userId
        self.currentSessionId = None
        self.sessionStartTime = None
        self.achievements = []
        self.progressUpdated = Signal()
        self.achievementUnlocked = Signal()
        self.levelUp = Signal()
        self.milestoneReached = Signal()

        # Load previously unlocked achievements from the database
        self.loadAchievements()

        # Learning thresholds and milestones
        self.levelThresholds = {
            'A1': {'vocabulary': 50, 'accuracy': 60, 'sessions': 3, 'points': 100},
            'A2': {'vocabulary': 200, 'accuracy': 65, 'sessions': 10, 'points': 500},
            'B1': {'vocabulary': 600, 'accuracy': 70, 'sessions': 25, 'points': 1500},
            'B2': {'vocabulary': 1200, 'accuracy': 75, 'sessions': 50, 'points': 3000},
            'C1': {'vocabulary': 2500, 'accuracy': 80, 'sessions': 100, 'points': 6000},
            'C2': {'vocabulary': 4000, 'accuracy': 85, 'sessions': 200, 'points': 10000}
        }
        
        # Achievement definitions
        self.achievementDefinitions = {
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
    
    def startSession(self, userId: str = 'default'):
        # Start a new learning session
        self.userId = userId
        self.currentSessionId = self.createSession(userId)
        self.sessionStartTime = datetime.now()
    
    def createSession(self, userId: str) -> int:
        # Create a new session record in database
        query = "\n        INSERT INTO learning_sessions \n        (user_id, session_date, duration_minutes, vocabulary_studied, \n         phrases_studied, grammar_studied, exercises_completed, accuracy_score, level)\n        VALUES (?, datetime('now'), 0, 0, 0, 0, 0, 0.0, 'A1')\n        "
        
        sessionId = self.db.executeUpdate(query, (userId,))
        return sessionId
    
    def endSession(self, durationMinutes: int = 0, sessionStats: Optional[Dict] = None):
        # End the current learning session
        if not self.currentSessionId:
            return
        
        if durationMinutes <= 0 and self.sessionStartTime is not None:
            durationMinutes = int((datetime.now() - self.sessionStartTime).total_seconds() // 60)

        if sessionStats is None:
            sessionStats = {
                'vocabulary_studied': 0,
                'phrases_studied': 0,
                'grammar_studied': 0,
                'exercises_completed': 0,
                'accuracy_score': 0.0
            }
        
        query = '\n        UPDATE learning_sessions \n        SET duration_minutes = ?, vocabulary_studied = ?, phrases_studied = ?, \n            grammar_studied = ?, exercises_completed = ?, accuracy_score = ?, level = ?\n        WHERE id = ?\n        '
        
        self.db.executeUpdate(query, (
            durationMinutes,
            sessionStats.get('vocabulary_studied', 0),
            sessionStats.get('phrases_studied', 0),
            sessionStats.get('grammar_studied', 0),
            sessionStats.get('exercises_completed', 0),
            sessionStats.get('accuracy_score', 0.0),
            self.getCurrentLevel(),
            self.currentSessionId
        ))
        
        # Check for session-based achievements and update overall progress
        self.checkSessionAchievements(sessionStats)
        self.checkAchievements()
        
        self.currentSessionId = None
        self.sessionStartTime = None
        
        # Emit progress update
        self.progressUpdated.emit()
    
    def getOverallProgress(self) -> float:
        # Calculate overall progress percentage
        summary = self.db.getProgressSummary(self.userId)
        
        if 'vocabulary' not in summary:
            return 0.0
        
        vocabStats = summary['vocabulary']
        totalVocabulary = vocabStats.get('total_vocabulary', 0)
        learnedVocabulary = vocabStats.get('learned_vocabulary', 0)
        
        if totalVocabulary == 0:
            return 0.0
        
        return (learnedVocabulary / totalVocabulary) * 100
    
    def getCurrentLevel(self) -> str:
        # Determine user's current level based on progress
        summary = self.db.getProgressSummary(self.userId)
        
        if 'vocabulary' not in summary:
            return 'A1'
        
        vocabStats = summary['vocabulary']
        learnedVocabulary = vocabStats.get('learned_vocabulary', 0)
        accuracy = vocabStats.get('vocabulary_accuracy', 0) * 100
        
        # Check each level from highest to lowest
        for level in ['C2', 'C1', 'B2', 'B1', 'A2', 'A1']:
            threshold = self.levelThresholds[level]
            
            if (learnedVocabulary >= threshold['vocabulary'] and 
                accuracy >= threshold['accuracy']):
                return level
        
        return 'A1'
    
    def getLevelProgress(self, level: str) -> Dict:
        # Get detailed progress for a specific level
        threshold = self.levelThresholds.get(level, {})
        summary = self.db.getProgressSummary(self.userId)
        
        if 'vocabulary' not in summary:
            return {'percentage': 0, 'completed': 0, 'required': 0}
        
        vocabStats = summary['vocabulary']
        learnedVocabulary = vocabStats.get('learned_vocabulary', 0)
        accuracy = vocabStats.get('vocabulary_accuracy', 0) * 100
        
        # Calculate progress for each requirement
        vocabProgress = min(100, (learnedVocabulary / threshold.get('vocabulary', 1)) * 100) if threshold.get('vocabulary') else 0
        accuracyProgress = min(100, (accuracy / threshold.get('accuracy', 1)) * 100) if threshold.get('accuracy') else 0
        
        # Session progress would need session tracking
        sessionProgress = 0  # Placeholder
        
        # Session progress based on historical sessions
        sessionCount = self.db.executeSingle(
            "SELECT COUNT(*) as count FROM learning_sessions WHERE user_id = ?",
            (self.userId,)
        )
        sessionCountValue = sessionCount['count'] if sessionCount and sessionCount['count'] else 0
        sessionProgress = min(100, (sessionCountValue / threshold.get('sessions', 1)) * 100) if threshold.get('sessions') else 0
        
        # Points progress
        totalPoints = self.getTotalPoints()
        pointsProgress = min(100, (totalPoints / threshold.get('points', 1)) * 100) if threshold.get('points') else 0
        
        # Overall level progress
        overallProgress = (vocabProgress + accuracyProgress + sessionProgress + pointsProgress) / 4
        
        return {
            'percentage': round(overallProgress, 2),
            'vocabulary': {
                'completed': learnedVocabulary,
                'required': threshold.get('vocabulary', 0),
                'progress': round(vocabProgress, 2)
            },
            'accuracy': {
                'completed': round(accuracy, 1),
                'required': threshold.get('accuracy', 0),
                'progress': round(accuracyProgress, 2)
            },
            'sessions': {
                'completed': sessionCountValue,
                'required': threshold.get('sessions', 0),
                'progress': sessionProgress
            },
            'points': {
                'completed': totalPoints,
                'required': threshold.get('points', 0),
                'progress': round(pointsProgress, 2)
            }
        }
    
    def getTotalPoints(self) -> int:
        # Calculate total points earned from achievements
        total = 0
        for achievementId in self.achievements:
            if achievementId in self.achievementDefinitions:
                total += self.achievementDefinitions[achievementId]['points']
        return total

    def loadAchievements(self):
        # Load unlocked achievements from the database for the current user
        results = self.db.executeQuery(
            "SELECT achievement_code FROM achievements WHERE user_id = ?",
            (self.userId,)
        )
        self.achievements = [row.get('achievement_code') for row in results if row.get('achievement_code')]

    def getStudyStreakDays(self) -> int:
        # Calculate consecutive days of study ending today
        rows = self.db.executeQuery(
            "SELECT DISTINCT date(session_date) as session_day FROM learning_sessions WHERE user_id = ? AND session_date <= date('now') ORDER BY session_day DESC LIMIT 30",
            (self.userId,)
        )
        studyDays: List[str] = []
        for row in rows:
            sessionDay = row.get('session_day')
            if isinstance(sessionDay, str):
                studyDays.append(sessionDay)
        if not studyDays:
            return 0

        streak = 0
        today = date.today()
        for sessionDay in studyDays:
            sessionDate = datetime.strptime(sessionDay, "%Y-%m-%d").date()
            if sessionDate > today:
                continue
            expectedDate = today
            if streak > 0:
                expectedDate = today - timedelta(days=streak)
            if sessionDate == expectedDate:
                streak += 1
            else:
                break
        return streak

    def getLevelDisplayName(self, level: str) -> str:
        labels = {
            'A1': 'Beginner (A1)',
            'A2': 'Elementary (A2)',
            'B1': 'Intermediate (B1)',
            'B2': 'Upper Intermediate (B2)',
            'C1': 'Advanced (C1)',
            'C2': 'Proficient (C2)'
        }
        return labels.get(level, level)

    def checkAchievements(self):
        # Check and unlock achievements based on current progress
        summary = self.db.getProgressSummary(self.userId)
        
        # Check various achievements
        self.checkVocabularyAchievements(summary)
        self.checkSessionAchievements()
        self.checkConsistencyAchievements()
        self.checkMilestoneAchievements()
    
    def checkVocabularyAchievements(self, summary: Dict):
        # Check vocabulary-related achievements
        if 'vocabulary' not in summary:
            return
        
        vocabStats = summary['vocabulary']
        learnedVocabulary = vocabStats.get('learned_vocabulary', 0)
        
        # First word
        if learnedVocabulary >= 1 and 'first_word' not in self.achievements:
            self.unlockAchievement('first_word')
        
        # Vocabulary collector (10 words)
        if learnedVocabulary >= 10 and 'vocabulary_collector' not in self.achievements:
            self.unlockAchievement('vocabulary_collector')
        
        # Word master (100 words)
        if learnedVocabulary >= 100 and 'word_master' not in self.achievements:
            self.unlockAchievement('word_master')
        
        # Vocabulary century milestone
        if learnedVocabulary >= 100:
            self.checkMilestone('vocabulary_century')
    
    def checkSessionAchievements(self, sessionStats: Optional[Dict] = None):
        # Check session-based achievements
        if sessionStats is None:
            return
        
        exercisesCompleted = sessionStats.get('exercises_completed', 0)
        accuracyScore = sessionStats.get('accuracy_score', 0)
        
        # Perfect session
        if accuracyScore >= 100 and 'perfect_session' not in self.achievements:
            self.unlockAchievement('perfect_session')
        
        # Speed learner
        if exercisesCompleted >= 50 and 'speed_learner' not in self.achievements:
            self.unlockAchievement('speed_learner')
        
        # Exercise marathon
        if exercisesCompleted >= 100:
            self.checkMilestone('exercise_marathon')
        
        # Accuracy perfection
        if accuracyScore >= 95:
            self.checkMilestone('accuracy_perfection')
    
    def checkConsistencyAchievements(self):
        # Check consistency-based achievements
        recentSessions = self.db.executeQuery("\n            SELECT COUNT(DISTINCT date(session_date)) as study_days\n            FROM learning_sessions \n            WHERE user_id = ? \n            AND session_date >= date('now', '-7 days')\n        ", (self.userId,))
        
        if recentSessions:
            studyDays = recentSessions[0]['study_days']
            if studyDays >= 7 and 'consistent_learner' not in self.achievements:
                self.unlockAchievement('consistent_learner')
            
            if studyDays >= 7:
                self.checkMilestone('week_warrior')
    
    def checkMilestoneAchievements(self):
        # Check milestone achievements
        # This would track various milestones
        pass
    
    def checkMilestone(self, milestoneKey: str):
        # Check and emit milestone reached
        if milestoneKey in self.milestones:
            self.milestoneReached.emit(self.milestones[milestoneKey])
    
    def unlockAchievement(self, achievementId: str):
        # Unlock an achievement
        if achievementId in self.achievementDefinitions and achievementId not in self.achievements:
            achievement = self.achievementDefinitions[achievementId]
            
            # Add to achievements list
            self.achievements.append(achievementId)
            
            # Store in database
            self.db.executeUpdate(
                "INSERT OR REPLACE INTO achievements (user_id, achievement_code, achievement_name, description, unlocked_at) VALUES (?, ?, ?, ?, ?)",
                (self.userId, achievementId, achievement['name'], achievement['description'], datetime.now().isoformat())
            )
            
            # Emit signal
            self.achievementUnlocked.emit(achievement['name'])
            
            # Emit progress update
            self.progressUpdated.emit()
    
    def getAchievements(self) -> List[Dict]:
        # Get all achievements with unlock status
        achievements = []
        
        for achievementId, definition in self.achievementDefinitions.items():
            achievements.append({
                'id': achievementId,
                'name': definition['name'],
                'description': definition['description'],
                'icon': definition['icon'],
                'points': definition['points'],
                'unlocked': achievementId in self.achievements,
                'unlocked_at': self.getAchievementUnlockTime(achievementId)
            })
        
        return achievements
    
    def getAchievementUnlockTime(self, achievementId: str) -> Optional[str]:
        # Get when an achievement was unlocked
        result = self.db.executeSingle(
            "SELECT unlocked_at FROM achievements WHERE user_id = ? AND achievement_code = ?",
            (self.userId, achievementId)
        )
        
        return result['unlocked_at'] if result else None
    
    def getLearningStatistics(self) -> Dict:
        # Get comprehensive learning statistics
        summary = self.db.getProgressSummary(self.userId)
        
        # Add achievement statistics
        achievements = self.getAchievements()
        unlockedAchievements = [a for a in achievements if a['unlocked']]
        totalAchievementPoints = sum(a['points'] for a in unlockedAchievements)
        
        # Add session statistics
        sessionStats = self.db.executeSingle("\n            SELECT \n                COUNT(*) as total_sessions,\n                SUM(duration_minutes) as total_minutes,\n                AVG(accuracy_score) as avg_accuracy,\n                SUM(exercises_completed) as total_exercises\n            FROM learning_sessions \n            WHERE user_id = ?\n        ", (self.userId,))
        
        stats = {
            'vocabulary': summary.get('vocabulary', {}),
            'achievements': {
                'total': len(achievements),
                'unlocked': len(unlockedAchievements),
                'points': totalAchievementPoints
            },
            'sessions': dict(sessionStats) if sessionStats else {},
            'current_level': self.getCurrentLevel(),
            'overall_progress': self.getOverallProgress(),
            'total_points': self.getTotalPoints()
        }
        
        return stats
    
    def getNextLevelRequirements(self) -> Dict:
        # Get requirements for the next level
        currentLevel = self.getCurrentLevel()
        levelOrder = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        
        currentIndex = levelOrder.index(currentLevel)
        if currentIndex < len(levelOrder) - 1:
            nextLevel = levelOrder[currentIndex + 1]
            return {
                'next_level': nextLevel,
                'requirements': self.levelThresholds[nextLevel],
                'current_progress': self.getLevelProgress(currentLevel)
            }
        
        return {
            'next_level': 'C2',
            'requirements': self.levelThresholds['C2'],
            'current_progress': self.getLevelProgress(currentLevel)
        }
    
    def getWeeklyProgress(self) -> Dict:
        # Get progress for the past week
        result = self.db.executeSingle("\n            SELECT \n                COUNT(*) as session_count,\n                SUM(duration_minutes) as total_minutes,\n                SUM(vocabulary_studied) as total_vocabulary,\n                SUM(phrases_studied) as total_phrases,\n                SUM(grammar_studied) as total_grammar,\n                SUM(exercises_completed) as total_exercises,\n                AVG(accuracy_score) as avg_accuracy\n            FROM learning_sessions \n            WHERE user_id = ? \n            AND session_date >= date('now', '-7 days')\n        ", (self.userId,))
        
        return dict(result) if result else {}
    
    def getMonthlyProgress(self) -> Dict:
        # Get progress for the past month
        result = self.db.executeSingle("\n            SELECT \n                COUNT(*) as session_count,\n                SUM(duration_minutes) as total_minutes,\n                SUM(vocabulary_studied) as total_vocabulary,\n                SUM(phrases_studied) as total_phrases,\n                SUM(grammar_studied) as total_grammar,\n                SUM(exercises_completed) as total_exercises,\n                AVG(accuracy_score) as avg_accuracy\n            FROM learning_sessions \n            WHERE user_id = ? \n            AND session_date >= date('now', '-30 days')\n        ", (self.userId,))
        
        return dict(result) if result else {}
    
    def exportProgressData(self) -> Dict:
        # Export all progress data
        return {
            'user_id': self.userId,
            'export_date': datetime.now().isoformat(),
            'current_level': self.getCurrentLevel(),
            'overall_progress': self.getOverallProgress(),
            'achievements': self.getAchievements(),
            'statistics': self.getLearningStatistics(),
            'weekly_progress': self.getWeeklyProgress(),
            'monthly_progress': self.getMonthlyProgress(),
            'next_level_requirements': self.getNextLevelRequirements()
        }



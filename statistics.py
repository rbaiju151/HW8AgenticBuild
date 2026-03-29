"""
Statistics tracking module.
Tracks user performance metrics including accuracy, completion time, and category-specific stats.
Uses pickle for non-human readable storage.

Design Notes on Scoring:
- Accuracy Weight (70%): Emphasizes correctness of answers
- Speed Weight (30%): Encourages fast quiz completion
- Time Normalization (10): Converts average time/question to reasonable scale
  * Example: If avg time is 10 seconds/question, time_score = 100 / (1 + 10/10) = 50/100
  * This balances the scoring so both components meaningfully contribute
"""

import time
from pathlib import Path
from typing import Dict, List, Optional

from data_storage import load_pickle_file, save_pickle_file

# Leaderboard scoring constants
ACCURACY_WEIGHT = 0.7  # 70% of score based on accuracy
SPEED_WEIGHT = 0.3  # 30% of score based on speed
TIME_NORMALIZATION = 10  # Normalize time values to reasonable scale
TIME_SCORE_MAX = 100  # Maximum time score


def get_statistics_file_path() -> Path:
    """Get the path to the statistics file."""
    return Path(__file__).parent / "statistics_data.pkl"


def load_statistics() -> dict:
    """
    Load statistics from the pickle file.
    
    Returns:
        Dictionary mapping usernames to their statistics.
        Returns empty dict if file doesn't exist.
    """
    return load_pickle_file(get_statistics_file_path())


def save_statistics(statistics: dict) -> None:
    """
    Save statistics to the pickle file.
    
    Args:
        statistics: Dictionary mapping usernames to their statistics
        
    Raises:
        IOError: If file cannot be written
    """
    save_pickle_file(get_statistics_file_path(), statistics)


def get_user_stats(username: str) -> dict:
    """
    Get statistics for a specific user.
    
    Args:
        username: The username to get stats for
        
    Returns:
        Dictionary containing user statistics, or empty dict if user has no stats
    """
    statistics = load_statistics()
    username_lower = username.lower()
    
    if username_lower not in statistics:
        return {
            "total_questions": 0,
            "correct_answers": 0,
            "total_time": 0,
            "quizzes_completed": 0,
            "category_stats": {}
        }
    
    return statistics[username_lower]


def record_quiz_result(username: str, correct: int, total: int, time_taken: float, 
                       category: str, question_ids: List[int]) -> None:
    """
    Record the results of a quiz attempt.
    
    Args:
        username: The username of the quiz taker
        correct: Number of correct answers
        total: Total number of questions in quiz
        time_taken: Time taken to complete quiz in seconds
        category: Category of questions (or 'Mixed' if multiple)
        question_ids: List of question IDs that were asked
        
    Raises:
        IOError: If statistics file cannot be written
    """
    statistics = load_statistics()
    username_lower = username.lower()
    
    if username_lower not in statistics:
        statistics[username_lower] = {
            "total_questions": 0,
            "correct_answers": 0,
            "total_time": 0,
            "quizzes_completed": 0,
            "category_stats": {},
            "quiz_history": []
        }
    
    user_stats = statistics[username_lower]
    
    # Update overall stats
    user_stats["total_questions"] += total
    user_stats["correct_answers"] += correct
    user_stats["total_time"] += time_taken
    user_stats["quizzes_completed"] += 1
    
    # Update category stats
    if category not in user_stats["category_stats"]:
        user_stats["category_stats"][category] = {
            "questions": 0,
            "correct": 0,
            "time": 0,
            "attempts": 0
        }
    
    category_stat = user_stats["category_stats"][category]
    category_stat["questions"] += total
    category_stat["correct"] += correct
    category_stat["time"] += time_taken
    category_stat["attempts"] += 1
    
    # Record quiz in history
    if "quiz_history" not in user_stats:
        user_stats["quiz_history"] = []
    
    user_stats["quiz_history"].append({
        "timestamp": time.time(),
        "category": category,
        "correct": correct,
        "total": total,
        "time": time_taken,
        "accuracy": (correct / total * 100) if total > 0 else 0
    })
    
    save_statistics(statistics)


def get_overall_accuracy(username: str) -> float:
    """
    Get overall accuracy percentage for a user.
    
    Args:
        username: The username to calculate accuracy for
        
    Returns:
        Accuracy percentage, 0 if no questions answered
    """
    stats = get_user_stats(username)
    total = stats["total_questions"]
    
    if total == 0:
        return 0.0
    
    return (stats["correct_answers"] / total) * 100


def get_average_time_per_question(username: str) -> float:
    """
    Get average time per question for a user.
    
    Args:
        username: The username to calculate average for
        
    Returns:
        Average time in seconds
    """
    stats = get_user_stats(username)
    total = stats["total_questions"]
    
    if total == 0:
        return 0.0
    
    return stats["total_time"] / total


def get_category_accuracy(username: str, category: str) -> float:
    """
    Get accuracy for a specific category.
    
    Args:
        username: The username
        category: The category name
        
    Returns:
        Accuracy percentage for that category
    """
    stats = get_user_stats(username)
    categories = stats.get("category_stats", {})
    
    if category not in categories:
        return 0.0
    
    cat_stat = categories[category]
    total = cat_stat["questions"]
    
    if total == 0:
        return 0.0
    
    return (cat_stat["correct"] / total) * 100


def get_leaderboard_score(username: str) -> float:
    """
    Calculate a composite leaderboard score based on accuracy and speed.
    Higher is better.
    
    Args:
        username: The username to calculate score for
        
    Returns:
        Composite leaderboard score
    """
    stats = get_user_stats(username)
    
    if stats["total_questions"] == 0:
        return 0.0
    
    accuracy = (stats["correct_answers"] / stats["total_questions"]) * 100
    
    # Average time per question (lower is better, so we invert it)
    avg_time = get_average_time_per_question(username)
    time_score = TIME_SCORE_MAX / (1 + avg_time / TIME_NORMALIZATION)
    
    # Composite score: ACCURACY_WEIGHT% accuracy + SPEED_WEIGHT% speed
    score = (accuracy * ACCURACY_WEIGHT) + (time_score * SPEED_WEIGHT)
    
    return score


def get_all_users_for_leaderboard() -> List[tuple]:
    """
    Get all users with their scores for leaderboard display.
    
    Returns:
        List of (username, score, accuracy, average_time) tuples, sorted by score (highest first)
    """
    statistics = load_statistics()
    leaderboard = []
    
    for username in statistics.keys():
        if statistics[username]["total_questions"] > 0:
            score = get_leaderboard_score(username)
            accuracy = get_overall_accuracy(username)
            avg_time = get_average_time_per_question(username)
            leaderboard.append((username, score, accuracy, avg_time))
    
    # Sort by score (highest first)
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    return leaderboard

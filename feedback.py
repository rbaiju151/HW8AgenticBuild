"""
User feedback module.
Tracks user feedback on questions to help determine which questions to serve in the future.
Uses pickle for non-human readable storage.
"""

import time
from pathlib import Path
from typing import Optional, Dict, List

from data_storage import load_pickle_file, save_pickle_file


def get_feedback_file_path() -> Path:
    """Get the path to the feedback file."""
    return Path(__file__).parent / "feedback_data.pkl"


def load_feedback() -> dict:
    """
    Load feedback from the pickle file.
    
    Returns:
        Nested dictionary: {question_id: {username: feedback_data}}
        Returns empty dict if file doesn't exist.
    """
    return load_pickle_file(get_feedback_file_path())


def save_feedback(feedback: dict) -> None:
    """
    Save feedback to the pickle file.
    
    Args:
        feedback: Nested dictionary of feedback data
        
    Raises:
        IOError: If file cannot be written
    """
    save_pickle_file(get_feedback_file_path(), feedback)


def record_feedback(question_id: int, username: str, liked: bool, 
                   difficulty: Optional[str] = None, notes: Optional[str] = None) -> None:
    """
    Record feedback for a question from a user.
    
    Args:
        question_id: The ID of the question
        username: The username providing feedback
        liked: Whether the user liked the question (True/False)
        difficulty: Optional difficulty rating ('easy', 'medium', 'hard')
        notes: Optional feedback notes from the user
    """
    feedback = load_feedback()
    username_lower = username.lower()
    question_id_str = str(question_id)
    
    if question_id_str not in feedback:
        feedback[question_id_str] = {}
    
    feedback[question_id_str][username_lower] = {
        "liked": liked,
        "difficulty": difficulty,
        "notes": notes,
        "timestamp": time.time()
    }
    
    save_feedback(feedback)


def get_question_feedback(question_id: int) -> dict:
    """
    Get all feedback for a specific question.
    
    Args:
        question_id: The ID of the question
        
    Returns:
        Dictionary mapping usernames to their feedback
    """
    feedback = load_feedback()
    question_id_str = str(question_id)
    
    return feedback.get(question_id_str, {})


def get_user_feedback(username: str) -> dict:
    """
    Get all feedback provided by a specific user.
    
    Args:
        username: The username
        
    Returns:
        Dictionary mapping question_ids to feedback
    """
    feedback = load_feedback()
    username_lower = username.lower()
    user_feedback = {}
    
    for question_id, user_feedbacks in feedback.items():
        if username_lower in user_feedbacks:
            user_feedback[question_id] = user_feedbacks[username_lower]
    
    return user_feedback


def get_user_feedback_for_question(question_id: int, username: str) -> Optional[dict]:
    """
    Get feedback from a specific user for a specific question.
    
    Args:
        question_id: The ID of the question
        username: The username
        
    Returns:
        Feedback dict if exists, None otherwise
    """
    feedback = load_feedback()
    question_id_str = str(question_id)
    username_lower = username.lower()
    
    if question_id_str not in feedback:
        return None
    
    return feedback[question_id_str].get(username_lower)


def get_question_rating(question_id: int) -> dict:
    """
    Get aggregated rating information for a question.
    
    Args:
        question_id: The ID of the question
        
    Returns:
        Dictionary with 'likes', 'dislikes', 'liked_by' list, and 'disliked_by' list
    """
    question_feedback = get_question_feedback(question_id)
    
    result = {
        "likes": 0,
        "dislikes": 0,
        "liked_by": [],
        "disliked_by": [],
        "average_difficulty": None
    }
    
    difficulties = []
    
    for username, fb_data in question_feedback.items():
        if fb_data.get("liked"):
            result["likes"] += 1
            result["liked_by"].append(username)
        else:
            result["dislikes"] += 1
            result["disliked_by"].append(username)
        
        if fb_data.get("difficulty"):
            difficulties.append(fb_data["difficulty"])
    
    # Calculate average difficulty
    if difficulties:
        difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
        avg = sum(difficulty_map.get(d, 2) for d in difficulties) / len(difficulties)
        if avg <= 1.5:
            result["average_difficulty"] = "easy"
        elif avg <= 2.5:
            result["average_difficulty"] = "medium"
        else:
            result["average_difficulty"] = "hard"
    
    return result


def get_questions_by_user_preference(username: str, category: Optional[str] = None) -> dict:
    """
    Get a ranking of questions by user preference (which questions they liked).
    
    Args:
        username: The username
        category: Optional category to filter by
        
    Returns:
        Dictionary with 'liked_questions' and 'disliked_questions' lists
    """
    user_feedback = get_user_feedback(username)
    
    result = {
        "liked_questions": [],
        "disliked_questions": []
    }
    
    for question_id, fb_data in user_feedback.items():
        question_id_int = int(question_id)
        
        if fb_data.get("liked"):
            result["liked_questions"].append(question_id_int)
        else:
            result["disliked_questions"].append(question_id_int)
    
    return result


def get_well_received_questions(min_likes: int = 2) -> List[int]:
    """
    Get questions that are well-received by users (have more likes than dislikes).
    
    Args:
        min_likes: Minimum number of likes to include a question
        
    Returns:
        List of question IDs that are well-received
    """
    feedback = load_feedback()
    well_received = []
    
    for question_id_str, user_feedbacks in feedback.items():
        rating = get_question_rating(int(question_id_str))
        
        if rating["likes"] >= min_likes and rating["likes"] > rating["dislikes"]:
            well_received.append(int(question_id_str))
    
    return well_received

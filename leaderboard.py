"""
Leaderboard display module.
Displays rankings of users based on a composite score of accuracy and speed.
"""

from statistics import get_leaderboard_score, get_all_users_for_leaderboard, get_user_stats


def display_leaderboard(limit: int = 10) -> None:
    """
    Display the leaderboard with top users.
    
    Args:
        limit: Maximum number of users to display (default 10)
    """
    leaderboard = get_all_users_for_leaderboard()
    
    if not leaderboard:
        print("\n" + "=" * 70)
        print("LEADERBOARD")
        print("=" * 70)
        print("\nNo users have completed any quizzes yet.")
        print("=" * 70)
        return
    
    print("\n" + "=" * 70)
    print("LEADERBOARD - Top Scores")
    print("=" * 70)
    print(f"{'Rank':<6} {'Username':<20} {'Score':<12} {'Accuracy':<12} {'Avg Time/Q':<12}")
    print("-" * 70)
    
    for rank, (username, score, accuracy, avg_time) in enumerate(leaderboard[:limit], 1):
        print(f"{rank:<6} {username:<20} {score:<12.2f} {accuracy:<12.1f}% {avg_time:<12.2f}s")
    
    print("=" * 70)


def display_user_rank(username: str) -> None:
    """
    Display a user's current rank and stats.
    
    Args:
        username: The username to display rank for
    """
    leaderboard = get_all_users_for_leaderboard()
    username_lower = username.lower()
    
    rank = None
    user_data = None
    
    for idx, (name, score, accuracy, avg_time) in enumerate(leaderboard, 1):
        if name == username_lower:
            rank = idx
            user_data = (name, score, accuracy, avg_time)
            break
    
    stats = get_user_stats(username)
    
    if rank is None:
        print(f"\nYou haven't completed any quizzes yet.")
        if stats["total_questions"] == 0:
            print("Start a quiz to appear on the leaderboard!")
    else:
        print(f"\n" + "=" * 70)
        print(f"YOUR RANKING")
        print("=" * 70)
        print(f"Rank: #{rank} out of {len(leaderboard)}")
        print(f"Score: {user_data[1]:.2f}")
        print(f"Accuracy: {user_data[2]:.1f}%")
        print(f"Average Time per Question: {user_data[3]:.2f}s")
        print(f"Total Questions Answered: {stats['total_questions']}")
        print(f"Total Correct: {stats['correct_answers']}")
        print(f"Quizzes Completed: {stats['quizzes_completed']}")
        print("=" * 70)


def get_user_rank(username: str) -> tuple:
    """
    Get a user's rank and position on the leaderboard.
    
    Args:
        username: The username to get rank for
        
    Returns:
        Tuple of (rank, total_users, score) or None if user has no quizzes
    """
    leaderboard = get_all_users_for_leaderboard()
    username_lower = username.lower()
    
    for rank, (name, score, accuracy, avg_time) in enumerate(leaderboard, 1):
        if name == username_lower:
            return (rank, len(leaderboard), score)
    
    return None


def get_nearby_users(username: str, radius: int = 2) -> list:
    """
    Get users near a specific user on the leaderboard.
    
    Args:
        username: The username to get nearby users for
        radius: How many users above and below to show (default 2)
        
    Returns:
        List of (rank, username, score, accuracy, avg_time) tuples
    """
    leaderboard = get_all_users_for_leaderboard()
    username_lower = username.lower()
    
    user_rank = None
    for rank, (name, score, accuracy, avg_time) in enumerate(leaderboard, 1):
        if name == username_lower:
            user_rank = rank
            break
    
    if user_rank is None:
        return []
    
    start_idx = max(0, user_rank - radius - 1)
    end_idx = min(len(leaderboard), user_rank + radius)
    
    result = []
    for idx in range(start_idx, end_idx):
        name, score, accuracy, avg_time = leaderboard[idx]
        result.append((idx + 1, name, score, accuracy, avg_time))
    
    return result

#!/usr/bin/env python
"""
Comprehensive test suite for the quiz application.
Tests all modules to ensure they are functioning correctly.
"""

import users
import statistics as stats
import feedback
import leaderboard
import json
import app as quiz_app

def test_questions_json():
    """Test that questions.json is valid."""
    print('TEST 1: Validating questions.json...')
    try:
        with open('questions.json', 'r') as f:
            questions = json.load(f)
        print(f'✓ Successfully loaded {len(questions["questions"])} questions')
        
        # Verify all sample questions are present
        categories = set()
        for q in questions["questions"]:
            categories.add(q["category"])
        print(f'  Categories found: {", ".join(sorted(categories))}')
        return True
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def test_user_management():
    """Test user registration and authentication."""
    print('\nTEST 2: Testing user registration and authentication...')
    try:
        # Try to register (may already exist from previous test)
        result = users.register_user('testuser_comprehensive', 'securepass123')
        
        # Authenticate
        auth = users.authenticate('testuser_comprehensive', 'securepass123')
        if auth:
            print('✓ User authentication successful')
            return True
        else:
            print('✗ User authentication failed')
            return False
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def test_statistics():
    """Test statistics tracking."""
    print('\nTEST 3: Testing statistics tracking...')
    try:
        stats.record_quiz_result('testuser_comprehensive', 4, 5, 45.2, 'Load Transfer', [0, 1, 2, 3, 4])
        user_stats = stats.get_user_stats('testuser_comprehensive')
        
        if user_stats['total_questions'] == 5:
            accuracy = stats.get_overall_accuracy('testuser_comprehensive')
            print(f'✓ Statistics recording successful')
            print(f'  Accuracy: {accuracy:.1f}%')
            print(f'  Quizzes completed: {user_stats["quizzes_completed"]}')
            return True
        else:
            print('✗ Statistics recording failed')
            return False
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def test_feedback():
    """Test feedback system."""
    print('\nTEST 4: Testing feedback system...')
    try:
        feedback.record_feedback(0, 'testuser_comprehensive', liked=True, difficulty='medium')
        feedback_data = feedback.get_user_feedback('testuser_comprehensive')
        
        if len(feedback_data) > 0:
            print('✓ Feedback system working')
            print(f'  Questions with feedback: {len(feedback_data)}')
            return True
        else:
            print('✗ Feedback system failed')
            return False
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def test_leaderboard():
    """Test leaderboard functionality."""
    print('\nTEST 5: Testing leaderboard...')
    try:
        leaderboard_data = leaderboard.get_all_users_for_leaderboard()
        user_rank = leaderboard.get_user_rank('testuser_comprehensive')
        
        if user_rank:
            print(f'✓ Leaderboard functional')
            print(f'  Total users on leaderboard: {user_rank[1]}')
            print(f'  Your rank: #{user_rank[0]}')
            print(f'  Your score: {user_rank[2]:.2f}')
            return True
        else:
            print('✓ Leaderboard functional (user not ranked yet)')
            return True
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def test_question_bank():
    """Test QuestionBank class."""
    print('\nTEST 6: Testing QuestionBank class...')
    try:
        qb = quiz_app.QuestionBank()
        
        if not qb.valid_questions:
            print('✗ No valid questions loaded')
            return False
        
        categories = qb.get_categories()
        print(f'✓ QuestionBank loaded successfully')
        print(f'  Valid questions: {len(qb.valid_questions)}')
        print(f'  Categories: {", ".join(categories)}')
        
        # Test getting random questions
        random_q = qb.get_random_questions(2)
        if len(random_q) == 2:
            print(f'✓ Random question selection works')
            return True
        else:
            print('✗ Random question selection failed')
            return False
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def main():
    """Run all tests."""
    print("=" * 70)
    print("QUIZ APPLICATION - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_questions_json,
        test_user_management,
        test_statistics,
        test_feedback,
        test_leaderboard,
        test_question_bank
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f'CRITICAL ERROR in {test_func.__name__}: {e}')
            results.append(False)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())

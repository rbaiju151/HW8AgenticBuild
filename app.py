"""
Quiz Application Main Module
A simple command-line quiz application with user authentication, score tracking, and leaderboard.
"""

import json
import random
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import users
import statistics as stats
import feedback
import leaderboard


class QuestionBank:
    """Manages loading and validating questions from JSON file."""
    
    def __init__(self, filepath: str = "questions.json"):
        """
        Initialize the question bank.
        
        Args:
            filepath: Path to the questions JSON file
        """
        self.filepath = Path(filepath)
        self.questions = []
        self.valid_questions = []
        self.invalid_questions = []
        self.warnings = []
        self.load_questions()
    
    def load_questions(self) -> bool:
        """
        Load questions from JSON file with error handling.
        
        Returns:
            True if any valid questions were loaded, False otherwise
        """
        if not self.filepath.exists():
            self.warnings.append(f"CRITICAL ERROR: Questions file not found at {self.filepath}")
            return False
        
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.warnings.append(f"CRITICAL ERROR: Questions file is not valid JSON: {e}")
            return False
        except Exception as e:
            self.warnings.append(f"CRITICAL ERROR: Cannot read questions file: {e}")
            return False
        
        if "questions" not in data or not isinstance(data["questions"], list):
            self.warnings.append("CRITICAL ERROR: Questions file must contain a 'questions' array")
            return False
        
        # Validate each question
        for idx, question in enumerate(data["questions"]):
            if self.validate_question(question):
                self.valid_questions.append(question)
                self.questions.append(question)
            else:
                self.invalid_questions.append((idx, question))
        
        if not self.valid_questions:
            self.warnings.append("CRITICAL ERROR: No valid questions found in file")
            return False
        
        return True
    
    def validate_question(self, question: dict) -> bool:
        """
        Validate a single question structure.
        
        Args:
            question: The question dict to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["question", "type", "answer", "category"]
        
        # Check required fields
        if not isinstance(question, dict):
            self.warnings.append(f"Question is not a dict: {question}")
            return False
        
        for field in required_fields:
            if field not in question:
                self.warnings.append(f"Question missing '{field}' field")
                return False
        
        question_type = question.get("type")
        
        if question_type == "multiple_choice":
            if "options" not in question or not isinstance(question["options"], list):
                self.warnings.append(f"Multiple choice question missing 'options' array: {question['question']}")
                return False
            if not question.get("answer") in question["options"]:
                self.warnings.append(f"Multiple choice answer not in options: {question['question']}")
                return False
        
        elif question_type == "true_false":
            if question.get("answer") not in ["true", "false", True, False]:
                self.warnings.append(f"True/false question has invalid answer: {question['question']}")
                return False
        
        elif question_type == "short_answer":
            if not isinstance(question.get("answer"), str):
                self.warnings.append(f"Short answer question has non-string answer: {question['question']}")
                return False
        
        else:
            self.warnings.append(f"Unknown question type '{question_type}': {question['question']}")
            return False
        
        return True
    
    def display_warnings(self) -> None:
        """Display loading warnings to user."""
        if self.warnings:
            for warning in self.warnings:
                if "CRITICAL" in warning:
                    print(f"\n⚠️  {warning}")
                else:
                    print(f"⚠️  WARNING: {warning}")
    
    def get_categories(self) -> List[str]:
        """Get unique categories from questions."""
        categories = set()
        for question in self.questions:
            categories.add(question.get("category", "Other"))
        return sorted(list(categories))
    
    def get_questions_by_category(self, category: str) -> List[Dict]:
        """Get questions for a specific category."""
        return [q for q in self.questions if q.get("category") == category]
    
    def get_random_questions(self, count: int, category: Optional[str] = None) -> List[Tuple[int, Dict]]:
        """
        Get random questions, optionally filtered by category.
        
        Args:
            count: Number of questions to return
            category: Optional category to filter by
            
        Returns:
            List of (index, question) tuples
        """
        if category:
            available = self.get_questions_by_category(category)
        else:
            available = self.questions
        
        count = min(count, len(available))
        selected = random.sample(available, count)
        
        # Get indices
        result = []
        for question in selected:
            for idx, q in enumerate(self.questions):
                if q == question:
                    result.append((idx, question))
                    break
        
        return result


class Quiz:
    """Manages a single quiz session."""
    
    def __init__(self, username: str, question_bank: QuestionBank):
        """
        Initialize a quiz session.
        
        Args:
            username: The user taking the quiz
            question_bank: The QuestionBank instance
        """
        self.username = username
        self.question_bank = question_bank
        self.questions = []
        self.category = None
        self.start_time = None
        self.current_question = 0
        self.correct_answers = 0
        self.user_answers = {}
        self.user_feedback = {}
    
    def select_quiz_parameters(self) -> bool:
        """
        Prompt user to select quiz parameters.
        
        Returns:
            True if user confirmed selection, False if they want to cancel
        """
        categories = self.question_bank.get_categories()
        
        print("\n" + "=" * 70)
        print("QUIZ SETUP")
        print("=" * 70)
        
        # Select category
        print("\nAvailable Categories:")
        for idx, category in enumerate(categories, 1):
            count = len(self.question_bank.get_questions_by_category(category))
            print(f"  {idx}. {category} ({count} questions)")
        
        while True:
            try:
                choice = input(f"\nSelect category (1-{len(categories)}) or 'M' for mixed: ").strip()
                
                if choice.upper() == 'M':
                    self.category = "Mixed"
                    break
                
                cat_idx = int(choice) - 1
                if 0 <= cat_idx < len(categories):
                    self.category = categories[cat_idx]
                    break
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(categories)}")
            except ValueError:
                print("⚠️  Please enter a valid number or 'M' for mixed")
        
        # Select number of questions
        max_questions = len(self.question_bank.questions)
        if self.category != "Mixed":
            max_questions = len(self.question_bank.get_questions_by_category(self.category))
        
        while True:
            try:
                num_questions = int(input(f"\nHow many questions? (1-{max_questions}): ").strip())
                if 1 <= num_questions <= max_questions:
                    break
                else:
                    print(f"⚠️  Please enter a number between 1 and {max_questions}")
            except ValueError:
                print("⚠️  Please enter a valid number")
        
        # Get questions
        if self.category == "Mixed":
            self.questions = self.question_bank.get_random_questions(num_questions)
        else:
            self.questions = self.question_bank.get_random_questions(num_questions, self.category)
        
        # Confirm
        print(f"\n✓ Ready to start quiz: {num_questions} questions from {self.category}")
        input("Press Enter to begin...")
        
        return True
    
    def run_quiz(self) -> bool:
        """
        Run the quiz.
        
        Returns:
            True if quiz completed, False if user quit
        """
        self.start_time = time.time()
        print("\n" + "=" * 70)
        print(f"QUIZ - {self.category}")
        print("=" * 70)
        
        for self.current_question, (question_idx, question) in enumerate(self.questions, 1):
            try:
                if not self.ask_question(question_idx, question):
                    return False
                
                # Optional feedback
                self.ask_feedback(question_idx, question)
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Quiz interrupted by user")
                if input("Continue quiz? (y/n): ").strip().lower() != 'y':
                    return False
        
        return True
    
    def ask_question(self, question_idx: int, question: Dict) -> bool:
        """
        Present a question to the user and check their answer.
        
        Args:
            question_idx: Index of the question in the question bank
            question: The question dict
            
        Returns:
            True if answered, False if user wants to quit
        """
        question_text = question["question"]
        question_type = question["type"]
        
        print(f"\nQuestion {self.current_question}/{len(self.questions)}:")
        print(f"{question_text}")
        
        if question_type == "multiple_choice":
            return self.ask_multiple_choice(question_idx, question)
        elif question_type == "true_false":
            return self.ask_true_false(question_idx, question)
        elif question_type == "short_answer":
            return self.ask_short_answer(question_idx, question)
        
        return True
    
    def ask_multiple_choice(self, question_idx: int, question: Dict) -> bool:
        """Ask a multiple choice question."""
        options = question["options"]
        correct_answer = question["answer"]
        
        for idx, option in enumerate(options, 1):
            print(f"  {idx}. {option}")
        
        while True:
            try:
                choice = input("\nYour answer (1-{}) or Q to quit: ".format(len(options))).strip()
                
                if choice.upper() == 'Q':
                    if input("Are you sure you want to quit? (y/n): ").strip().lower() == 'y':
                        return False
                    continue
                
                answer_idx = int(choice) - 1
                if 0 <= answer_idx < len(options):
                    user_answer = options[answer_idx]
                    self.user_answers[question_idx] = user_answer
                    
                    if user_answer == correct_answer:
                        self.correct_answers += 1
                        print("✓ Correct!")
                    else:
                        print(f"✗ Incorrect. The correct answer is: {correct_answer}")
                    
                    return True
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(options)}")
            except ValueError:
                print(f"⚠️  Please enter a valid number from 1 to {len(options)}")
    
    def ask_true_false(self, question_idx: int, question: Dict) -> bool:
        """Ask a true/false question."""
        correct_answer = str(question["answer"]).lower()
        
        print("  1. True")
        print("  2. False")
        
        while True:
            try:
                choice = input("\nYour answer (1-2) or Q to quit: ").strip().upper()
                
                if choice == 'Q':
                    if input("Are you sure you want to quit? (y/n): ").strip().lower() == 'y':
                        return False
                    continue
                
                if choice in ['1', '2']:
                    user_answer = 'true' if choice == '1' else 'false'
                    self.user_answers[question_idx] = user_answer
                    
                    if user_answer == correct_answer:
                        self.correct_answers += 1
                        print("✓ Correct!")
                    else:
                        print(f"✗ Incorrect. The correct answer is: {correct_answer}")
                    
                    return True
                else:
                    print("⚠️  Please enter 1 for True or 2 for False")
            except ValueError:
                print("⚠️  Please enter a valid choice")
    
    def ask_short_answer(self, question_idx: int, question: Dict) -> bool:
        """Ask a short answer question."""
        correct_answer = question["answer"].lower()
        
        while True:
            try:
                user_answer = input("\nYour answer (or Q to quit): ").strip()
                
                if user_answer.upper() == 'Q':
                    if input("Are you sure you want to quit? (y/n): ").strip().lower() == 'y':
                        return False
                    continue
                
                self.user_answers[question_idx] = user_answer
                
                if user_answer.lower() == correct_answer:
                    self.correct_answers += 1
                    print("✓ Correct!")
                else:
                    print(f"✗ Incorrect. The correct answer is: {correct_answer}")
                
                return True
            except Exception as e:
                print(f"⚠️  Error processing answer: {e}")
    
    def ask_feedback(self, question_idx: int, question: Dict) -> None:
        """
        Ask user for feedback on a question.
        
        Feedback is optional - non-critical errors are logged but don't affect quiz flow.
        """
        try:
            response = input("\nWas this question helpful? (y/n/skip): ").strip().lower()
            
            if response in ['y', 'yes']:
                feedback.record_feedback(question_idx, self.username, liked=True)
                self.user_feedback[question_idx] = True
                print("Thanks for the feedback!")
            elif response in ['n', 'no']:
                feedback.record_feedback(question_idx, self.username, liked=False)
                self.user_feedback[question_idx] = False
                print("Thanks for the feedback!")
            # Else: user skipped feedback (valid response)
        except (IOError, OSError) as e:
            print(f"⚠️  Warning: Could not save feedback for question {question_idx}: {e}")
            print("   (Quiz progress was saved, but feedback was not)")
        except Exception as e:
            print(f"⚠️  Warning: Error processing feedback for question {question_idx}: {e}")
            print("   (This is non-critical and won't affect your quiz results)")
    
    def get_results(self) -> Dict:
        """Get quiz results."""
        end_time = time.time()
        time_taken = end_time - self.start_time
        total = len(self.questions)
        
        return {
            "correct": self.correct_answers,
            "total": total,
            "accuracy": (self.correct_answers / total * 100) if total > 0 else 0,
            "time_taken": time_taken,
            "category": self.category
        }
    
    def save_results(self) -> None:
        """Save quiz results to statistics."""
        try:
            results = self.get_results()
            question_indices = [idx for idx, _ in self.questions]
            
            stats.record_quiz_result(
                self.username,
                results["correct"],
                results["total"],
                results["time_taken"],
                results["category"],
                question_indices
            )
        except IOError as e:
            print(f"⚠️  Warning: Could not permanently save results: {e}")
        except Exception as e:
            print(f"⚠️  Warning: Error saving results: {e}")
    
    def display_results(self) -> None:
        """Display quiz results."""
        results = self.get_results()
        
        print("\n" + "=" * 70)
        print("QUIZ RESULTS")
        print("=" * 70)
        print(f"Category: {results['category']}")
        print(f"Score: {results['correct']}/{results['total']}")
        print(f"Accuracy: {results['accuracy']:.1f}%")
        print(f"Time Taken: {results['time_taken']:.1f} seconds")
        print(f"Average Time per Question: {results['time_taken']/results['total']:.2f}s")
        print("=" * 70)


def clear_screen():
    """Clear the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def load_questions_with_handling() -> Optional[QuestionBank]:
    """
    Load questions with error handling and user override option.
    
    Returns:
        QuestionBank instance if successful, None if user wants to exit
    """
    question_bank = QuestionBank("questions.json")
    
    question_bank.display_warnings()
    
    if not question_bank.valid_questions:
        print("\n" + "=" * 70)
        print("CRITICAL ERROR: Cannot load questions")
        print("=" * 70)
        print("\nTo fix this error:")
        print("1. Check that 'questions.json' exists in the application directory")
        print("2. Verify the JSON file is properly formatted")
        print("3. Ensure all questions have required fields: question, type, answer, category")
        print("\nPlease fix the questions.json file and restart the app.")
        input("\nPress Enter to exit...")
        return None
    elif question_bank.invalid_questions:
        print(f"\n{len(question_bank.invalid_questions)} questions had formatting issues.")
        response = input("Continue with valid questions only? (y/n): ").strip().lower()
        if response != 'y':
            print("Exiting application.")
            return None
    
    return question_bank


def handle_login() -> Optional[str]:
    """
    Handle user login or registration with rate limiting.
    
    Returns:
        Username if successful, None if user wants to exit
    """
    failed_attempts = {}  # Track failed login attempts per username
    MAX_ATTEMPTS = 5
    LOCKOUT_TIME = 300  # 5 minutes in seconds
    
    while True:
        print("\n" + "=" * 70)
        print("QUIZ APPLICATION - LOGIN")
        print("=" * 70)
        print("1. Login")
        print("2. Create New Account")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            username = input("\nUsername: ").strip()
            password = input("Password: ").strip()
            
            if not username or not password:
                print("⚠️  Username and password cannot be empty")
                continue
            
            # Check login attempt rate limiting
            username_lower = username.lower()
            if username_lower in failed_attempts:
                attempts, last_attempt_time = failed_attempts[username_lower]
                time_since_last = time.time() - last_attempt_time
                if attempts >= MAX_ATTEMPTS and time_since_last < LOCKOUT_TIME:
                    wait_time = int(LOCKOUT_TIME - time_since_last)
                    print(f"⚠️  Too many failed login attempts. Please try again in {wait_time} seconds.")
                    continue
                elif time_since_last >= LOCKOUT_TIME:
                    # Reset attempts after lockout period
                    del failed_attempts[username_lower]
            
            if users.authenticate(username, password):
                # Clear failed attempts on successful login
                if username_lower in failed_attempts:
                    del failed_attempts[username_lower]
                print(f"✓ Welcome back, {username}!")
                time.sleep(1)
                return username
            else:
                # Track failed attempt
                if username_lower not in failed_attempts:
                    failed_attempts[username_lower] = (1, time.time())
                else:
                    attempts, _ = failed_attempts[username_lower]
                    failed_attempts[username_lower] = (attempts + 1, time.time())
                attempts_left = MAX_ATTEMPTS - failed_attempts[username_lower][0]
                if attempts_left > 0:
                    print(f"⚠️  Invalid username or password ({attempts_left} attempts remaining)")
                else:
                    print(f"⚠️  Too many failed attempts. Account locked for {LOCKOUT_TIME // 60} minutes.")
        
        elif choice == '2':
            username = input("\nNew username: ").strip()
            
            if not username:
                print("⚠️  Username cannot be empty")
                continue
            
            if users.user_exists(username):
                print("⚠️  Username already exists")
                continue
            
            password = input("Password: ").strip()
            confirm = input("Confirm password: ").strip()
            
            if not password:
                print("⚠️  Password cannot be empty")
                continue
            
            if password != confirm:
                print("⚠️  Passwords do not match")
                continue
            
            # Register user and handle new return type
            try:
                success, message = users.register_user(username, password)
                if success:
                    print(f"✓ {message}")
                    time.sleep(1)
                    return username
                else:
                    print(f"⚠️  {message}")
            except IOError as e:
                print(f"⚠️  Database error: {e}")
            except Exception as e:
                print(f"⚠️  Unexpected error: {e}")
        
        elif choice == '3':
            return None
        
        else:
            print("⚠️  Please enter a valid option")


def main_menu(username: str, question_bank: QuestionBank) -> bool:
    """
    Display main menu and handle user choices.
    
    Args:
        username: The logged-in username
        question_bank: The QuestionBank instance
        
    Returns:
        True to continue, False to logout
    """
    while True:
        print("\n" + "=" * 70)
        print(f"MAIN MENU - Welcome, {username}!")
        print("=" * 70)
        print("1. Start Quiz")
        print("2. View Leaderboard")
        print("3. View Your Stats")
        print("4. Logout")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            quiz = Quiz(username, question_bank)
            if quiz.select_quiz_parameters():
                if quiz.run_quiz():
                    quiz.save_results()
                    quiz.display_results()
        
        elif choice == '2':
            leaderboard.display_leaderboard()
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            leaderboard.display_user_rank(username)
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            response = input("\nAre you sure you want to logout? (y/n): ").strip().lower()
            if response == 'y':
                return False
        
        else:
            print("⚠️  Please enter a valid option")


def main():
    """Main application entry point."""
    try:
        # Load questions
        question_bank = load_questions_with_handling()
        if question_bank is None:
            return
        
        # Main application loop
        while True:
            # Login
            username = handle_login()
            if username is None:
                print("\nThank you for using the Quiz Application!")
                break
            
            # Main menu loop
            if not main_menu(username, question_bank):
                continue
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user")
        print("Exiting...")
    except Exception as e:
        print(f"\n⚠️  Unexpected error: {e}")
        print("The application will now exit.")
    finally:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()

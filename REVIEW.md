# Code Review Against SPEC.md

## Compliance with Acceptance Criteria

1. **[PASS] App successfully launches to login screen**
   - [app.py](app.py#L612) main() function loads questions and calls handle_login()
   - [app.py](app.py#L515) handle_login() displays proper login/registration menu

2. **[PASS] User can create a login and password, which opens the main screen**
   - [app.py](app.py#L535) Registration flow accepts username and password with confirmation
   - [users.py](users.py#L70) register_user() creates new accounts with SHA-256 hashed passwords
   - Registration successfully redirects to main menu

3. **[PASS] User can input start conditions for their first quiz**
   - [app.py](app.py#L226) select_quiz_parameters() prompts for category selection
   - [app.py](app.py#L248) Prompts for number of questions with validation
   - Supports both single category and mixed quiz modes

4. **[PASS] App successfully serves all five questions to the user**
   - [questions.json](questions.json) contains exactly 5 questions in correct format
   - All questions have required fields: question, type, answer, category
   - [app.py](app.py#L289) run_quiz() iterates through selected questions

5. **[PASS] User is able to provide feedback for each question optionally**
   - [app.py](app.py#L421) ask_feedback() prompts for feedback on every question
   - [feedback.py](feedback.py#L48) record_feedback() stores user feedback in pickle file
   - Feedback is optional (users can skip)

6. **[PASS] Leaderboard displays scores correctly**
   - [leaderboard.py](leaderboard.py#L8) display_leaderboard() shows top users ranked by score
   - [statistics.py](statistics.py#L212) get_leaderboard_score() calculates composite score (70% accuracy + 30% speed)
   - [leaderboard.py](leaderboard.py#L30) display_user_rank() shows individual user ranking

7. **[PASS] All files are properly stored and secure**
   - User passwords hashed with SHA-256 ([users.py](users.py#L8))
   - Statistics stored in non-human-readable pickle format ([statistics.py](statistics.py#L32))
   - Feedback stored in non-human-readable pickle format ([feedback.py](feedback.py#L32))
   - All data files use `.pkl` extension stored in project directory

---

## Error Handling Compliance

1. **[PASS] Missing/incorrectly formatted questions.json**
   - [app.py](app.py#L485) load_questions_with_handling() displays CRITICAL ERROR message
   - [app.py](app.py#L119) QuestionBank.load_questions() validates JSON structure
   - [app.py](app.py#L151) validate_question() checks all required fields
   - [app.py](app.py#L491) User can override and continue with valid questions only

2. **[PASS] User enters incorrect input**
   - [app.py](app.py#L240) Category selection validates numeric input (1-N)
   - [app.py](app.py#L252) Question count validates range (1-MAX)
   - [app.py](app.py#L366) Multiple choice validates option selection (1-N)
   - [app.py](app.py#L395) True/false validates input (1 or 2)
   - Input prompts display acceptable formats

3. **[PASS] Command line errors - keyboard interrupts**
   - [app.py](app.py#L310) KeyboardInterrupt during quiz prompts to confirm quit
   - [app.py](app.py#L629) main() catches KeyboardInterrupt and displays clean exit message

---

## Feature Compliance

1. **[PASS] Local login system with non-discoverable passwords**
   - Passwords hashed with SHA-256 ([users.py](users.py#L13)) - not plaintext
   - User credentials stored in binary pickle file ([users.py](users.py#L32)) - not human-readable
   - Authentication compares hashes, not passwords ([users.py](users.py#L52))

2. **[PASS] Score history file (non-human-readable, secure)**
   - Uses pickle binary format ([statistics.py](statistics.py#L32))
   - Usernames visible but not passwords ([statistics.py](statistics.py#L45))
   - Stores detailed history: accuracy, time, category, timestamp
   - [statistics.py](statistics.py#L84) record_quiz_result() captures all metrics

3. **[PASS] User feedback on questions**
   - Optional per-question feedback ([app.py](app.py#L421))
   - Stored in pickle format with timestamp
   - Can determine question quality over time

4. **[PASS] Questions in human-readable JSON**
   - [questions.json](questions.json) is valid JSON format
   - Easily modifiable for different subjects
   - Includes: question, type, options, answer, category

5. **[PASS] Leaderboard based on accuracy and speed**
   - Composite scoring algorithm ([statistics.py](statistics.py#L212)): 70% accuracy + 30% speed
   - [leaderboard.py](leaderboard.py#L8) Sorted by highest score first
   - Shows username, score, accuracy %, average time/question

---

## Bugs and Logic Errors

1. **[FAIL] Bare except clause suppresses all exceptions**
   - **Location:** [app.py](app.py#L428)
   - **Issue:** `except: pass` in ask_feedback() masks all errors including system exits
   - **Impact:** Feedback submission errors silently fail with no user notification
   - **Fix:** Replace with specific exception handling, e.g., `except (IOError, ValueError) as e:`

2. **[WARN] Username display loses original casing**
   - **Location:** [users.py](users.py#L112)
   - **Issue:** Function docstring claims to "preserve original casing" but stores all usernames in lowercase
   - **Impact:** Cannot restore original casing after login (user "John" becomes "john" permanently)
   - **Note:** This is acceptable for case-insensitive login design, but docstring is misleading

3. **[WARN] No minimum length validation for usernames/passwords**
   - **Location:** [app.py](app.py#L535) and [users.py](users.py#L70)
   - **Issue:** Users can create 1-character username or password
   - **Impact:** Weak account security
   - **Fix:** Add validation like `if len(password) < 8: raise ValueError("Password too short")`

4. **[WARN] Average time per question calculation assumes non-zero total_questions**
   - **Location:** [statistics.py](statistics.py#L172)
   - **Issue:** Returns 0.0 if no questions, but doesn't validate division elsewhere
   - **Note:** Safe due to check in get_leaderboard_score() but defensive

---

## Missing Error Handling

1. **[WARN] No error handling for quiz data write failures**
   - **Location:** [app.py](app.py#L456)
   - **Issue:** save_results() doesn't verify write succeeded
   - **Impact:** User could lose quiz results if pickle file write fails
   - **Fix:** Add try-except around pickle.dump() operations

2. **[WARN] No validation of question format before serving**
   - **Location:** [app.py](app.py#L137)
   - **Issue:** Malformed questions might be served despite validation (if validator is outdated)
   - **Note:** Low risk due to comprehensive validation checks

3. **[WARN] File permission errors not handled**
   - **Location:** [users.py](users.py#L38), [statistics.py](statistics.py#L32), [feedback.py](feedback.py#L32)
   - **Issue:** pickle.dump() could fail due to permissions but isn't caught
   - **Impact:** Crash if filesystem is read-only
   - **Fix:** Wrap file operations in try-except

---

## Code Quality Issues

1. **[WARN] Repeated code for file loading**
   - **Location:** [users.py](users.py#L25), [statistics.py](statistics.py#L18), [feedback.py](feedback.py#L18)
   - **Issue:** Three identical pickle loading patterns with duplicate error handling
   - **Fix:** Extract to common utility function

2. **[WARN] Inconsistent naming conventions**
   - **Location:** Multiple files
   - **Issue:** Mix of `get_` prefix (get_user_stats) and unprefixed functions (load_users)
   - **Note:** Generally consistent but could be more uniform

3. **[WARN] Magic numbers in leaderboard scoring**
   - **Location:** [statistics.py](statistics.py#L218)
   - **Issue:** Hardcoded 0.7 (accuracy weight) and 0.3 (speed weight) without explanation
   - **Fix:** Define as module constants: `ACCURACY_WEIGHT = 0.7`

4. **[WARN] Time normalization factor in scoring**
   - **Location:** [statistics.py](statistics.py#L217)
   - **Issue:** Magic number "10" in `100 / (1 + avg_time / 10)` not explained
   - **Impact:** Unclear if intentional or arbitrary
   - **Fix:** Define as constant or add comment explaining rationale

5. **[WARN] Unused imports**
   - **Location:** [leaderboard.py](leaderboard.py) 
   - **Issue:** Module imports `get_user_stats` but doesn't use it (not a critical issue)

---

## Security Concerns

1. **[WARN] Pickle deserialization is unsafe**
   - **Location:** [users.py](users.py#L25), [statistics.py](statistics.py#L18), [feedback.py](feedback.py#L18)
   - **Issue:** pickle.load() can execute arbitrary code if file is tampered with
   - **Impact:** Low risk if file permissions restricted, high risk if shared
   - **Fix:** Use json or protobuf instead, or restrict file permissions to 0600

2. **[PASS] Password hashing uses appropriate algorithm**
   - **Location:** [users.py](users.py#L8)
   - **Note:** SHA-256 is acceptable for quiz app (not user-facing auth)
   - **Suggestion:** Consider bcrypt or argon2 for higher security

3. **[PASS] Usernames stored lowercase (case-insensitive comparison)**
   - **Location:** [users.py](users.py#L47), [users.py](users.py#L71)
   - **Note:** Correct approach prevents username collision ("John" vs "john")

4. **[WARN] No rate limiting on login attempts**
   - **Location:** [app.py](app.py#L530)
   - **Issue:** Unlimited failed login attempts allow brute force
   - **Fix:** Track failed attempts and add delay or temporary lockout

5. **[PASS] Quiz data accessible only to logged-in user**
   - Users can only view their own stats/leaderboard
   - Leaderboard shows only aggregated scores, not detailed answers

---

## Questions.json Format Verification

1. **[PASS] All 5 questions present**
   - Load Transfer: 2 questions
   - Tires: 2 questions
   - Aerodynamics: 1 question

2. **[PASS] All questions have correct fields**
   - question, type, options (for multiple choice), answer, category

3. **[FAIL] SPEC.md shows incorrect format for question #3**
   - **SPEC shows:** `"answer": ["v", "v^2", "v^1/2", "v^3"]` with no "options" field
   - **Actual JSON:** Correctly has separate "options" array and "answer": "v^2"
   - **Note:** Implementation is correct; SPEC.md example is wrong

4. **[PASS] Question types consistent**
   - multiple_choice: 2 questions (questions 1 and 3)
   - true_false: 2 questions (questions 2 and 4)
   - short_answer: 1 question (question 5)

---

## Summary Statistics

- **Total Acceptance Criteria:** 7
- **Passed:** 7 [100%]
- **Failed:** 0
- **Warnings:** 10

### Critical Issues: 0
### Major Issues (FAIL): 1 (SPEC.md format error - not code issue)
### Minor Issues (WARN): 10

---

## Recommendations

### High Priority
1. Replace bare `except:` clause with specific exception types [app.py](app.py#L428)
2. Add file operation error handling for pickle saves [users.py](users.py#L38), etc.
3. Add minimum password length validation

### Medium Priority
1. Extract common pickle loading code to utility
2. Add rate limiting to login attempts
3. Use json or protobuf instead of pickle for safer deserialization
4. Add constants for magic numbers (0.7, 0.3, 10)

### Low Priority
1. Clarify username casing behavior in docstring
2. Make exception handling in feedback collection more informative
3. Consider storing display usernames separately if casing needs to be preserved


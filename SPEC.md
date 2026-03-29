**Behavior Description:** A simple command line Python app that quizzes users from a bank of questions stored in a formatted JSON file. The app should allow authenticated logins and track scores. When the user launches the app, the app should prompt them for a username and login. Once logged the app should greet the user and ask them which topics they would like to study (all categories specified in the JSON file). The user can also select  the number of questions. The app will then randomly select questions one by one from the question bank, present it to the user, check the answer, and update the user's scores and statistics in the results file. Once the round is over, the user can choose to start another round or log out. We will also add a leaderboard function to be specified in more detail later.

**Data Format:** The question bank should be in the following format and should include just these questions for now:
{
  "questions": [
    {
      "question": "If you have 20% anti-geometry, 20% of your load transfer will transfer through what suspension member?",
      "type": "multiple_choice",
      "options": ["Control Arms", "Pushrods", "Springs", "Dampers"],
      "answer": "Control Arms",
      "category": "Load Transfer"
    },
    {
      "question": "Does the coefficient of tire grip increase linearly with Fz?",
      "type": "true_false",
      "answer": "false",
      "category": "Tires"
    },
    {
      "question": "Aerodynamics loads scale with what power of velocity?",
      "type": "multiple_choice",
      "answer": ["v", "v^2", "v^1/2", "v^3"],
      "category": "Aerodynamics"
    },
    {
      "question": "For a given acceleration, can you change the amount of load transfer by changing the spring stiffness only?",
      "type": "true_false",
      "answer": "false",
      "category": "Load Transfer"
    },
    {
      "question": "Slip angle is the angle between your tire contact patch's heading and ___.",
      "type": "short_answer",
      "answer": "vehicle heading",
      "category": "Tires"
    }
  ]
}


**File Structure** The following files should be included. If you believe more files are required, you are free to add them as well.

- questions.json (file containing the above questions in the correct format)
- users.py (a non-human readble file which contains usernames and passwords for all users)
- statistics.py (a non-human readble file containing performance metrics for every user. We can start with simple accuracy metrics)
- feedback.py (a collection of user feedback for all questions that the program can use to pick which questions are better to serve to the user in the future)
- app.py (the main file that handles login, I/O requests, pulls questions, writes data to other files, and interacts with the user)
- leaderboard.py (optional file, might be able to handle these features in statistics.py, but essentially allows the app to display a leaderboard of top scores, where top scores are determined by both accuracy and the speed of answering)
- Any other files you deem neccessary for proper function

**Error Handling** Here are a few error cases you should be able to handle
- Missing/incorrectly formatted questions.json (If one or more questions are incorrectly formatted display a warning message but allow the user to override it and use any correclty formatted questions. If no questions are formatted correctly or the file is missing, display a critical error message and display instructions to fix it)

- User enters incorrect input (Mostly for short answer questions or login. Display a warning alongside acceptable input formats)

- Command line errors (If users accidentally press hotkeys/escape keys during the quiz, you should see this and execute a clean exit from the app instead of allowing Window's native error handling to take over)

**Required Features**
- A local login system that prompts users for a username and password (or allows them to enter a new username and password). The passwords should not be easily discoverable.
- A score history file that tracks performance and other useful statistics over time for each user. This file should not be human-readable and should be relatively secure. (This means someone could look at the file and perhaps find out usernames but not passwords or scores.)
- Users should somehow be able to provide feedback on whether they like a question or not, and this should inform what questions they get next.
- The questions should exist in their own human-readable .json file so that they can be easily modified. (This lets you use the project for studying other subjects if you wish; all you have to do is generate the question bank.)
- A leaderboard feature that calculates a score based on time to complete the quiz and accuracy and displays high scores of all users

**Acceptance Criteria** The following are features I will use to determine whether or not the app is passable
- App successfully launches to login screen
- User can create a login and password, which opens the main screen
- User can input start conditions for their first quiz
- App successfully serves all five questions to the user
- User is able to provide feedback for each question optionally
- Leaderboard displays scores correctly
- All files are properly stored and secure
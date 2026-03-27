**Behavior Description:** A simple command line Python app that quizzes users from a bank of questions stored in a formatted JSON file. The app should allow authenticated logins and track scores. When the user launches the app, the app should prompt them for a username and login. Once logged the app should greet the user and ask them which topics they would like to study (all categories specified in the JSON file). The user can also select  the number of questions. The app will then randomly select questions one by one from the question bank, present it to the user, check the answer, and update the user's scores and statistics in the results file. Once the round is over, the user can choose to start another round or log out.

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

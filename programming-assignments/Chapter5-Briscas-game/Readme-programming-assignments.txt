Programación Assignment:
Esta carpeta contiene la solución al problema de programación descrito a continuación. Se incluye el código fuente y el informe técnico correspondiente.

Enunciado de la tarea
I hope this assignment sparks as much excitement as when I taught this course in person. One of the highlights back then was our AI tournament, where your agents competed against each other—and against you! I strongly encourage you to organize a friendly tournament as part of your testing. It is one of the best ways to understand how your AI behaves under real conditions.

1. Assignment Overview
Your team must implement ONE of the following games:

Briscas
Domino (team-based, 4 players)
You may use ONE of the following approaches:

Stochastic games
Partially observable games
Monte Carlo simulation
Averaging over clairvoyance
Deep Neural Networks (DNNs) (new option)
Techniques 1–4 were covered in class. DNNs are allowed but require independent study.

2. Use of Libraries (Don't reinvent the wheel)
You are NOT expected to implement everything from scratch.

You are encouraged to use any of the following repositories:

AIMA Python
OpenSpiel
PettingZoo
PyTorch / TensorFlow
If you use a library, you MUST:
State which one you used
Explain how you used it
Justify why it is appropriate
Demonstrate understanding
Re-implementing standard algorithms without justification is discouraged.

3. Project Requirements
Your submission must include:

Justification of your chosen approach, including comparison with alternatives
Clear explanation of:
design decisions
algorithmic logic
evaluation results
If using DNNs:
Architecture description
Training process
Dataset generation (train/validation/test)
Legal use of tools (proof if required)
4. Testing and Evaluation (CRITICAL)
A working implementation is NOT enough. You must demonstrate how well your AI performs.

Minimum expectations:
Test against:
random/naive agents (baseline)
heuristic agents
human players (if possible)
Run many games (not a few examples)
Report metrics such as:
win rate
score differences
robustness across conditions
A strong AI is one that performs consistently across diverse scenarios.

5. Special Requirement for Domino (TEAM GAME)
Domino introduces team dynamics and partner interaction.

You MUST evaluate:

Team performance (not just individual moves)
Partner sensitivity:
performance with strong vs weak partners
Opponent variation:
different teams and strategies
Suggested experiments:
(AI + AI) vs (AI + AI)
(AI + random) vs (random + random)
(AI + human) vs (human + human)
Self-play is encouraged, but NOT sufficient on its own.

6. Self-Play and Learning (Recommended)
You may use:

AI vs AI (self-play)
Strategy improvement over time
Model selection based on performance
However, you MUST still test against external opponents.

7. Oral Demonstration (“Happy Hour”)
If selected:

ALL team members must attend
ALL members must be able to explain:
the implementation
design decisions
results
8. Tools and Recommendations
Use Jupyter Notebooks for clarity and integration
Google Colab is recommended for GPU/TPU access (especially for DNNs)
9. Key Principles
Do NOT rely only on your own gameplay level
Do NOT assume your AI is strong without evidence
Do NOT skip evaluation
Your grade depends more on analysis and evaluation than on code size.

Final Thought
This assignment is not just about building an AI—it is about:

thinking strategically
designing experiments
understanding strengths and limitations
Take advantage of this opportunity to experiment, compete, and learn

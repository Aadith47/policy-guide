import sys
import time

from answer import answer_question

RUNS = 5
DELAY_SECONDS = 7  # free tier request limits

# Usage: python .\repeat_question.py can i get paid for overtime
if len(sys.argv) < 2:
    print("Usage: python .\\repeat_question.py <question>")
    sys.exit(1)

question = " ".join(sys.argv[1:])

# Same question many times: if the verdict changes, the model is unstable
for run in range(1, RUNS + 1):
    answer = answer_question(question)
    print(f"\nRun {run}: {answer['verdict']} | pages {answer['pages']}")
    print(f"  {answer['reason']}")
    time.sleep(DELAY_SECONDS)
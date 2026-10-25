import json
from pathlib import Path

from search import search

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FILE = BASE_DIR / "data" / "test_questions.json"
K_VALUES = (3, 5)


def check_retrieval():
    cases = json.loads(TEST_FILE.read_text(encoding="utf-8"))
    # Only cases with an expected page can be judged here
    cases = [case for case in cases if case.get("expected_page") is not None]

    for k in K_VALUES:
        hits = 0
        missed = []
        for case in cases:
            pages = [hit["page"] for hit in search(case["question"], top_k=k)]
            if case["expected_page"] in pages:
                hits += 1
            else:
                missed.append((case["question"], case["expected_page"], pages))

        print(f"\nTop {k}: right page found {hits}/{len(cases)}")
        for question, expected, pages in missed:
            print(f"  MISS: {question}\n    wanted p{expected}, got {pages}")


if __name__ == "__main__":
    check_retrieval()
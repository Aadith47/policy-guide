import json
import time
from collections import Counter
from pathlib import Path

from answer import answer_question

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FILE = BASE_DIR / "data" / "test_questions.json"
RESULTS_FILE = BASE_DIR / "data" / "results.json"
DELAY_SECONDS = 7  # the free tier has low request limits, so we slow down


def run_tests():
    cases = json.loads(TEST_FILE.read_text(encoding="utf-8"))
    results = []

    for case in cases:
        try:
            answer = answer_question(case["question"])
        except Exception as error:
            # One failed call should not kill a 30-question run
            print(f"ERROR on '{case['question']}': {error}")
            answer = {"verdict": "ERROR", "pages": [], "reason": str(error)}

        expected_page = case.get("expected_page")
        # Some rules live on more than one page, so extra pages can be marked ok
        acceptable = {expected_page, *case.get("also_ok_pages", [])}
        results.append(
            {
                "question": case["question"],
                "expected_verdict": case["expected_verdict"],
                "got_verdict": answer["verdict"],
                "expected_page": expected_page,
                "got_pages": answer["pages"],
                "got_reason": answer["reason"],
                "verdict_ok": answer["verdict"] == case["expected_verdict"],
                # The page only matters when the case expects one
                "page_ok": expected_page is None
                or bool(acceptable & set(answer["pages"])),
            }
        )
        time.sleep(DELAY_SECONDS)

    return results


def print_report(results):
    total = len(results)
    verdict_hits = sum(1 for item in results if item["verdict_ok"])
    with_page = [item for item in results if item["expected_page"] is not None]
    page_hits = sum(1 for item in with_page if item["page_ok"])

    print(f"\nVerdict accuracy: {verdict_hits}/{total}")
    print(f"Right page cited: {page_hits}/{len(with_page)}")

    # Which mistakes happen most: (expected -> got)
    pairs = Counter(
        (item["expected_verdict"], item["got_verdict"]) for item in results
    )
    print("\nExpected -> Got")
    for (expected, got), count in sorted(pairs.items()):
        print(f"  {expected} -> {got}: {count}")

    print("\nFailures")
    for item in results:
        if not (item["verdict_ok"] and item["page_ok"]):
            print(
                f"  {item['question']}\n"
                f"    expected {item['expected_verdict']} p{item['expected_page']}, "
                f"got {item['got_verdict']} p{item['got_pages']}\n"
                f"    reason: {item['got_reason']}"
            )


if __name__ == "__main__":
    results = run_tests()
    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print_report(results)
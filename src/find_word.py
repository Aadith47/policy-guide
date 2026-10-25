import sys

from search import search

# Usage: python .\find_word.py smok can i smoke in the lobby
# First word = what to look for, the rest = the question
keyword = sys.argv[1].lower()
question = " ".join(sys.argv[2:])

for hit in search(question):
    print(f"\n--- page {hit['page']} ---")
    # Rough sentence split is good enough for a quick check
    for sentence in hit["text"].split(". "):
        if keyword in sentence.lower():
            print("  -", sentence.strip())
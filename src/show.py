import sys

from search import search

# Usage: python .\show.py can I work from home 3 days a week
question = " ".join(sys.argv[1:])

# Print the full text, not a preview, so we can judge the chunk properly
for hit in search(question):
    print(f"\n--- page {hit['page']} | {hit['distance']:.3f} ---")
    print(hit["text"])
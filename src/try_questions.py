from search import search

QUESTIONS = [
    "Can I smoke in the lobby?",
    "I'm sick today, what do I do?",
    "Can I date my manager?",
    "Can I work from home 3 days a week?",
    "Can I hire my cousin onto my team?",
    "Can I take leave without informing HR?",
    "How many days can I work from home?",
    "Can I get paid for overtime?"
]

# Top 3 hits per question, short preview so we can judge them quickly
for question in QUESTIONS:
    print(f"\nQ: {question}")
    for hit in search(question):
        preview = hit["text"][:120]
        print(f"  page {hit['page']} | {hit['distance']:.3f} | {preview}")
# PolicyGuide

A RAG assistant that helps new employees check if an action follows or breaks company policy. It answers from the handbook text only, and shows the page it used.

![How PolicyGuide works](docs/pipeline.png)

## What it does

You type a question, such as "Can I smoke in the lobby?" The assistant replies with:

- **Verdict:** Allowed, Violation, Depends, or Unclear
- **Reason:** a short explanation, taken from the handbook
- **Pages:** the handbook pages it relied on
- **Next step:** what to do, or who to ask
- **Evidence:** the handbook text behind the answer, so you can check it yourself

If the handbook does not cover a question, the assistant says so and tells the user to ask HR. It does not guess.

## The app

The interface is a Streamlit web app (`src/app.py`):

- A question box with a few example questions to click
- A colour-coded verdict (green for Allowed, red for Violation, yellow for Depends, blue for Unclear)
- An expandable section with the exact handbook text used for the answer
- A clear message if the model cannot be reached, instead of a crash
- A limit of 20 questions per session, to protect the free API quota

On the first start, the app builds the search index by itself if it is missing.

## How it works

1. **Ingest:** `src/ingest.py` reads the handbook PDF and splits each page into chunks. Each chunk keeps its page number.
2. **Index:** `src/store.py` turns the chunks into vectors with a free embedding model (Chroma's default, all-MiniLM-L6-v2) and saves them in a local `db/` folder.
3. **Search:** `src/search.py` finds the chunks closest in meaning to the question.
4. **Answer:** `src/answer.py` sends those chunks and the question to Google Gemini with a strict prompt. The model must reply in JSON. The code then checks the reply.
5. **App:** `src/app.py` shows the answer in the browser.
6. **Evaluate:** `src/eval.py` runs a fixed test set and reports the score.

## Guardrails

These are layered. None of them is a complete defence on its own.

- **Input checks:** empty, very long, or obviously manipulative questions are refused before any API call.
- **Prompt design:** the question and the handbook excerpts are labelled as data. The model is told not to follow instructions inside them, and to answer only from the excerpts.
- **Citation check:** a decisive verdict (Allowed, Violation, Depends) is only accepted if it cites a page that search actually returned. Otherwise the answer becomes Unclear.
- **Reply check:** a reply that is not valid JSON is retried, then replaced with a safe "ask HR" answer. An unquoted key from the model is repaired before parsing.
- **Network errors:** dropped connections are retried. If the model cannot be reached at all, the code raises an error instead of returning a fake answer, and the app shows a clear message.

## Results

Test set: 19 questions in `data/test_questions.json`. Most were written by an AI assistant, and some by me. Each has an expected verdict and, where the handbook covers it, an expected page.

| Run | Verdict accuracy | Correct page cited |
|---|---|---|
| Final run | 19/19 | 16/16 |

I ran it several times with the same settings. One earlier run scored 18/19 because a network error stopped one question. I count that as a failure, and I added the retry after it.

**Two test labels were corrected** after I checked the handbook text. In both cases the bot's answer matched the document and my first label did not.

The test set checks the answers from `answer_question()`. It does not test the web interface.

### Known limits

- The test set is small (19 questions), and most questions were written by the same people who built the bot. The score shows the bot works on these cases. It does not prove general accuracy.
- The bot once dropped a condition in "more than one remote day needs manager approval". A prompt rule now handles it. It is the kind of rule that could break other answers, so the test set should be run again after any change.
- The handbook is a sample template from a public source, with placeholder text. It is not a real company's policy, and some parts read like a US-style document.
- The question limit in the app is easy to get around by refreshing the page. It only protects against accidents.
- The assistant is a guide, not a legal or HR decision. HR has the final say.

## Setup

Requirements: Python 3.10 or newer, and a free Gemini API key from Google AI Studio.

```bash
git clone https://github.com/Aadith47/policy-guide.git
cd policy-guide
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a file named `.env` in the project root:

```
GEMINI_API_KEY=your-key-here
```

Never commit `.env` or the `db/` folder. The `.gitignore` already lists them.

The first run downloads a small embedding model (about 80 MB), so it needs an internet connection and takes longer.

## Run the app

From the project root (`policy-guide`):

```bash
streamlit run src/app.py
```

A browser tab opens at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push the repository to GitHub, without `.env` and without `db/`.
2. In Streamlit Community Cloud, create a new app from the repository and set the main file to `src/app.py`.
3. In the app's **Secrets** settings, add:

```toml
GEMINI_API_KEY = "your-key-here"
```

The app builds the index on its first start, so the first load is slow.

## Other scripts

From the `src` folder:

```bash
python store.py              # build the index (the app also does this when it is missing)
python eval.py               # run the test set and print the score
python retrieval_check.py    # check search only, no API calls
```

To ask a single question without the app:

```bash
python -c "from answer import answer_question; print(answer_question('Can I smoke in the lobby?'))"
```

## Project layout

```
policy-guide/
├── data/
│   ├── handbook.pdf
│   └── test_questions.json
├── docs/
│   └── pipeline.png
├── src/
│   ├── app.py
│   ├── ingest.py
│   ├── store.py
│   ├── search.py
│   ├── answer.py
│   ├── eval.py
│   ├── retrieval_check.py
│   └── experiment.py
├── requirements.txt
└── .gitignore
```

## Credits and sources

- Handbook: sample employee handbook template (Workable), used for learning and testing only.
- Built with pypdf, Chroma, google-genai, python-dotenv, and Streamlit.
- Built by [Aadith](https://github.com/Aadith47).
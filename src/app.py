import os

import streamlit as st

from answer import ModelUnavailableError, answer_question
from store import build_index, get_collection

MAX_QUESTIONS_PER_SESSION = 20  # protects the free API quota on a public app

EXAMPLE_QUESTIONS = [
    "Can I smoke in the lobby?",
    "Can I get paid for overtime?",
    "Can I work from home 3 days a week?",
    "Can I date my manager?",
]

# Colour and icon per verdict, so the answer is clear at a glance
VERDICT_STYLE = {
    "Allowed": (st.success, "✅"),
    "Violation": (st.error, "🚫"),
    "Depends": (st.warning, "⚠️"),
    "Unclear": (st.info, "❓"),
}

st.set_page_config(page_title="PolicyGuide", page_icon="📘")


def load_api_key():
    # Locally the key comes from .env (loaded in answer.py).
    # On Streamlit Cloud it comes from the app's secrets.
    if "GEMINI_API_KEY" in os.environ:
        return
    try:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass


@st.cache_resource(show_spinner="Preparing the handbook index...")
def ensure_index():
    # The db folder is not in git, so a fresh deployment starts with an empty index
    if get_collection().count() == 0:
        build_index()
    return True


def pick_example(text):
    st.session_state.question = text


def show_answer(answer):
    show_verdict, icon = VERDICT_STYLE.get(answer["verdict"], (st.info, "❓"))
    show_verdict(f"{icon} **{answer['verdict']}**")
    st.write(answer["reason"])

    pages = ", ".join(str(page) for page in answer["pages"])
    if pages:
        st.markdown(f"**Handbook pages:** {pages}")
    st.markdown(f"**Next step:** {answer['next_step']}")

    # Show the evidence, so the user can check the answer instead of trusting it
    sources = answer.get("sources", [])
    if sources:
        with st.expander("Show the handbook text used"):
            for source in sources:
                st.caption(f"Page {source['page']}")
                st.write(source["text"])


load_api_key()
ensure_index()

st.title("📘 PolicyGuide")
st.caption(
    "Ask if something follows or breaks the company handbook. "
    "Answers come only from the handbook text."
)

with st.expander("Usually asked"):
    for example in EXAMPLE_QUESTIONS:
        st.button(example, on_click=pick_example, args=(example,), key=f"ex_{example}")

with st.form("ask_form"):
    question = st.text_input(
        "Your question",
        key="question",
        placeholder="e.g. Can I smoke in the lobby?",
    )
    submitted = st.form_submit_button("Ask", type="primary")

if submitted and question.strip():
    asked = st.session_state.get("asked", 0)
    if asked >= MAX_QUESTIONS_PER_SESSION:
        st.warning("You reached the question limit for this session.")
        st.stop()
    st.session_state.asked = asked + 1

    with st.spinner("Reading the handbook..."):
        try:
            answer = answer_question(question)
        except ModelUnavailableError:
            st.error("The assistant could not be reached. Please try again in a moment.")
            st.stop()
        except RuntimeError:
            st.error("The app is not set up correctly (the API key is missing).")
            st.stop()
    show_answer(answer)

st.divider()
st.caption(
    "A guide, not an HR decision. Based on a sample employee handbook, "
    "not a real company's policy. When unsure, ask HR."
)
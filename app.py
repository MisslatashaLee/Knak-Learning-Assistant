import streamlit as st
import anthropic
from pathlib import Path

# Page setup
st.set_page_config(
    page_title="Knak Learning Assistant",
    page_icon="📧"
)
st.markdown("""
<style>

    .stApp {
        background-color: #f7f8fc;
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
    }

    h1 {
        text-align: center;
        font-size: 42px !important;
        margin-bottom: 5px;
    }

.subtitle {
    text-align: center;
    color: #5f6f7f;
    font-size: 17px;
    margin-bottom: 12px;
}

.subtitle::after {
    content: "";
    display: block;
    width: 70px;
    height: 3px;
    background-color: #0093D0;
    margin: 14px auto 24px auto;
    border-radius: 2px;
}
.stChatInput {
    border-radius: 12px;
}

.stChatInput > div {
    border: 2px solid #0093D0 !important;
    border-radius: 12px !important;
}
/* User chat icon - dark blue */
[data-testid="stChatMessageAvatarUser"] {
    background-color: #0067A0 !important;
    color: white !important;
}

/* Assistant chat icon - bright blue */
[data-testid="stChatMessageAvatarAssistant"] {
    background-color: #0093D0 !important;
    color: white !important;
}
h1 {
    color: #0067A0 !important;
}
h2, h3 {
    color: #0093D0 !important;
}
</style>
""", unsafe_allow_html=True)
st.title("📧 Knak Learning Assistant")

st.markdown(
    """
    <div class="subtitle">
    Your AI learning companion for email creation and content authoring
    </div>
    """,
    unsafe_allow_html=True
)
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
# Connect to Claude
client = anthropic.Anthropic(
    api_key=st.secrets["ANTHROPIC_API_KEY"]
)

# Load the Knak knowledge base

def load_knowledge():
    return Path("knowledge_base.txt").read_text(encoding="utf-8")

knowledge_base = load_knowledge()

# Instructions for Claude
system_prompt = f"""
You are the Knak Learning Assistant.

Your purpose is to help new marketers learn basic email creation
and content authoring concepts.

Use the provided knowledge base as your only source of information.

Rules:
- Give clear, beginner-friendly explanations.
- Keep answers concise unless the user asks for more detail.
- Use examples only when they are supported by the knowledge base.
- Answer questions using only information explicitly stated in the knowledge base.
- Do not infer, assume, or add product behavior that is not explicitly stated.
- Do not invent company-specific processes, policies, features, or capabilities.
- Never claim to have access to confidential company information.
- If part of an answer is supported by the knowledge base but another part is not,
  answer only the supported portion.
  - Do not suggest external resources, documentation, websites, or next steps unless they are explicitly included in the knowledge base.
- If the answer is not available in the knowledge base, respond only:
  "I don't have that information in my learning materials yet."

KNOWLEDGE BASE:

{knowledge_base}
"""

# Conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat box
question = st.chat_input("Ask a question about email creation...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=500,
                system=system_prompt,
                messages=st.session_state.messages
            )

            answer = response.content[0].text
            fallback = "I don't have that information in my learning materials yet."

            if fallback in answer:
                answer = fallback

            st.write(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
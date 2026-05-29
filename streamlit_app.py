import base64
from pathlib import Path

import streamlit as st

from scripts.chatbot import CustomerServiceChatbot


st.set_page_config(
    page_title="Lovehoney Product Finder",
    layout="centered",
    initial_sidebar_state="expanded",
)

@st.cache_resource(show_spinner="Loading chatbot...")
def load_chatbot():
    return CustomerServiceChatbot()


@st.cache_data
def load_background_image():
    image_path = Path(__file__).resolve().parent / "image.png"
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def main():
    background_image = load_background_image()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(8, 10, 18, 0.72), rgba(8, 10, 18, 0.72)),
                url("data:image/png;base64,{background_image}");
            background-size: 420px 420px;
            background-repeat: repeat;
            background-attachment: fixed;
        }}

        .rainbow-title {{
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.2;
            margin: 0 0 1.5rem 0;
        }}

        [data-testid="stChatMessage"] {{
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin: 0.85rem 0;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.24);
            border: 1px solid rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(6px);
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
            background: rgba(91, 44, 111, 0.92);
            color: #ffffff;
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
            background: rgba(255, 255, 255, 0.94);
            color: #17151c;
            border-color: rgba(91, 44, 111, 0.22);
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) li,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) span {{
            color: #17151c;
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) li,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span {{
            color: #ffffff;
        }}
        </style>
        <h1 class="rainbow-title">
            <span style="color:#ff4b4b;">Love</span><span style="color:#ff9f1c;">honey</span>
            <span style="color:#ffd166;">Product</span>
            <span style="color:#06d6a0;">Find</span><span style="color:#4dabf7;">er</span>
        </h1>
        """,
        unsafe_allow_html=True,
    )

    chatbot = load_chatbot()

    if "product_discovery_session" not in st.session_state:
        result = chatbot.start_product_discovery()
        st.session_state["product_discovery_session"] = result["session"]
        st.session_state["messages"] = [  # Start visible chat history.
            {
                "role": "assistant",  # First visible message is from the assistant.
                "content": result["answer"],  # Show the first category question.
                "sources": "",  # No sources for an opening question.
            }
        ]
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption("Sources")
                st.markdown(message["sources"]) 
    
           
    user_query = st.chat_input(
        "Tell me what you are looking for",
        max_chars=250,
    )
    
    if not user_query:
        return
    
    st.session_state["messages"].append({
                                        "role": "user",  # Store user role.
                                        "content": user_query,  # Store submitted answer.
                                        "sources": "",  # User messages do not have sources.
                                        })

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result = chatbot.handle_message(
                    user_query,
                    st.session_state["product_discovery_session"],
                    )
                st.session_state["product_discovery_session"] = result.get(
                    "session",
                    st.session_state["product_discovery_session"]
                )

            st.markdown(result["answer"])
            sources = result.get("sources", "")
            if sources:
                st.caption("Sources")
                st.markdown(sources)

            st.session_state["messages"].append({
                                                "role": "assistant",  # Store assistant role.
                                                "content": result["answer"],  # Store visible assistant text.
                                                "sources": sources,  # Store final sources when present.
                                                })

        except Exception as exc:
            st.error("Unable to generate an answer, please retry")
            st.exception(exc)


if __name__ == "__main__":
    main()

"""Chat message display component."""

import streamlit as st


def display_message(role: str, content: str) -> None:
    """
    Display a chat message.

    Args:
        role: "user" or "assistant"
        content: Message content (supports markdown)
    """
    avatar = "👤" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def display_message_history(messages: list) -> None:
    """
    Display all messages in history.

    Args:
        messages: List of {"role": str, "content": str} dicts
    """
    for msg in messages:
        display_message(msg["role"], msg["content"])

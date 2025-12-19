"""Chat input component."""

from collections.abc import Callable

import streamlit as st


def chat_input_area(
    on_submit: Callable[[str], None], placeholder: str = "What would you like to do?"
) -> None:
    """
    Display chat input with submit handling.

    Args:
        on_submit: Callback function when user submits message
        placeholder: Input placeholder text
    """
    if prompt := st.chat_input(placeholder):
        on_submit(prompt)

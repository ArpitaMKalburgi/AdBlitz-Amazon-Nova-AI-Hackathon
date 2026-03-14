import streamlit as st


def render_refine_bar(on_refine):
    st.divider()
    st.subheader("🔁 Refine Your Campaign")

    col1, col2 = st.columns([4, 1])
    with col1:
        feedback = st.text_input(
            "Not happy with something? Tell us what to change...",
            placeholder=(
                "e.g. Make the copy more playful, "
                "target a younger audience, use warmer colors..."
            )
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        regenerate = st.button(
            "🔄 Regenerate", type="primary", use_container_width=True
        )

    if regenerate:
        if feedback.strip():
            on_refine(feedback)
        else:
            st.warning("Please describe what you'd like to change before regenerating.")
import streamlit as st


def render_image_gallery(images):
    st.subheader("🖼️ Generated Ad Creatives")

    cols = st.columns(3)
    for i, img in enumerate(images):
        with cols[i % 3]:
            label   = img["format"].replace("_", " ").title()
            caption = f"{label} — {img['platform']} | {img['description']}"
            with st.expander(f"🖼️ {label}", expanded=True):
                st.image(img["url"], caption=caption, use_container_width=True)
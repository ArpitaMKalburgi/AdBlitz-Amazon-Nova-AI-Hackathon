import streamlit as st


def render_upload(on_generate):
    st.subheader("📸 Upload Your Product Photo")

    col1, col2 = st.columns([1, 1])

    with col1:
        # ── Input method toggle ───────────────────────────────
        input_method = st.radio(
            "How do you want to add your product photo?",
            ["📁 Upload a file", "📷 Take a photo"],
            horizontal=True
        )

        uploaded_file = None

        if input_method == "📁 Upload a file":
            uploaded_file = st.file_uploader(
                "Upload product photo",
                type=["png", "jpg", "jpeg"],
                help="Upload a clear product image for best results"
            )

        elif input_method == "📷 Take a photo":
            uploaded_file = st.camera_input(
                "Point your camera at the product and click the button"
            )

        # ── Preview ───────────────────────────────────────────
        if uploaded_file:
            st.image(
                uploaded_file,
                caption="Product Preview",
                use_container_width=True
            )

    with col2:
        if uploaded_file:
            st.success("✅ Product photo ready!")
            st.markdown("**What happens next:**")
            st.markdown("- 🧠 Brand Agent analyzes your product")
            st.markdown("- ✍️ Copy Agent writes platform-specific ads")
            st.markdown("- 🎨 Visual Agent generates ad creatives")
            st.markdown("- 👥 Audience Agent builds personas")
            st.markdown("- 📊 Media Plan Agent creates launch strategy")

            if st.button(
                "🚀 Generate Campaign",
                type="primary",
                use_container_width=True
            ):
                on_generate(uploaded_file)
        else:
            st.info("👆 Upload or take a photo to get started")
            st.markdown("**Supported formats:** PNG, JPG, JPEG")
            st.markdown("**Best results:** Clear photo, good lighting, neutral background")
            st.markdown("**📷 Camera tip:** Make sure product fills the frame")

    return uploaded_file
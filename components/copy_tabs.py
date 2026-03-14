import streamlit as st


def render_copy_tabs(copy):
    st.subheader("✍️ Ad Copy — All Platforms")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📸 Instagram", "👥 Facebook", "🔍 Google", "🎵 TikTok", "📧 Email"
    ])

    # ── Instagram ──────────────────────────────────────────────
    with tab1:
        ig = copy["instagram"]
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**🎣 Hook:**")
            st.info(ig["hook"])
            st.markdown("**📝 Body:**")
            st.write(ig["body"])
            st.markdown("**📣 CTA:**")
            st.success(ig["cta"])
        with col2:
            st.markdown("**#️⃣ Hashtags:**")
            hashtags = ig["hashtags"]
            # Contract defines hashtags as array — handle both just in case
            if isinstance(hashtags, list):
                for tag in hashtags:
                    st.markdown(f"`{tag}`")
            else:
                for tag in hashtags.split():
                    st.markdown(f"`{tag}`")

    # ── Facebook ───────────────────────────────────────────────
    with tab2:
        fb = copy["facebook"]
        st.markdown("**📰 Headline:**")
        st.info(fb["headline"])
        st.markdown("**📝 Primary Text:**")
        st.write(fb["primary_text"])
        st.markdown("**📋 Description:**")
        st.caption(fb["description"])
        st.markdown("**📣 CTA:**")
        st.success(fb["cta"])
        if fb.get("long_body"):
            with st.expander("📖 Long-form version"):
                st.write(fb["long_body"])

    # ── Google ─────────────────────────────────────────────────
    with tab3:
        g = copy["google"]
        st.markdown("**📰 Headlines:**")
        for i, h in enumerate(g["headlines"], 1):
            st.markdown(f"**H{i}:** {h}")
        st.markdown("---")
        st.markdown("**📝 Descriptions:**")
        for i, d in enumerate(g["descriptions"], 1):
            st.markdown(f"**D{i}:** {d}")
        if g.get("keywords"):
            st.markdown("---")
            st.markdown("**🔑 Target Keywords:**")
            st.write("  ·  ".join(g["keywords"]))

    # ── TikTok ─────────────────────────────────────────────────
    with tab4:
        tt = copy["tiktok"]
        st.markdown("**🎣 Hook:**")
        st.info(tt["hook"])
        st.markdown("**🎬 Scene Breakdown:**")
        for scene in tt["scenes"]:
            with st.expander(f"⏱️ {scene['time']}", expanded=True):
                st.write(scene["action"])
        st.markdown("**📣 CTA:**")
        st.success(tt["cta"])
        if tt.get("suggested_audio"):
            st.markdown(f"**🎵 Suggested Audio:** {tt['suggested_audio']}")

    # ── Email ──────────────────────────────────────────────────
    with tab5:
        em = copy["email"]
        st.markdown("**📨 Subject Lines (A/B test these):**")
        for i, subj in enumerate(em["subject_lines"], 1):
            st.markdown(f"**Option {i}:** `{subj}`")
        st.markdown(f"**👁️ Preview Text:** *{em['preview_text']}*")
        st.markdown("---")
        st.markdown("**📧 Email Body:**")
        st.text(em["body"])
import streamlit as st


def render_video_player(video):
    st.subheader("🎬 Video Ad")

    voiceover_label = "with AI voiceover" if video.get("has_voiceover") else "no voiceover"
    duration        = f"{video['duration_seconds']} seconds"
    voice_style     = video.get("voice_style", "N/A")

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                    padding: 24px; border-radius: 16px;
                    text-align: center; margin-bottom: 16px;">
            <h3 style="color:#FFD700; margin:0;">
                ⭐ {duration} video ad {voiceover_label}
            </h3>
            <p style="color:#aaa; margin:6px 0 0 0;">
                Voice style: <em>{voice_style}</em>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.video(video["url"])

    # Extra detail expanders
    if video.get("voiceover_script"):
        with st.expander("🎙️ Voiceover Script"):
            st.write(video["voiceover_script"])

    if video.get("video_prompt_used"):
        with st.expander("🎬 Video Generation Prompt"):
            st.caption(video["video_prompt_used"])
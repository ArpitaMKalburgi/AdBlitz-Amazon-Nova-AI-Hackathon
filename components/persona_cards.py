import streamlit as st

# UI-only colors — not from data contract
CARD_COLORS = ["#F4E1D2", "#C9A96E", "#D4AF91"]


def render_persona_cards(personas):
    st.subheader("👥 Target Audience Personas")

    cols = st.columns(3)
    for i, persona in enumerate(personas):
        color = CARD_COLORS[i % len(CARD_COLORS)]
        with cols[i]:
            # Header card
            st.markdown(
                f"""
                <div style="border:2px solid {color}; border-radius:12px;
                            padding:16px; background:{color}22; margin-bottom:10px;">
                    <h3 style="margin:0; color:#333;">{persona['name']}</h3>
                    <p style="margin:4px 0; color:#555;">
                        🎂 Age: <strong>{persona['age']}</strong>
                    </p>
                    <p style="margin:4px 0; color:#555;">💼 {persona['job']}</p>
                    <p style="margin:4px 0; color:#555;">💰 {persona.get('income','N/A')}</p>
                    <p style="margin:4px 0; color:#555;">
                        🕐 {persona.get('active_times','N/A')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("**📱 Platforms:**")
            st.write("  ·  ".join(persona["platforms"]))

            if persona.get("values"):
                st.markdown("**💎 Values:**")
                for v in persona["values"]:
                    st.markdown(f"- {v}")

            st.markdown("**😤 Pain Points:**")
            for point in persona["pain_points"]:
                st.markdown(f"- {point}")

            if persona.get("how_they_discover"):
                st.markdown("**🔍 How They Discover:**")
                st.caption(persona["how_they_discover"])

            st.markdown("**💡 Buying Triggers:**")
            for trigger in persona["buying_triggers"]:
                st.markdown(f"- {trigger}")

            if persona.get("buying_blockers"):
                st.markdown("**🚫 Won't Buy If:**")
                for blocker in persona["buying_blockers"]:
                    st.markdown(f"- {blocker}")

            st.markdown("**🎯 Best Ad Format:**")
            st.info(persona["best_ad_format"])
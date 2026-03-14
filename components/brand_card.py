import streamlit as st


def render_brand_card(brand):
    st.subheader("🎨 Brand Identity")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"### {brand['product_name']}")
        st.markdown(f"**Category:** {brand['category']}")
        st.markdown(f"**Target Audience:** {brand['target_audience']}")
        st.markdown(f"**Emotional Angle:** {brand['emotional_angle']}")

        st.markdown("**Brand Vibe:**")
        st.info(brand['brand_vibe'])

        st.markdown("**Brand Voice:**")
        st.info(brand['brand_voice'])

    with col2:
        st.markdown("**Color Palette:**")
        color_html = "<div style='display:flex; gap:12px; flex-wrap:wrap; margin-bottom:16px;'>"
        for color in brand['color_palette']:
            color_html += f"""
                <div style='display:flex; flex-direction:column; align-items:center; gap:4px;'>
                    <div style='width:52px; height:52px; border-radius:50%;
                                background-color:{color};
                                border:2px solid #ddd;
                                box-shadow:0 2px 6px rgba(0,0,0,0.12);'></div>
                    <span style='font-size:10px; color:#666;'>{color}</span>
                </div>"""
        color_html += "</div>"
        st.markdown(color_html, unsafe_allow_html=True)

        st.markdown("**Taglines:**")
        for tagline in brand['taglines']:
            st.markdown(f"> *\"{tagline}\"*")

    st.markdown("**Key Selling Points:**")
    sp_cols = st.columns(len(brand['selling_points']))
    for i, point in enumerate(brand['selling_points']):
        with sp_cols[i]:
            st.success(f"✅ {point}")
import streamlit as st
import plotly.express as px
import pandas as pd


def render_media_plan(media_plan):
    st.subheader("📊 Media Plan & Launch Strategy")

    # Daily budget banner
    if media_plan.get("daily_budget_recommendation"):
        st.info(
            f"💰 Recommended daily budget: "
            f"**{media_plan['daily_budget_recommendation']}**"
        )

    col1, col2 = st.columns([1, 1])

    # Budget pie chart
    with col1:
        st.markdown("**💰 Budget Allocation:**")
        budget = media_plan["budget_split"]
        fig = px.pie(
            names=list(budget.keys()),
            values=list(budget.values()),
            title="Ad Spend Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.3
        )
        fig.update_layout(margin=dict(t=40, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    # Platform strategy
    with col2:
        st.markdown("**🎯 Platform Strategy:**")
        for p in media_plan.get("platform_strategy", []):
            with st.expander(f"📱 {p['platform']}"):
                st.write(f"**Creatives:** {', '.join(p['creatives'])}")
                st.write(f"**Targeting:** {p['targeting']}")
                st.write(f"**Why:** {p['why']}")

    # A/B tests
    st.markdown("**🧪 A/B Test Plan:**")
    for ab in media_plan.get("ab_tests", []):
        with st.expander(f"Test: {ab['test']}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Variant A:** {ab['variant_a']}")
            with col_b:
                st.markdown(f"**Variant B:** {ab['variant_b']}")
            st.info(
                f"📏 Metric: **{ab['metric']}**  |  "
                f"Duration: **{ab.get('duration','N/A')}**  |  "
                f"Winner rule: {ab.get('winner_rule','N/A')}"
            )

    # 7-day calendar
    st.markdown("**📅 7-Day Launch Calendar:**")
    df = pd.DataFrame(media_plan["seven_day_calendar"])
    # Rename columns for display
    df.columns = [c.replace("_", " ").title() for c in df.columns]
    st.dataframe(df, use_container_width=True, hide_index=True)
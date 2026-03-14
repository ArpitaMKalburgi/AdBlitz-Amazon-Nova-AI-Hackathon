import streamlit as st
import time


def render_loading():
    st.subheader("⚙️ Campaign Generation in Progress")

    agents = [
        ("🧠 Brand Agent",     "Analyzing product & building brand identity"),
        ("✍️ Copy Agent",      "Writing platform-specific ad copy"),
        ("🎨 Visual Agent",    "Generating ad creatives"),
        ("👥 Audience Agent",  "Building audience personas"),
        ("📊 Media Plan Agent","Creating 7-day launch strategy"),
    ]

    progress_bar = st.progress(0)
    status_container = st.empty()

    for i in range(len(agents)):
        lines = []
        for j, (name, desc) in enumerate(agents):
            if j < i:
                lines.append(f"✅ **{name}** — {desc}")
            elif j == i:
                lines.append(f"⏳ **{name}** — {desc}...")
            else:
                lines.append(f"🔘 **{name}** — Waiting...")
        status_container.markdown("\n\n".join(lines))
        progress_bar.progress((i + 1) / len(agents))
        time.sleep(0.8)

    # Final state — all done
    status_container.markdown("\n\n".join(
        [f"✅ **{name}** — {desc}" for name, desc in agents]
    ))
    progress_bar.progress(1.0)
    st.success("🎉 Campaign generated! Scroll down to explore.")
    time.sleep(0.4)
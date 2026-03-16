import streamlit as st


def _icon_box(platform):
    m = {
        "instagram": (
            "linear-gradient(135deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)",
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/></svg>',
        ),
        "facebook": (
            "#1877F2",
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white" stroke="none"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>',
        ),
        "google": (
            "#1a1a3e",
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>',
        ),
        "tiktok": (
            "#000",
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"/></svg>',
        ),
        "email": (
            "#1a3a5e",
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>',
        ),
        "twitter": (
            "#000",
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white" stroke="none"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
        ),
    }
    bg, svg = m.get(platform, ("#7c3aed", ""))
    return f'<div style="width:38px;height:38px;border-radius:10px;background:{bg};display:flex;align-items:center;justify-content:center;flex-shrink:0;">{svg}</div>'


def _header(pk, label):
    return f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #1a1a3e;">{_icon_box(pk)}<span style="font-size:1.1rem;font-weight:700;color:#e8e8ff;">{label}</span></div>'


def _scene_time(scene, index):
    return str(scene.get("time") or scene.get("time_start") or f"Scene {index + 1}")


def _scene_text(scene):
    for key in ("action", "description", "text", "scene", "visual"):
        value = scene.get(key)
        if value:
            return str(value)
    return "Scene details unavailable."


def render_copy_tabs(copy):
    c1, c2 = st.columns(2)
    with c1:
        ig = copy["instagram"]
        st.markdown(
            f'<div class="platform-card">{_header("instagram","Instagram")}<div style="margin-bottom:16px;"><div class="copy-label copy-label-hook">HOOK</div><div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:10px;padding:14px;color:#e8e8ff;">"{ig["hook"]}"</div></div><div><div class="copy-label copy-label-body">BODY COPY</div><div style="color:#8888aa;line-height:1.6;font-size:0.9rem;">{ig["body"].replace(chr(10),"<br>")}</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:#111128;border:1px solid #1a1a3e;border-radius:0 0 16px 16px;padding:0 24px 20px;margin-top:-17px;"><div class="copy-label copy-label-cta">CTA</div><div class="cta-box" style="display:flex;justify-content:space-between;align-items:center;">{ig["cta"]}<span style="color:#a78bfa;">-></span></div></div>',
            unsafe_allow_html=True,
        )
        ht = ig.get("hashtags", [])
        if ht:
            t = "".join([f'<span class="tag">{h}</span>' for h in ht])
            st.markdown(
                f'<div class="dark-card"><div class="copy-label" style="color:#6666aa;">HASHTAGS</div><div class="tag-container">{t}</div></div>',
                unsafe_allow_html=True,
            )

    with c2:
        fb = copy["facebook"]
        body = fb.get("long_body", fb.get("primary_text", "")).replace("\n", "<br>")
        st.markdown(
            f'<div class="platform-card">{_header("facebook","Facebook")}<div style="margin-bottom:16px;"><div class="copy-label copy-label-hook">HOOK</div><div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:10px;padding:14px;color:#e8e8ff;">"{fb["headline"]}"</div></div><div><div class="copy-label copy-label-body">BODY COPY</div><div style="color:#8888aa;line-height:1.6;font-size:0.9rem;">{body}</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:#111128;border:1px solid #1a1a3e;border-radius:0 0 16px 16px;padding:0 24px 20px;margin-top:-17px;"><div class="copy-label copy-label-cta">CTA</div><div class="cta-box" style="display:flex;justify-content:space-between;align-items:center;">{fb["cta"]}<span style="color:#a78bfa;">-></span></div></div>',
            unsafe_allow_html=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        tt = copy["tiktok"]
        st.markdown(
            f'<div class="platform-card">{_header("tiktok","TikTok")}<div style="margin-bottom:16px;"><div class="copy-label copy-label-hook">HOOK</div><div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:10px;padding:14px;color:#e8e8ff;">"{tt["hook"]}"</div></div><div class="copy-label copy-label-body">SCENE BREAKDOWN</div></div>',
            unsafe_allow_html=True,
        )
        for index, scene in enumerate(tt.get("scenes", [])):
            st.markdown(
                f'<div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:8px;padding:10px 12px;margin-bottom:6px;display:flex;align-items:center;gap:10px;"><span style="color:#a78bfa;font-weight:700;font-size:0.8rem;white-space:nowrap;">{_scene_time(scene, index)}</span><span style="color:#8888aa;font-size:0.9rem;">{_scene_text(scene)}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div style="margin-top:10px;"><div class="copy-label copy-label-cta">CTA</div><div class="cta-box" style="display:flex;justify-content:space-between;align-items:center;">{tt["cta"]}<span style="color:#a78bfa;">-></span></div></div>',
            unsafe_allow_html=True,
        )

    with c4:
        g = copy["google"]
        h_html = "<br>".join(
            [f'<span style="color:#a78bfa;font-weight:600;font-size:0.8rem;">H{i + 1}</span> <span style="color:#e8e8ff;">{headline}</span>' for i, headline in enumerate(g["headlines"])]
        )
        d_html = "<br>".join(
            [f'<span style="color:#fbbf24;font-weight:600;font-size:0.8rem;">D{i + 1}</span> <span style="color:#8888aa;">{description}</span>' for i, description in enumerate(g["descriptions"])]
        )
        st.markdown(
            f'<div class="platform-card">{_header("google","Google Search")}<div style="margin-bottom:16px;"><div class="copy-label copy-label-hook">HEADLINES</div><div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:10px;padding:14px;line-height:1.8;">{h_html}</div></div><div><div class="copy-label copy-label-body">DESCRIPTIONS</div><div style="color:#8888aa;line-height:1.8;">{d_html}</div></div></div>',
            unsafe_allow_html=True,
        )
        kw = g.get("keywords", [])
        if kw:
            t = "".join([f'<span class="tag">{k}</span>' for k in kw])
            st.markdown(
                f'<div class="dark-card"><div class="copy-label" style="color:#6666aa;">TARGET KEYWORDS</div><div class="tag-container">{t}</div></div>',
                unsafe_allow_html=True,
            )

    if "twitter" in copy:
        c5, c6 = st.columns(2)
        with c5:
            em = copy["email"]
            st.markdown(
                f'<div class="platform-card">{_header("email","Email")}<div class="copy-label copy-label-hook">SUBJECT LINES</div></div>',
                unsafe_allow_html=True,
            )
            for i, subj in enumerate(em["subject_lines"]):
                st.markdown(
                    f'<div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:8px;padding:10px 12px;margin-bottom:6px;color:#e8e8ff;"><span style="color:#5555aa;font-size:0.8rem;font-weight:600;">Option {i + 1}</span>  {subj}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div style="margin-top:12px;"><div class="copy-label copy-label-body">PREVIEW TEXT</div><div style="color:#8888aa;font-style:italic;font-size:0.9rem;">{em["preview_text"]}</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="margin-top:12px;"><div class="copy-label copy-label-body">EMAIL BODY</div><div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:10px;padding:16px;color:#8888aa;white-space:pre-wrap;line-height:1.6;font-size:0.9rem;">{em["body"]}</div></div>',
                unsafe_allow_html=True,
            )
        with c6:
            tw = copy["twitter"]
            hook = tw.get("hook", tw.get("headline", ""))
            body = tw.get("body", tw.get("primary_text", "")).replace("\n", "<br>")
            cta = tw.get("cta", "")
            st.markdown(
                f'<div class="platform-card">{_header("twitter","Twitter / X")}<div style="margin-bottom:16px;"><div class="copy-label copy-label-hook">HOOK</div><div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:10px;padding:14px;color:#e8e8ff;">"{hook}"</div></div><div><div class="copy-label copy-label-body">BODY COPY</div><div style="color:#8888aa;line-height:1.6;font-size:0.9rem;">{body}</div></div></div>',
                unsafe_allow_html=True,
            )
            if cta:
                st.markdown(
                    f'<div style="margin-top:8px;"><div class="copy-label copy-label-cta">CTA</div><div class="cta-box" style="display:flex;justify-content:space-between;align-items:center;">{cta}<span style="color:#a78bfa;">-></span></div></div>',
                    unsafe_allow_html=True,
                )
    else:
        em = copy["email"]
        st.markdown(
            f'<div class="platform-card">{_header("email","Email")}<div class="copy-label copy-label-hook">SUBJECT LINES</div></div>',
            unsafe_allow_html=True,
        )
        for i, subj in enumerate(em["subject_lines"]):
            st.markdown(
                f'<div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:8px;padding:10px 12px;margin-bottom:6px;color:#e8e8ff;"><span style="color:#5555aa;font-size:0.8rem;font-weight:600;">Option {i + 1}</span>  {subj}</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div style="margin-top:12px;"><div class="copy-label copy-label-body">PREVIEW TEXT</div><div style="color:#8888aa;font-style:italic;font-size:0.9rem;">{em["preview_text"]}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="margin-top:12px;"><div class="copy-label copy-label-body">EMAIL BODY</div><div style="background:#0a0a1a;border:1px solid #1a1a3e;border-radius:10px;padding:16px;color:#8888aa;white-space:pre-wrap;line-height:1.6;font-size:0.9rem;">{em["body"]}</div></div>',
            unsafe_allow_html=True,
        )

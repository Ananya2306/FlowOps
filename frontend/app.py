"""
app.py  —  FlowOps Frontend (Fixed render issues)
"""

import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from frontend.services.api_client import (
    fetch_zones, fetch_recommendation, post_simulate, post_reset, check_health
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FlowOps — Exit Guide",
    page_icon="🚪",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, .stApp { background-color:#0d1117; color:#e2e8f0;
    font-family:'Segoe UI',system-ui,-apple-system,sans-serif; }
#MainMenu,footer,header,[data-testid="stToolbar"]{ visibility:hidden; }
.block-container{ padding-top:2rem; padding-bottom:4rem; max-width:720px; }
section[data-testid="stSidebar"]{ background:#0f172a; }
.stButton>button{ width:100%; background:#1e293b; color:#94a3b8;
    border:1px solid #334155; border-radius:8px; font-size:0.82rem;
    font-weight:500; padding:6px 14px; }
.stButton>button:hover{ background:#334155; color:#e2e8f0; border-color:#475569; }
[data-testid="stExpander"]{ background:#0f172a;
    border:1px solid #1e293b !important; border-radius:10px !important; }
hr{ border-color:#1e293b !important; margin:1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

STATUS_COLOR = {"LOW":"#22c55e","MEDIUM":"#eab308","HIGH":"#f97316","CRITICAL":"#ef4444"}
STATUS_LABEL = {"LOW":"Clear","MEDIUM":"Moderate","HIGH":"Busy","CRITICAL":"Congested"}

# ── Health check ──────────────────────────────────────────────────────────────
if not check_health():
    st.markdown(
        "<div style='text-align:center;padding:3rem 1rem;'>"
        "<div style='font-size:3rem;'>⚡</div>"
        "<div style='font-size:1.2rem;font-weight:700;color:#f1f5f9;margin:1rem 0 0.5rem;'>Backend is offline</div>"
        "<div style='color:#64748b;font-size:0.9rem;'>Run: <code>uvicorn backend.app:app --reload --port 8000</code></div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.stop()

# ── Data fetch — API calls untouched ─────────────────────────────────────────
try:
    venue_state = fetch_zones()
    rec_data    = fetch_recommendation()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

zones    = venue_state["zones"]
rec_zone = rec_data["recommended_zone"]
alt_zone = rec_data.get("alternative_zone")

rec_color   = STATUS_COLOR[rec_zone["status"]]
rec_wait    = rec_data["estimated_wait_minutes"]
rec_saved   = rec_data["time_saved_vs_worst"]
rec_density = int(rec_zone["density"] * 100)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem;'>"
    "<div>"
    "<span style='font-size:1rem;font-weight:700;color:#f1f5f9;letter-spacing:0.04em;'>🏟️ FlowOps</span>"
    f"<span style='font-size:0.78rem;color:#475569;margin-left:10px;'>{venue_state.get('venue_name','')}</span>"
    "</div>"
    f"<div style='font-size:0.72rem;color:#334155;'>{venue_state.get('event','')}</div>"
    "</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='text-align:center;margin-bottom:1rem;'>"
    "<span style='font-size:0.75rem;color:#475569;'>🎮 Player Status</span><br>"
    "<span style='font-size:1rem;font-weight:600;color:#22c55e;'>You are in stadium · Ready to exit</span>"
    "</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='text-align:center;font-size:0.7rem;color:#22c55e;margin-bottom:1rem;'>"
    "🟢 LIVE — updating in real time"
    "</div>",
    unsafe_allow_html=True
)
# ── HERO — recommended exit ───────────────────────────────────────────────────

# Pill badge
st.markdown(
    "<div style='text-align:center;margin-bottom:0.75rem;'>"
    f"<span style='display:inline-block;background:{rec_color}18;border:1px solid {rec_color}66;"
    f"color:{rec_color};font-size:0.7rem;font-weight:700;letter-spacing:0.12em;"
    f"text-transform:uppercase;padding:4px 14px;border-radius:100px;'>✦ Recommended Exit</span>"
    "</div>",
    unsafe_allow_html=True
)

# Hero card wrapper — open
st.markdown(
    f"<div style='background:linear-gradient(145deg,#0f172a 0%,#111827 100%);"
    f"border:2px solid {rec_color};border-radius:20px;padding:1.75rem 2rem 1.5rem;"
    f"box-shadow:0 0 48px {rec_color}28;margin-bottom:1.25rem;'>",
    unsafe_allow_html=True
)

# Big action text
st.markdown(
    f"<div style='text-align:center;font-size:2.6rem;font-weight:800;color:#f8fafc;"
    f"line-height:1.1;letter-spacing:-0.02em;margin-bottom:0.3rem;'>"
    f"🚀 ESCAPE ROUTE: {rec_zone['label']}"
    f"</div>",
    unsafe_allow_html=True
)


st.markdown(
    f"<div style='text-align:center;font-size:0.95rem;color:#94a3b8;margin-bottom:1rem;'>"
    f"⚡ Move now to avoid congestion · Save ~{rec_saved:.0f} min"
    f"</div>",
    unsafe_allow_html=True
)
# Location
st.markdown(
    f"<div style='text-align:center;font-size:1rem;color:#64748b;margin-bottom:1.4rem;'>"
    f"📍 {rec_zone['location']}"
    f"</div>",
    unsafe_allow_html=True
)

# 3 stat boxes
col_wait, col_saved, col_density = st.columns(3)
with col_wait:
    st.markdown(
        f"<div style='background:#0d1117;border:1px solid #1e293b;border-radius:12px;"
        f"padding:0.9rem 0.5rem;text-align:center;'>"
        f"<div style='font-size:1.6rem;font-weight:800;color:{rec_color};'>{rec_wait:.0f} min</div>"
        f"<div style='font-size:0.66rem;color:#475569;margin-top:3px;line-height:1.4;'>estimated<br>wait time</div>"
        f"</div>",
        unsafe_allow_html=True
    )
with col_saved:
    st.markdown(
        f"<div style='background:#0d1117;border:1px solid #1e293b;border-radius:12px;"
        f"padding:0.9rem 0.5rem;text-align:center;'>"
        f"<div style='font-size:1.6rem;font-weight:800;color:#22c55e;'>🏆 +{rec_saved:.0f} min advantage</div>"
        f"<div style='font-size:0.66rem;color:#475569;margin-top:3px;line-height:1.4;'>faster than<br>worst exit</div>"
        f"</div>",
        unsafe_allow_html=True
    )
with col_density:
    st.markdown(
        f"<div style='background:#0d1117;border:1px solid #1e293b;border-radius:12px;"
        f"padding:0.9rem 0.5rem;text-align:center;'>"
        f"<div style='font-size:1.6rem;font-weight:800;color:#f8fafc;'>{rec_density}%</div>"
        f"<div style='font-size:0.66rem;color:#475569;margin-top:3px;line-height:1.4;'>crowd<br>density</div>"
        f"</div>",
        unsafe_allow_html=True
    )

# Hero card wrapper — close
st.markdown("</div>", unsafe_allow_html=True)

if st.button("🚶 Start Exit Journey"):
    st.success(f"Move towards {rec_zone['label']} — fastest path detected!")
# ── Alternative exit ──────────────────────────────────────────────────────────
if alt_zone:
    alt_color   = STATUS_COLOR[alt_zone["status"]]
    alt_wait    = alt_zone.get("estimated_wait_minutes", 0)
    alt_density = int(alt_zone["density"] * 100)

    st.markdown(
        f"<div style='background:#0f172a;border:1px solid #1e293b;border-radius:14px;"
        f"padding:0.9rem 1.2rem;display:flex;align-items:center;justify-content:space-between;"
        f"margin-bottom:1.5rem;'>"
        f"<div>"
        f"<div style='font-size:0.62rem;color:#475569;text-transform:uppercase;"
        f"letter-spacing:0.1em;margin-bottom:3px;'>If {rec_zone['label']} is crowded when you arrive</div>"
        f"<div style='font-size:1rem;font-weight:700;color:#e2e8f0;'>Try {alt_zone['label']} "
        f"<span style='font-size:0.8rem;font-weight:400;color:#64748b;'>{alt_zone['location']}</span></div>"
        f"</div>"
        f"<div style='text-align:right;min-width:80px;'>"
        f"<div style='font-size:1rem;font-weight:700;color:{alt_color};'>{alt_wait:.0f} min</div>"
        f"<div style='font-size:0.65rem;color:#475569;'>{alt_density}% crowd</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True
    )

# ── Section label: all exits ──────────────────────────────────────────────────
st.markdown(
    "<div style='display:flex;align-items:center;gap:12px;margin:1.5rem 0 1rem;'>"
    "<div style='font-size:0.68rem;font-weight:700;letter-spacing:0.12em;"
    "text-transform:uppercase;color:#334155;white-space:nowrap;'>🏁 Exit Leaderboard</div>"
    "<div style='flex:1;height:1px;background:#1e293b;'></div>"
    "<div style='font-size:0.65rem;color:#334155;'>sorted by wait time</div>"
    "</div>",
    unsafe_allow_html=True
)

# ── Zone list ─────────────────────────────────────────────────────────────────
rec_id       = rec_zone["id"]
sorted_zones = sorted(zones, key=lambda z: z.get("estimated_wait_minutes", 99))

for zone in sorted_zones:
    is_best     = zone["id"] == rec_id
    color       = STATUS_COLOR[zone["status"]]
    density     = int(zone["density"] * 100)
    wait        = zone.get("estimated_wait_minutes", 0)
    bg          = "#0a1628" if is_best else "#0f172a"
    border_col  = color if is_best else "#1e293b"
    border_w    = "2px"  if is_best else "1px"
    name_color  = "#f1f5f9" if is_best else "#94a3b8"
    name_weight = "700" if is_best else "500"
    wait_color  = "#f1f5f9" if is_best else "#64748b"
    best_tag    = (
        f" <span style='font-size:0.62rem;color:{color};font-weight:700;'>← best</span>"
        if is_best else ""
    )

    st.markdown(
        f"<div style='background:{bg};border:{border_w} solid {border_col};"
        f"border-radius:12px;padding:0.8rem 1.1rem;margin-bottom:8px;"
        f"display:flex;align-items:center;gap:12px;'>"

        f"<div style='width:10px;height:10px;border-radius:50%;"
        f"background:{color};flex-shrink:0;box-shadow:0 0 6px {color}88;'></div>"

        f"<div style='flex:1;min-width:0;'>"
        f"<div style='font-size:0.95rem;font-weight:{name_weight};color:{name_color};"
        f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>"
        f"{zone['label']}{best_tag}</div>"
        f"<div style='font-size:0.72rem;color:#475569;margin-top:1px;'>{zone['location']}</div>"
        f"</div>"

        f"<div style='width:80px;'>"
        f"<div style='display:flex;justify-content:space-between;"
        f"font-size:0.62rem;color:#475569;margin-bottom:3px;'>"
        f"<span>crowd</span><span>{density}%</span></div>"
        f"<div style='background:#1e293b;border-radius:3px;height:4px;'>"
        f"<div style='background:{color};width:{density}%;height:4px;border-radius:3px;'></div>"
        f"</div></div>"

        f"<div style='text-align:right;min-width:48px;'>"
        f"<div style='font-size:1rem;font-weight:700;color:{wait_color};'>{wait:.0f}m</div>"
        f"<div style='font-size:0.62rem;color:#334155;'>wait</div>"
        f"</div>"

        f"</div>",
        unsafe_allow_html=True
    )

# ── Detail table (collapsed) ──────────────────────────────────────────────────
st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
with st.expander("📋 View detailed zone data"):
    df = pd.DataFrame([
        {
            "Exit":          z["label"],
            "Location":      z["location"],
            "Status":        STATUS_LABEL[z["status"]],
            "Crowd density": f"{int(z['density']*100)}%",
            "People inside": f"{z['current_crowd']:,}",
            "Flow rate":     f"{z['flow_rate']} / min",
            "Est. wait":     f"{z.get('estimated_wait_minutes',0):.1f} min",
        }
        for z in sorted_zones
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(
        "Flow rate = people exiting per minute (higher = faster). "
        "Crowd density = % of exit capacity currently in use."
    )

# ── Demo controls ─────────────────────────────────────────────────────────────
st.markdown(
    "<div style='margin-top:2.5rem;margin-bottom:0.75rem;'>"
    "<div style='display:flex;align-items:center;gap:12px;margin-bottom:0.4rem;'>"
    "<div style='font-size:0.68rem;font-weight:700;letter-spacing:0.12em;"
    "text-transform:uppercase;color:#334155;white-space:nowrap;'>Demo controls</div>"
    "<div style='flex:1;height:1px;background:#1e293b;'></div>"
    "</div>"
    "<div style='font-size:0.72rem;color:#334155;margin-bottom:0.75rem;'>"
    "Simulate crowd movement to see the system respond in real time."
    "</div>"
    "</div>",
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns([2, 2, 3])
with c1:
    if st.button("🔄 Simulate tick"):
        with st.spinner("⚡ Recalculating escape routes..."):
            time.sleep(1.2)
            post_simulate()
        st.rerun()
with c2:
    if st.button("↺ Reset crowds", help="Restore all exits to starting state"):
        post_reset()
        st.rerun()
with c3:
    auto = st.toggle("⚡ Auto-refresh (5s)", value=False)

with st.expander("⚠️ Inject a crowd surge (demo)"):
    surge_zone_id = st.selectbox(
        "Pick an exit to surge",
        options=[z["id"] for z in zones],
        format_func=lambda zid: next(z["label"] for z in zones if z["id"] == zid),
    )
    surge_mag = st.slider(
        "Surge size", min_value=0.1, max_value=0.6, value=0.25, step=0.05,
        help="How much crowd density to inject"
    )
    if st.button("🚨 Trigger surge"):
        post_simulate(surge_zone=surge_zone_id, surge_magnitude=surge_mag)
        st.rerun()

st.markdown(
    "<div style='margin-top:3rem;text-align:center;color:#1e293b;font-size:0.7rem;'>"
    "FlowOps v1.0.0 · Real-Time Crowd Flow Optimization</div>",
    unsafe_allow_html=True
)

# ── Auto-refresh — API call untouched ─────────────────────────────────────────
if auto:
    with st.spinner("Updating crowd movement..."):
        time.sleep(5)
        post_simulate()
    st.rerun()
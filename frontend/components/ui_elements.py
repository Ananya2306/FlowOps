"""
ui_elements.py
Reusable Streamlit UI components for FlowOps dashboard.
Keeps the main app.py clean and focused on layout logic.
"""

import streamlit as st


STATUS_COLOR = {
    "LOW":      "#22c55e",
    "MEDIUM":   "#eab308",
    "HIGH":     "#f97316",
    "CRITICAL": "#ef4444",
}

STATUS_ICON = {
    "LOW":      "🟢",
    "MEDIUM":   "🟡",
    "HIGH":     "🟠",
    "CRITICAL": "🔴",
}

STATUS_LABEL = {
    "LOW":      "Clear",
    "MEDIUM":   "Moderate",
    "HIGH":     "Busy",
    "CRITICAL": "Congested",
}


def zone_card(zone: dict, highlight: bool = False) -> None:
    """Render a single exit zone card."""
    status     = zone.get("status", "LOW")
    color      = STATUS_COLOR[status]
    icon       = STATUS_ICON[status]
    label      = STATUS_LABEL[status]
    density_pct = int(zone["density"] * 100)
    wait        = zone.get("estimated_wait_minutes", 0)

    border = f"3px solid {color}" if highlight else f"1px solid #334155"
    bg     = "#1e293b" if not highlight else "#0f172a"

    st.markdown(f"""
    <div style="
        background:{bg};
        border:{border};
        border-radius:12px;
        padding:16px 20px;
        margin-bottom:8px;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <span style="font-size:1.1rem;font-weight:700;color:#f1f5f9;">
                    {icon} {zone['label']}
                </span>
                <span style="font-size:0.75rem;color:#94a3b8;margin-left:8px;">
                    {zone['location']}
                </span>
            </div>
            <span style="
                background:{color}22;
                color:{color};
                border:1px solid {color};
                border-radius:6px;
                padding:2px 10px;
                font-size:0.75rem;
                font-weight:600;
            ">{label}</span>
        </div>
        <div style="margin-top:10px;">
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">
                <span>Crowd density</span>
                <span>{density_pct}%</span>
            </div>
            <div style="background:#334155;border-radius:4px;height:6px;">
                <div style="background:{color};width:{density_pct}%;height:6px;border-radius:4px;transition:width 0.5s;"></div>
            </div>
        </div>
        <div style="display:flex;gap:24px;margin-top:10px;font-size:0.8rem;color:#94a3b8;">
            <span>⏱ Wait: <strong style="color:#f1f5f9;">{wait:.0f} min</strong></span>
            <span>🚶 Flow: <strong style="color:#f1f5f9;">{zone['flow_rate']}/min</strong></span>
            <span>👥 Crowd: <strong style="color:#f1f5f9;">{zone['current_crowd']:,}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def recommendation_banner(rec: dict) -> None:
    """Large hero card showing the recommended exit."""
    zone    = rec["recommended_zone"]
    status  = zone["status"]
    color   = STATUS_COLOR[status]
    wait    = rec["estimated_wait_minutes"]
    saved   = rec["time_saved_vs_worst"]
    conf    = int(rec["confidence"] * 100)

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2px solid {color};
        border-radius:16px;
        padding:24px 28px;
        margin-bottom:20px;
        box-shadow: 0 0 40px {color}33;
    ">
        <div style="font-size:0.75rem;font-weight:700;letter-spacing:0.15em;color:{color};text-transform:uppercase;">
            ✦ Recommended Exit
        </div>
        <div style="font-size:2rem;font-weight:800;color:#f1f5f9;margin:6px 0;">
            {zone['label']} — {zone['location']}
        </div>
        <div style="font-size:1rem;color:#cbd5e1;margin-bottom:16px;">
            {rec['message']}
        </div>
        <div style="display:flex;gap:32px;flex-wrap:wrap;">
            <div>
                <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;">Est. Wait</div>
                <div style="font-size:1.5rem;font-weight:700;color:{color};">{wait:.0f} min</div>
            </div>
            <div>
                <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;">Time Saved</div>
                <div style="font-size:1.5rem;font-weight:700;color:#22c55e;">↓ {saved:.0f} min</div>
            </div>
            <div>
                <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;">Confidence</div>
                <div style="font-size:1.5rem;font-weight:700;color:#f1f5f9;">{conf}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def metric_row(total_crowd: int, best_wait: float, zones_critical: int) -> None:
    """Top-level KPI row."""
    cols = st.columns(3)
    metrics = [
        ("👥 Total Crowd",       f"{total_crowd:,}",        "people in venue"),
        ("⏱ Best Wait",          f"{best_wait:.0f} min",    "at recommended exit"),
        ("🔴 Critical Zones",    str(zones_critical),        "exits over 80% density"),
    ]
    for col, (label, value, sub) in zip(cols, metrics):
        with col:
            st.metric(label=label, value=value, delta=sub, delta_color="off")


def sidebar_controls() -> dict:
    """Render sidebar controls and return user choices."""
    st.sidebar.title("⚙️ Simulation Controls")
    st.sidebar.markdown("---")

    auto_refresh = st.sidebar.toggle("🔄 Auto-refresh (5s)", value=False)
    st.sidebar.markdown("### Manual Tick")
    ticks = st.sidebar.slider("Ticks to advance", 1, 10, 1)

    st.sidebar.markdown("### Surge Event")
    surge_on   = st.sidebar.checkbox("Inject crowd surge")
    surge_zone = None
    surge_mag  = 0.2
    if surge_on:
        surge_zone = st.sidebar.selectbox(
            "Surge zone", ["EXIT_A", "EXIT_B", "EXIT_C", "EXIT_D", "EXIT_E"]
        )
        surge_mag = st.sidebar.slider("Magnitude", 0.1, 0.6, 0.2, 0.05)

    return {
        "auto_refresh": auto_refresh,
        "ticks": ticks,
        "surge_on": surge_on,
        "surge_zone": surge_zone,
        "surge_mag": surge_mag,
    }

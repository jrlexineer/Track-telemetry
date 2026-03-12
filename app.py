import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import time

# ── PAGE CONFIG ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Track Telemetry | Josh AI Solutions",
    page_icon="🏎️",
    layout="wide"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Barlow', sans-serif;
        background-color: #0a0a0a;
        color: #f0f0f0;
    }
    .stApp { background-color: #0a0a0a; }

    h1, h2, h3 { font-family: 'Barlow', sans-serif; font-weight: 900; }

    .hero {
        text-align: center;
        padding: 2rem 0 1rem 0;
        border-bottom: 1px solid #222;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-size: 3rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #ffffff;
        margin: 0;
    }
    .hero p {
        color: #888;
        font-size: 0.95rem;
        letter-spacing: 0.08em;
        margin-top: 0.5rem;
        font-family: 'Share Tech Mono', monospace;
    }
    .hero .brand {
        font-size: 0.75rem;
        color: #e74c3c;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        font-family: 'Share Tech Mono', monospace;
    }

    .stat-card {
        background: #111;
        border: 1px solid #222;
        border-left: 3px solid;
        padding: 1rem 1.2rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
    }
    .stat-label {
        font-size: 0.7rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #666;
        font-family: 'Share Tech Mono', monospace;
    }
    .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    .stat-sub {
        font-size: 0.75rem;
        color: #555;
        font-family: 'Share Tech Mono', monospace;
    }

    .event-log {
        background: #0d0d0d;
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
        min-height: 80px;
        color: #aaa;
    }

    .footer {
        text-align: center;
        padding: 2rem 0;
        border-top: 1px solid #1a1a1a;
        margin-top: 3rem;
        color: #444;
        font-size: 0.8rem;
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 0.1em;
    }
    .footer a { color: #e74c3c; text-decoration: none; }

    div[data-testid="stSidebar"] {
        background-color: #0d0d0d;
        border-right: 1px solid #1a1a1a;
    }
    .stButton > button {
        background: #e74c3c;
        color: white;
        border: none;
        font-family: 'Barlow', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.6rem 2rem;
        border-radius: 2px;
        width: 100%;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #c0392b; }
    .stSlider > div > div { color: #f0f0f0; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="brand">Josh AI Solutions</div>
    <h1>🏎️ Track Telemetry</h1>
    <p>Live race simulation · Tire degradation modeling · Strategy analytics</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Race Config")

    total_laps = st.slider("Total Laps", 10, 30, 20)
    lap_delay  = st.slider("Sim Speed (sec/lap)", 0.1, 1.5, 0.4, step=0.1)

    st.markdown("---")
    st.markdown("### 🚗 Cars")

    cars_available = {
        "Miata NA":    {"base_lap": 125.0, "deg_per_lap": 0.008, "pit_threshold": 2.5, "pit_time": 28},
        "E46 330i":    {"base_lap": 113.0, "deg_per_lap": 0.018, "pit_threshold": 2.0, "pit_time": 26},
        "C6 Corvette": {"base_lap": 106.0, "deg_per_lap": 0.028, "pit_threshold": 1.5, "pit_time": 25},
        "GT3":         {"base_lap": 100.0, "deg_per_lap": 0.012, "pit_threshold": 2.2, "pit_time": 24},
    }
    selected = {}
    for car, cfg in cars_available.items():
        if st.checkbox(car, value=True):
            selected[car] = cfg

    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("""
    <div style="font-size:0.8rem; color:#666; line-height:1.6;">
    Tire degradation curves mirror demand decay in retail.
    The pit window = the markdown timing decision.
    Same framework. Different domain.
    </div>
    """, unsafe_allow_html=True)

COLORS = {
    "Miata NA":    "#3498DB",
    "E46 330i":    "#E67E22",
    "C6 Corvette": "#E74C3C",
    "GT3":         "#2ECC71"
}

# ── RUN BUTTON ────────────────────────────────────────────────────
col_btn, col_space = st.columns([1, 3])
with col_btn:
    run = st.button("▶  START RACE")

if not selected:
    st.warning("Select at least one car.")
    st.stop()

# ── LAYOUT ────────────────────────────────────────────────────────
col_chart, col_right = st.columns([3, 1])

with col_chart:
    chart_placeholder = st.empty()

with col_right:
    st.markdown("#### Live Standings")
    standings_placeholder = st.empty()
    st.markdown("#### Race Events")
    events_placeholder = st.empty()

# ── RACE SIM ──────────────────────────────────────────────────────
if run:
    CARS = selected
    history  = {car: {"lap": [], "lap_time": [], "cumulative": []} for car in CARS}
    tire_age = {car: 0 for car in CARS}
    pitted   = {car: False for car in CARS}
    pit_laps = {car: None for car in CARS}
    cum_time = {car: 0.0 for car in CARS}
    all_events = []

    for lap in range(1, total_laps + 1):
        lap_events = []

        for car, cfg in CARS.items():
            age = tire_age[car]
            deg_factor = 1 + (cfg["deg_per_lap"] * age)
            lap_time = cfg["base_lap"] * deg_factor + np.random.uniform(-2.0, 2.0)

            if not pitted[car] and (deg_factor - 1) * 100 >= cfg["pit_threshold"]:
                lap_time += cfg["pit_time"]
                tire_age[car] = 0
                pitted[car] = True
                pit_laps[car] = lap
                lap_events.append(f"Lap {lap:02d} — 🔧 {car} PITS")
            else:
                tire_age[car] += 1

            cum_time[car] += lap_time
            history[car]["lap"].append(lap)
            history[car]["lap_time"].append(lap_time)
            history[car]["cumulative"].append(cum_time[car])

        all_events = lap_events + all_events

        # ── LIVE CHART ────────────────────────────────────────────
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor("#0f0f0f")

        for ax in axes:
            ax.set_facecolor("#141414")
            ax.tick_params(colors="#aaa", labelsize=8)
            ax.xaxis.label.set_color("#aaa")
            ax.yaxis.label.set_color("#aaa")
            ax.title.set_color("white")
            for spine in ax.spines.values():
                spine.set_edgecolor("#2a2a2a")

        # Left: lap times
        for car in CARS:
            axes[0].plot(history[car]["lap"], history[car]["lap_time"],
                        "o-", label=car, color=COLORS[car], linewidth=2, markersize=3)
            if pit_laps[car]:
                axes[0].axvline(pit_laps[car], color=COLORS[car], linestyle="--", alpha=0.25)

        axes[0].set_title(f"Lap Times  —  Lap {lap}/{total_laps}", fontsize=10)
        axes[0].set_xlabel("Lap", fontsize=8)
        axes[0].set_ylabel("Lap Time (sec)", fontsize=8)
        axes[0].set_xlim(1, total_laps)
        axes[0].legend(fontsize=7, facecolor="#1a1a1a", labelcolor="white", framealpha=0.9)
        axes[0].grid(True, alpha=0.1, color="white")
        axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x//60)}:{x%60:04.1f}"))

        # Right: gap to leader
        if len(history[list(CARS.keys())[0]]["cumulative"]) > 0:
            current_standings = sorted(CARS.keys(), key=lambda c: cum_time[c])
            leader_cum = history[current_standings[0]]["cumulative"]
            for car in CARS:
                gaps = [history[car]["cumulative"][i] - leader_cum[i]
                        for i in range(len(history[car]["cumulative"]))]
                axes[1].plot(history[car]["lap"], gaps, "o-", label=car,
                            color=COLORS[car], linewidth=2, markersize=3)

        axes[1].axhline(0, color="white", linewidth=0.6, alpha=0.2)
        axes[1].set_title("Gap to Leader", fontsize=10)
        axes[1].set_xlabel("Lap", fontsize=8)
        axes[1].set_ylabel("Seconds Behind", fontsize=8)
        axes[1].set_xlim(1, total_laps)
        axes[1].legend(fontsize=7, facecolor="#1a1a1a", labelcolor="white", framealpha=0.9)
        axes[1].grid(True, alpha=0.1, color="white")

        plt.tight_layout(pad=1.5)
        chart_placeholder.pyplot(fig)
        plt.close()

        # ── LIVE STANDINGS ────────────────────────────────────────
        current_standings = sorted(CARS.keys(), key=lambda c: cum_time[c])
        leader_t = cum_time[current_standings[0]]
        standings_md = ""
        medals = ["🥇", "🥈", "🥉", "4️⃣"]
        for i, car in enumerate(current_standings):
            gap = cum_time[car] - leader_t
            gap_str = "LEADER" if gap == 0 else f"+{gap:.1f}s"
            color = COLORS[car]
            standings_md += f"""
            <div style="padding:0.5rem 0; border-bottom:1px solid #1a1a1a;">
                <span style="font-size:1rem;">{medals[i]}</span>
                <span style="color:{color}; font-weight:700; margin-left:0.5rem;">{car}</span>
                <span style="float:right; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#888;">{gap_str}</span>
            </div>"""
        standings_placeholder.markdown(standings_md, unsafe_allow_html=True)

        # ── EVENTS LOG ────────────────────────────────────────────
        events_html = "<div class='event-log'>"
        for e in all_events[:6]:
            events_html += f"<div style='margin-bottom:0.3rem;'>{e}</div>"
        if not all_events:
            events_html += "<div style='color:#333;'>No events yet...</div>"
        events_html += "</div>"
        events_placeholder.markdown(events_html, unsafe_allow_html=True)

        time.sleep(lap_delay)

    # ── FINAL RESULTS ─────────────────────────────────────────────
    final = sorted(CARS.keys(), key=lambda c: cum_time[c])
    leader_time = cum_time[final[0]]

    st.markdown("---")
    st.markdown("## 🏁 Final Result")

    cols = st.columns(len(final))
    medals_full = ["🥇 WINNER", "🥈 P2", "🥉 P3", "4th P4"]
    for i, (col, car) in enumerate(zip(cols, final)):
        total = cum_time[car]
        gap = total - leader_time
        best = min(history[car]["lap_time"])
        pit = f"Lap {pit_laps[car]}" if pit_laps[car] else "No stop"
        gap_str = "—" if gap == 0 else f"+{gap:.1f}s"
        color = COLORS[car]
        col.markdown(f"""
        <div class="stat-card" style="border-left-color:{color};">
            <div class="stat-label">{medals_full[i]}</div>
            <div class="stat-value" style="color:{color};">{car}</div>
            <div class="stat-sub">Gap: {gap_str}</div>
            <div class="stat-sub">Best: {int(best//60)}:{best%60:05.2f}</div>
            <div class="stat-sub">Pit: {pit}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── FINAL 4-PANEL CHART ───────────────────────────────────────
    st.markdown("### 📊 Full Race Analysis")
    fig2 = plt.figure(figsize=(14, 9))
    fig2.patch.set_facecolor("#0f0f0f")

    ax1 = fig2.add_subplot(2, 2, 1)
    ax2 = fig2.add_subplot(2, 2, 2)
    ax3 = fig2.add_subplot(2, 2, 3)
    ax4 = fig2.add_subplot(2, 2, 4)

    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_facecolor("#141414")
        ax.tick_params(colors="#aaa", labelsize=8)
        ax.xaxis.label.set_color("#aaa")
        ax.yaxis.label.set_color("#aaa")
        ax.title.set_color("white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a2a")

    for car in CARS:
        ax1.plot(history[car]["lap"], history[car]["lap_time"],
                "o-", label=car, color=COLORS[car], linewidth=2, markersize=3)
        if pit_laps[car]:
            ax1.axvline(pit_laps[car], color=COLORS[car], linestyle="--", alpha=0.25)
    ax1.set_title("Lap Times — Full Race", fontsize=10)
    ax1.set_xlabel("Lap", fontsize=8)
    ax1.set_ylabel("Lap Time (sec)", fontsize=8)
    ax1.legend(fontsize=7, facecolor="#1a1a1a", labelcolor="white", framealpha=0.9)
    ax1.grid(True, alpha=0.1, color="white")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x//60)}:{x%60:04.1f}"))

    leader_cumulative = history[final[0]]["cumulative"]
    for car in CARS:
        gaps = [history[car]["cumulative"][i] - leader_cumulative[i] for i in range(total_laps)]
        ax2.plot(range(1, total_laps+1), gaps, "o-", label=car,
                color=COLORS[car], linewidth=2, markersize=3)
        if pit_laps[car]:
            pit_idx = pit_laps[car] - 1
            ax2.annotate("PIT", xy=(pit_laps[car], gaps[pit_idx]),
                        color=COLORS[car], fontsize=6, ha="center",
                        xytext=(0, 8), textcoords="offset points")
    ax2.axhline(0, color="white", linewidth=0.6, alpha=0.2)
    ax2.set_title("Gap to Leader", fontsize=10)
    ax2.set_xlabel("Lap", fontsize=8)
    ax2.set_ylabel("Seconds Behind", fontsize=8)
    ax2.legend(fontsize=7, facecolor="#1a1a1a", labelcolor="white", framealpha=0.9)
    ax2.grid(True, alpha=0.1, color="white")

    best_laps = {car: min(history[car]["lap_time"]) for car in CARS}
    sorted_cars = sorted(best_laps, key=best_laps.get)
    bars = ax3.barh(sorted_cars, [best_laps[c] for c in sorted_cars],
                    color=[COLORS[c] for c in sorted_cars], alpha=0.85, height=0.5)
    for bar, car in zip(bars, sorted_cars):
        t = best_laps[car]
        ax3.text(bar.get_width() - 0.5, bar.get_y() + bar.get_height()/2,
                f"{int(t//60)}:{t%60:05.2f}", va="center", ha="right",
                color="white", fontsize=8, fontweight="bold")
    ax3.set_title("Best Lap by Car", fontsize=10)
    ax3.set_xlabel("Lap Time (sec)", fontsize=8)
    ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x//60)}:{x%60:04.1f}"))
    ax3.grid(True, alpha=0.1, color="white", axis="x")

    ax4.axis("off")
    ax4.set_title("Final Standings", fontsize=10)
    ax4.title.set_color("white")
    table_data = []
    medals_t = ["1st", "2nd", "3rd", "4th"]
    for i, car in enumerate(final):
        total = cum_time[car]
        gap = total - leader_time
        pit = f"Lap {pit_laps[car]}" if pit_laps[car] else "No stop"
        best = min(history[car]["lap_time"])
        table_data.append([medals_t[i], car, "WINNER" if gap==0 else f"+{gap:.1f}s",
                           f"{int(best//60)}:{best%60:05.2f}", pit])
    table = ax4.table(cellText=table_data,
                      colLabels=["", "Car", "Gap", "Best Lap", "Pit"],
                      cellLoc="center", loc="center", bbox=[0, 0.05, 1, 0.9])
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor("#141414" if row > 0 else "#222")
        cell.set_text_props(color="white")
        cell.set_edgecolor("#2a2a2a")
        if row > 0:
            car_name = table_data[row-1][1]
            if col == 1:
                cell.set_text_props(color=COLORS.get(car_name, "white"), fontweight="bold")
            if col == 2 and table_data[row-1][2] == "WINNER":
                cell.set_text_props(color="#FFD700", fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    st.pyplot(fig2)
    plt.close()

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Josh AI Solutions · Analytical Systems & Automation ·
    <a href="https://miyamotoai.carrd.co" target="_blank">miyamotoai.carrd.co</a>
    <br><br>
    From the track to the boardroom — the same data thinking, different domain.
</div>
""", unsafe_allow_html=True)

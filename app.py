import streamlit as st
import pandas as pd
import joblib
import time

# -------------------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------------------
st.set_page_config(page_title="Valuation Engine", page_icon="🛠️", layout="centered")

# -------------------------------------------------------------
# 2. SESSION STATE — controls landing vs. tool view
# -------------------------------------------------------------
if "show_tool" not in st.session_state:
    st.session_state.show_tool = False

def open_tool():
    st.session_state.show_tool = True

def close_tool():
    st.session_state.show_tool = False

# -------------------------------------------------------------
# 3. DESIGN SYSTEM — "INSTRUMENT PANEL"
# Dyno readout / blueprint vernacular. Mono type for data,
# grotesk for prose. Signal-orange accent. Fully responsive.
# -------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #0a0c10;
            --panel: #12151c;
            --panel-2: #181c25;
            --line: #2a2f3a;
            --line-soft: rgba(255,255,255,0.06);
            --paper: #e8e3d9;
            --muted: #7c8597;
            --signal: #ff6b35;
            --signal-dim: rgba(255, 107, 53, 0.18);
            --good: #5fd4a0;
        }

        html, body, .stApp { background: var(--bg); color: var(--paper); font-family: 'Inter', sans-serif; }
        #MainMenu, footer, header { visibility: hidden; }
        .stAlert { display: none; }

        .main .block-container { padding-top: 0rem; padding-bottom: 3rem; max-width: 880px; }

        .stApp::before {
            content: "";
            position: fixed; inset: 0;
            background-image:
                linear-gradient(var(--line-soft) 1px, transparent 1px),
                linear-gradient(90deg, var(--line-soft) 1px, transparent 1px);
            background-size: 28px 28px;
            pointer-events: none; z-index: 0;
        }

        /* ===== HERO ===== */
        .hero-wrap {
            margin: 0 -1rem;
            padding: 3.6rem 1.6rem 3rem;
            border-bottom: 1px solid var(--line);
            position: relative;
            text-align: center;
        }
        .hero-eyebrow {
            display: inline-flex; align-items: center; gap: 0.5rem;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase;
            color: var(--signal);
            border: 1px solid rgba(255,107,53,0.35);
            background: var(--signal-dim);
            padding: 0.3rem 0.7rem; border-radius: 20px;
            margin-bottom: 1.6rem;
        }
        .hero-eyebrow::before {
            content: ""; width: 6px; height: 6px; border-radius: 50%;
            background: var(--signal); box-shadow: 0 0 8px var(--signal);
        }
        .hero-title {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: clamp(2rem, 6.5vw, 3.4rem);
            line-height: 1.08;
            letter-spacing: -0.5px;
            color: var(--paper);
            margin: 0 0 1.1rem;
        }
        .hero-title .accent { color: var(--signal); }
        .hero-sub {
            font-size: clamp(0.95rem, 2vw, 1.1rem);
            color: var(--muted);
            max-width: 540px;
            margin: 0 auto 2rem;
            line-height: 1.6;
        }

        /* ===== STAT STRIP ===== */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.8rem;
            margin: 0 -1rem 0;
            padding: 0 1rem;
        }
        .stat-plate {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 4px;
            padding: 1rem 0.8rem;
            text-align: center;
        }
        .stat-num {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: clamp(1.3rem, 3.5vw, 1.7rem);
            color: var(--paper);
        }
        .stat-label {
            font-size: 0.68rem;
            color: var(--muted);
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-top: 0.3rem;
            font-family: 'IBM Plex Mono', monospace;
        }

        /* ===== HOW IT WORKS ===== */
        .section-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            color: var(--signal);
            text-align: center;
            margin: 3.2rem 0 0.6rem;
        }
        .section-title {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: clamp(1.3rem, 3.5vw, 1.7rem);
            color: var(--paper);
            text-align: center;
            margin-bottom: 2rem;
        }
        .flow-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0;
            position: relative;
        }
        .flow-step {
            text-align: center;
            padding: 0 0.6rem;
            position: relative;
        }
        .flow-num {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: 0.78rem;
            color: var(--bg);
            background: var(--paper);
            display: inline-flex;
            width: 26px; height: 26px;
            align-items: center; justify-content: center;
            border-radius: 50%;
            margin-bottom: 0.9rem;
        }
        .flow-title {
            font-weight: 700;
            font-size: 0.95rem;
            color: var(--paper);
            margin-bottom: 0.4rem;
        }
        .flow-desc {
            font-size: 0.8rem;
            color: var(--muted);
            line-height: 1.5;
        }
        .flow-arrow {
            position: absolute;
            top: 13px; right: -8px;
            color: var(--line);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1rem;
        }

        /* ===== FEATURE LIST (what it reads) ===== */
        .feature-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.6rem;
            margin-top: 1.4rem;
        }
        .feature-chip {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 4px;
            padding: 0.7rem 0.9rem;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            color: var(--muted);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .feature-chip::before {
            content: "▸"; color: var(--signal); flex-shrink: 0;
        }

        /* ===== CTA BLOCK ===== */
        .cta-block {
            text-align: center;
            margin: 3.4rem 0 1rem;
            padding: 2.2rem 1.4rem;
            border: 1px dashed var(--line);
            border-radius: 6px;
            background: var(--panel);
        }
        .cta-title {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: clamp(1.15rem, 3vw, 1.5rem);
            color: var(--paper);
            margin-bottom: 0.5rem;
        }
        .cta-sub {
            font-size: 0.85rem;
            color: var(--muted);
            margin-bottom: 1.4rem;
        }

        /* ===== BUTTONS (Streamlit) ===== */
        .stButton button {
            width: 100%;
            background: var(--signal) !important;
            color: #1a0a02 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            letter-spacing: 1.5px;
            padding: 0.85rem 0 !important;
            border: none !important;
            border-radius: 3px !important;
            text-transform: uppercase;
            transition: filter 0.15s ease, transform 0.1s ease;
        }
        .stButton button:hover { filter: brightness(1.12); }
        .stButton button:active { transform: scale(0.99); }
        .stButton button:focus-visible { outline: 2px solid var(--paper); outline-offset: 2px; }

        /* secondary/ghost button variant via key targeting */
        button[kind="secondary"] {
            background: transparent !important;
            color: var(--muted) !important;
            border: 1px solid var(--line) !important;
        }
        button[kind="secondary"]:hover {
            color: var(--paper) !important;
            border-color: var(--muted) !important;
            filter: none !important;
        }

        /* ===== TOOL VIEW — SPEC PLATE + PANELS ===== */
        .plate {
            border: 1px solid var(--line); border-radius: 4px; background: var(--panel);
            padding: 1.4rem 1.6rem; margin-bottom: 1.4rem; position: relative;
        }
        .plate::before {
            content: ""; position: absolute; top: 10px; left: 10px;
            width: 6px; height: 6px; border-radius: 50%;
            background: var(--signal); box-shadow: 0 0 8px var(--signal);
        }
        .plate-row { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0.4rem; }
        .plate-title { font-family: 'IBM Plex Mono', monospace; font-weight: 700; font-size: 1.6rem; letter-spacing: 0.5px; color: var(--paper); margin: 0; }
        .plate-tag {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: var(--signal);
            letter-spacing: 1.5px; text-transform: uppercase;
            border: 1px solid rgba(255,107,53,0.35); background: var(--signal-dim);
            padding: 0.25rem 0.55rem; border-radius: 3px; white-space: nowrap;
        }
        .plate-sub { font-size: 0.82rem; color: var(--muted); margin-top: 0.35rem; }

        .panel { border: 1px solid var(--line); border-radius: 4px; background: var(--panel); padding: 1.3rem 1.4rem 0.6rem; margin-bottom: 1rem; }
        .panel-head { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem; padding-bottom: 0.7rem; border-bottom: 1px dashed var(--line); }
        .panel-index { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: var(--bg); background: var(--paper); border-radius: 3px; padding: 0.1rem 0.45rem; font-weight: 700; }
        .panel-name { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; letter-spacing: 1.8px; text-transform: uppercase; color: var(--paper); font-weight: 600; }
        .panel-hint { margin-left: auto; font-size: 0.7rem; color: var(--muted); font-family: 'IBM Plex Mono', monospace; }

        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stNumberInput input {
            background: var(--panel-2) !important; border: 1px solid var(--line) !important;
            border-radius: 3px !important; color: var(--paper) !important;
            font-family: 'IBM Plex Mono', monospace !important;
        }
        div[data-baseweb="select"]:focus-within > div, div[data-baseweb="input"]:focus-within > div {
            border-color: var(--signal) !important; box-shadow: 0 0 0 2px var(--signal-dim) !important;
        }
        .stSelectbox label, .stNumberInput label, .stSlider label {
            color: var(--muted) !important; font-weight: 500 !important; font-size: 0.7rem !important;
            letter-spacing: 0.8px; text-transform: uppercase; font-family: 'IBM Plex Mono', monospace !important;
        }
        .stSlider [data-baseweb="slider"] > div > div { background: var(--line) !important; }
        .stSlider [role="slider"] { background: var(--signal) !important; box-shadow: 0 0 0 4px var(--signal-dim) !important; }
        .stSlider [data-testid="stTickBar"] { display: none; }

        .readout {
            border: 1px solid var(--signal); border-radius: 4px;
            background: linear-gradient(180deg, rgba(255,107,53,0.08), rgba(255,107,53,0.02));
            padding: 1.6rem 1.4rem; margin-top: 1.2rem; text-align: center;
            animation: rise 0.45s ease forwards;
        }
        @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .readout-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 2.5px; text-transform: uppercase; color: var(--signal); margin-bottom: 0.6rem; }
        .readout-value { font-family: 'IBM Plex Mono', monospace; font-size: clamp(2.2rem, 9vw, 3.4rem); font-weight: 700; color: var(--paper); letter-spacing: 1px; line-height: 1; }
        .readout-foot { margin-top: 0.7rem; font-size: 0.72rem; color: var(--muted); font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.5px; }

        .gauge { margin: 1.2rem auto 0; max-width: 420px; }
        .gauge-track { height: 6px; border-radius: 3px; background: var(--line); position: relative; overflow: hidden; }
        .gauge-fill { position: absolute; top: 0; left: 0; bottom: 0; background: linear-gradient(90deg, var(--good), var(--signal)); border-radius: 3px; }
        .gauge-scale { display: flex; justify-content: space-between; font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: var(--muted); margin-top: 0.4rem; }

        .strip { text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: var(--line); margin-top: 1.6rem; letter-spacing: 1.5px; text-transform: uppercase; }

        /* ===== MOBILE ===== */
        @media (max-width: 640px) {
            .main .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
            .hero-wrap { padding: 2.4rem 1rem 2.2rem; }
            .stats-row { grid-template-columns: 1fr; gap: 0.6rem; }
            .flow-row { grid-template-columns: 1fr; gap: 1.6rem; }
            .flow-arrow { display: none; }
            .feature-grid { grid-template-columns: 1fr; }
            .plate { padding: 1.1rem 1.1rem; }
            .plate-title { font-size: 1.25rem; }
            .plate-row { flex-direction: column; align-items: flex-start; }
            .panel { padding: 1.05rem 1.05rem 0.4rem; }
            .readout-value { font-size: 2.1rem; }
            .cta-block { padding: 1.6rem 1rem; }
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. CACHED MODEL LOADING (unchanged)
# -------------------------------------------------------------
@st.cache_resource
def load_assets():
    model = joblib.load('car_rf_model.pkl')
    scaler = joblib.load('car_scaler.pkl')
    model_columns = joblib.load('model_columns.pkl')
    return model, scaler, model_columns

try:
    model, scaler, model_columns = load_assets()
except Exception as e:
    st.error(f"Error loading ML artifacts. Make sure the .pkl files are in this folder. Details: {e}")
    st.stop()

# =================================================================
# 5. LANDING VIEW
# =================================================================
if not st.session_state.show_tool:

    st.markdown("""
        <div class="hero-wrap">
            <div class="hero-eyebrow">Random Forest · Live Inference</div>
            <div class="hero-title">Read the build sheet.<br>Get the <span class="accent">real value.</span></div>
            <div class="hero-sub">
                Enter twelve specs — drivetrain, dimensions, performance, efficiency —
                and the engine returns a market valuation in under a second.
                No guesswork, no dealer markup, just the numbers.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="stats-row">
            <div class="stat-plate"><div class="stat-num">12</div><div class="stat-label">Features Modeled</div></div>
            <div class="stat-plate"><div class="stat-num">&lt;1s</div><div class="stat-label">Inference Time</div></div>
            <div class="stat-plate"><div class="stat-num">RF</div><div class="stat-label">Ensemble Model</div></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="section-label">Process</div>
        <div class="section-title">How the engine reads a car</div>
        <div class="flow-row">
            <div class="flow-step">
                <div class="flow-num">01</div>
                <div class="flow-title">Enter the specs</div>
                <div class="flow-desc">Drivetrain, dimensions, engine, and efficiency — the same fields on any spec sheet.</div>
                <div class="flow-arrow">→</div>
            </div>
            <div class="flow-step">
                <div class="flow-num">02</div>
                <div class="flow-title">Engine runs inference</div>
                <div class="flow-desc">A trained Random Forest ensemble weighs every feature against real market data.</div>
                <div class="flow-arrow">→</div>
            </div>
            <div class="flow-step">
                <div class="flow-num">03</div>
                <div class="flow-title">Get your value</div>
                <div class="flow-desc">A single estimated price, shown against a market range for context.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="section-label">Build Sheet</div>
        <div class="section-title">What the engine reads</div>
        <div class="feature-grid">
            <div class="feature-chip">Drive wheel system</div>
            <div class="feature-chip">Engine placement</div>
            <div class="feature-chip">Fuel delivery system</div>
            <div class="feature-chip">Wheelbase &amp; body length</div>
            <div class="feature-chip">Curb weight</div>
            <div class="feature-chip">Engine size &amp; bore ratio</div>
            <div class="feature-chip">Horsepower</div>
            <div class="feature-chip">City &amp; highway mpg</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="cta-block">
            <div class="cta-title">Ready to value a car?</div>
            <div class="cta-sub">Takes about a minute. No account, no signup.</div>
        </div>
    """, unsafe_allow_html=True)

    st.button("Run a Valuation →", on_click=open_tool, use_container_width=True)

    st.markdown('<div class="strip">Valuation Engine · Predictive Analytics</div>', unsafe_allow_html=True)

# =================================================================
# 6. TOOL VIEW
# =================================================================
else:
    back_col, _ = st.columns([1, 3])
    with back_col:
        st.button("← Back", on_click=close_tool, type="secondary", use_container_width=True)

    st.markdown("""
        <div class="plate">
            <div class="plate-row">
                <div class="plate-title">VALUATION ENGINE</div>
                <div class="plate-tag">Model: Random Forest</div>
            </div>
            <div class="plate-sub">Fill in the build sheet below — the engine reads each spec and returns an estimated market value.</div>
        </div>
    """, unsafe_allow_html=True)

    # ---- Panel 01: Configuration ----
    st.markdown("""
        <div class="panel">
            <div class="panel-head">
                <span class="panel-index">01</span>
                <span class="panel-name">Configuration</span>
                <span class="panel-hint">drivetrain · layout · fuel</span>
            </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        drivewheel = st.selectbox("Drive Wheel", ["fwd", "rwd", "4wd"])
    with c2:
        enginelocation = st.selectbox("Engine Placement", ["front", "rear"])
    with c3:
        fuelsystem = st.selectbox("Fuel System", ["mpfi", "2bbl", "idi", "1bbl", "spdi", "4bbl", "mfi", "spfi"])

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Panel 02: Dimensions ----
    st.markdown("""
        <div class="panel">
            <div class="panel-head">
                <span class="panel-index">02</span>
                <span class="panel-name">Dimensions</span>
                <span class="panel-hint">inches</span>
            </div>
    """, unsafe_allow_html=True)

    wheelbase = st.slider("Wheelbase (in)", min_value=50.0, max_value=150.0, value=94.5, step=0.1)
    carlength = st.slider("Car Length (in)", min_value=100.0, max_value=250.0, value=168.8, step=0.1)
    carwidth = st.slider("Car Width (in)", min_value=50.0, max_value=100.0, value=64.1, step=0.1)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Panel 03: Performance ----
    st.markdown("""
        <div class="panel">
            <div class="panel-head">
                <span class="panel-index">03</span>
                <span class="panel-name">Performance</span>
                <span class="panel-hint">weight · engine · power</span>
            </div>
    """, unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        curbweight = st.number_input("Curb Weight (lbs)", min_value=1000, max_value=6000, value=2548, step=1)
        boreratio = st.number_input("Bore Ratio", min_value=1.0, max_value=5.0, value=3.47, step=0.01)
    with p2:
        enginesize = st.number_input("Engine Size", min_value=10, max_value=500, value=130, step=1)
        horsepower = st.number_input("Horsepower", min_value=10, max_value=1000, value=111, step=1)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Panel 04: Efficiency ----
    st.markdown("""
        <div class="panel">
            <div class="panel-head">
                <span class="panel-index">04</span>
                <span class="panel-name">Efficiency</span>
                <span class="panel-hint">miles per gallon</span>
            </div>
    """, unsafe_allow_html=True)

    e1, e2 = st.columns(2)
    with e1:
        citympg = st.number_input("City MPG", min_value=5, max_value=100, value=21, step=1)
    with e2:
        highwaympg = st.number_input("Highway MPG", min_value=5, max_value=100, value=27, step=1)

    st.markdown("</div>", unsafe_allow_html=True)

    predict_clicked = st.button("Run Valuation", use_container_width=True)

    if predict_clicked:
        input_data = {
            'drivewheel': drivewheel,
            'enginelocation': enginelocation,
            'fuelsystem': fuelsystem,
            'wheelbase': wheelbase,
            'carlength': carlength,
            'carwidth': carwidth,
            'curbweight': curbweight,
            'enginesize': enginesize,
            'boreratio': boreratio,
            'horsepower': horsepower,
            'citympg': citympg,
            'highwaympg': highwaympg
        }

        df_input = pd.DataFrame([input_data])
        df_encoded = pd.get_dummies(df_input, columns=['drivewheel', 'enginelocation', 'fuelsystem'])
        df_final = df_encoded.reindex(columns=model_columns, fill_value=0)
        scaled_features = scaler.transform(df_final)

        with st.spinner("Reading the build sheet…"):
            prediction = model.predict(scaled_features)[0]
            time.sleep(0.4)

        formatted_price = f"${prediction:,.0f}"
        gauge_min, gauge_max = 5000, 45000
        pct = max(0.0, min(1.0, (prediction - gauge_min) / (gauge_max - gauge_min))) * 100

        st.markdown(f"""
            <div class="readout">
                <div class="readout-label">Estimated Market Value</div>
                <div class="readout-value">{formatted_price}</div>
                <div class="gauge">
                    <div class="gauge-track"><div class="gauge-fill" style="width:{pct:.1f}%;"></div></div>
                    <div class="gauge-scale"><span>${gauge_min:,}</span><span>${gauge_max:,}</span></div>
                </div>
                <div class="readout-foot">RANDOM FOREST · 12 FEATURES · LIVE INFERENCE</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="strip">Valuation Engine · Predictive Analytics</div>', unsafe_allow_html=True)

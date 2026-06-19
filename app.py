import streamlit as st
import pandas as pd
import joblib
import time

# -------------------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------------------
st.set_page_config(page_title="Valuation Engine", page_icon="🛠️", layout="centered")

# -------------------------------------------------------------
# 2. DESIGN SYSTEM — "INSTRUMENT PANEL"
# Inspired by dyno readouts, build sheets, and blueprint paper.
# Mono type for data, tight grotesk for labels. Signal-orange
# accent (telemetry red-line), not luxury gold. Fully responsive.
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

        html, body, .stApp {
            background: var(--bg);
            color: var(--paper);
            font-family: 'Inter', sans-serif;
        }

        #MainMenu, footer, header { visibility: hidden; }
        .stAlert { display: none; }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 880px;
        }

        /* Faint blueprint grid behind everything */
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(var(--line-soft) 1px, transparent 1px),
                linear-gradient(90deg, var(--line-soft) 1px, transparent 1px);
            background-size: 28px 28px;
            pointer-events: none;
            z-index: 0;
        }

        /* ----- HEADER / SPEC PLATE ----- */
        .plate {
            border: 1px solid var(--line);
            border-radius: 4px;
            background: var(--panel);
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.4rem;
            position: relative;
        }
        .plate::before {
            content: "";
            position: absolute;
            top: 10px; left: 10px;
            width: 6px; height: 6px;
            border-radius: 50%;
            background: var(--signal);
            box-shadow: 0 0 8px var(--signal);
        }
        .plate-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .plate-title {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: 1.6rem;
            letter-spacing: 0.5px;
            color: var(--paper);
            margin: 0;
        }
        .plate-tag {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            color: var(--signal);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            border: 1px solid rgba(255,107,53,0.35);
            background: var(--signal-dim);
            padding: 0.25rem 0.55rem;
            border-radius: 3px;
            white-space: nowrap;
        }
        .plate-sub {
            font-size: 0.82rem;
            color: var(--muted);
            margin-top: 0.35rem;
            letter-spacing: 0.2px;
        }

        /* ----- SECTION PANELS ----- */
        .panel {
            border: 1px solid var(--line);
            border-radius: 4px;
            background: var(--panel);
            padding: 1.3rem 1.4rem 0.6rem;
            margin-bottom: 1rem;
        }
        .panel-head {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 1rem;
            padding-bottom: 0.7rem;
            border-bottom: 1px dashed var(--line);
        }
        .panel-index {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            color: var(--bg);
            background: var(--paper);
            border-radius: 3px;
            padding: 0.1rem 0.45rem;
            font-weight: 700;
        }
        .panel-name {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: 1.8px;
            text-transform: uppercase;
            color: var(--paper);
            font-weight: 600;
        }
        .panel-hint {
            margin-left: auto;
            font-size: 0.7rem;
            color: var(--muted);
            font-family: 'IBM Plex Mono', monospace;
        }

        /* ----- FORM CONTROLS ----- */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        .stNumberInput input {
            background: var(--panel-2) !important;
            border: 1px solid var(--line) !important;
            border-radius: 3px !important;
            color: var(--paper) !important;
            font-family: 'IBM Plex Mono', monospace !important;
        }
        div[data-baseweb="select"]:focus-within > div,
        div[data-baseweb="input"]:focus-within > div {
            border-color: var(--signal) !important;
            box-shadow: 0 0 0 2px var(--signal-dim) !important;
        }
        .stSelectbox label, .stNumberInput label, .stSlider label {
            color: var(--muted) !important;
            font-weight: 500 !important;
            font-size: 0.7rem !important;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            font-family: 'IBM Plex Mono', monospace !important;
        }
        /* Slider track + thumb */
        .stSlider [data-baseweb="slider"] > div > div {
            background: var(--line) !important;
        }
        .stSlider [role="slider"] {
            background: var(--signal) !important;
            box-shadow: 0 0 0 4px var(--signal-dim) !important;
        }
        .stSlider [data-testid="stTickBar"] { display: none; }

        /* ----- BUTTON ----- */
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
            margin-top: 0.6rem;
            transition: filter 0.15s ease, transform 0.1s ease;
        }
        .stButton button:hover {
            filter: brightness(1.12);
        }
        .stButton button:active {
            transform: scale(0.99);
        }
        .stButton button:focus-visible {
            outline: 2px solid var(--paper);
            outline-offset: 2px;
        }

        /* ----- READOUT (RESULT) ----- */
        .readout {
            border: 1px solid var(--signal);
            border-radius: 4px;
            background: linear-gradient(180deg, rgba(255,107,53,0.08), rgba(255,107,53,0.02));
            padding: 1.6rem 1.4rem;
            margin-top: 1.2rem;
            text-align: center;
            animation: rise 0.45s ease forwards;
        }
        @keyframes rise {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .readout-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            color: var(--signal);
            margin-bottom: 0.6rem;
        }
        .readout-value {
            font-family: 'IBM Plex Mono', monospace;
            font-size: clamp(2.2rem, 9vw, 3.4rem);
            font-weight: 700;
            color: var(--paper);
            letter-spacing: 1px;
            line-height: 1;
        }
        .readout-foot {
            margin-top: 0.7rem;
            font-size: 0.72rem;
            color: var(--muted);
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: 0.5px;
        }

        /* Gauge bar under the price */
        .gauge {
            margin: 1.2rem auto 0;
            max-width: 420px;
        }
        .gauge-track {
            height: 6px;
            border-radius: 3px;
            background: var(--line);
            position: relative;
            overflow: hidden;
        }
        .gauge-fill {
            position: absolute;
            top: 0; left: 0; bottom: 0;
            background: linear-gradient(90deg, var(--good), var(--signal));
            border-radius: 3px;
        }
        .gauge-scale {
            display: flex;
            justify-content: space-between;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.62rem;
            color: var(--muted);
            margin-top: 0.4rem;
            letter-spacing: 0.5px;
        }

        /* ----- FOOTER STRIP ----- */
        .strip {
            text-align: center;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.65rem;
            color: var(--line);
            margin-top: 1.6rem;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        /* ----- MOBILE TUNING ----- */
        @media (max-width: 640px) {
            .main .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
            .plate { padding: 1.1rem 1.1rem; }
            .plate-title { font-size: 1.25rem; }
            .plate-row { flex-direction: column; align-items: flex-start; }
            .panel { padding: 1.05rem 1.05rem 0.4rem; }
            .readout-value { font-size: 2.1rem; }
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. CACHED MODEL LOADING (unchanged)
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

# -------------------------------------------------------------
# 4. HEADER — SPEC PLATE
# -------------------------------------------------------------
st.markdown("""
    <div class="plate">
        <div class="plate-row">
            <div class="plate-title">VALUATION ENGINE</div>
            <div class="plate-tag">Model: Random Forest</div>
        </div>
        <div class="plate-sub">Enter the build sheet below — the engine reads each spec and returns an estimated market value.</div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. PANEL 01 — CONFIGURATION (single column, stacks naturally on mobile)
# -------------------------------------------------------------
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

st.markdown("</div>", unsafe_allow_html=True)  # close panel 01

# -------------------------------------------------------------
# 6. PANEL 02 — DIMENSIONS (sliders read like a build sheet)
# -------------------------------------------------------------
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

st.markdown("</div>", unsafe_allow_html=True)  # close panel 02

# -------------------------------------------------------------
# 7. PANEL 03 — PERFORMANCE
# -------------------------------------------------------------
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

st.markdown("</div>", unsafe_allow_html=True)  # close panel 03

# -------------------------------------------------------------
# 8. PANEL 04 — EFFICIENCY
# -------------------------------------------------------------
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

st.markdown("</div>", unsafe_allow_html=True)  # close panel 04

predict_clicked = st.button("Run Valuation", use_container_width=True)

# -------------------------------------------------------------
# 9. PREDICTION & READOUT
# -------------------------------------------------------------
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

    # Position the result on a rough $5k–$45k gauge for visual context
    gauge_min, gauge_max = 5000, 45000
    pct = max(0.0, min(1.0, (prediction - gauge_min) / (gauge_max - gauge_min))) * 100

    st.markdown(f"""
        <div class="readout">
            <div class="readout-label">Estimated Market Value</div>
            <div class="readout-value">{formatted_price}</div>
            <div class="gauge">
                <div class="gauge-track">
                    <div class="gauge-fill" style="width:{pct:.1f}%;"></div>
                </div>
                <div class="gauge-scale">
                    <span>${gauge_min:,}</span>
                    <span>${gauge_max:,}</span>
                </div>
            </div>
            <div class="readout-foot">RANDOM FOREST · {len(model_columns)} FEATURES · LIVE INFERENCE</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="strip">Valuation Engine · Predictive Analytics</div>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import joblib
import time

# -------------------------------------------------------------
# 1. PREMIUM UI THEME CONFIGURATION (NEXT‑GEN LUXURY)
# -------------------------------------------------------------
st.set_page_config(page_title="Valuation Engine", page_icon="🏎️", layout="centered")

# Custom CSS with futuristic dark/gold + neon accents
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

        /* Global reset */
        html, body, .stApp {
            background: radial-gradient(ellipse at top left, #0b0f1a 0%, #05080f 100%);
            color: #eaeef2;
            font-family: 'Inter', sans-serif;
        }

        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Main container with subtle glass effect */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* ----- TITLE & SUBTITLE ----- */
        .hero-title {
            text-align: center;
            font-size: 3.2rem !important;
            font-weight: 800;
            letter-spacing: 4px;
            background: linear-gradient(135deg, #f6e6b0 0%, #c5a059 50%, #a07c3e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(197, 160, 89, 0.2);
            margin-bottom: 0.2rem;
        }
        .hero-subtitle {
            text-align: center;
            font-size: 1rem;
            font-weight: 300;
            color: #8892b0;
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-top: -0.5rem;
            margin-bottom: 2.5rem;
        }
        .hero-subtitle span {
            color: #c5a059;
            font-weight: 600;
        }

        /* ----- GLASS CARD CONTAINERS ----- */
        .glass-card {
            background: rgba(20, 28, 45, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(197, 160, 89, 0.15);
            border-radius: 24px;
            padding: 1.5rem 1.8rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05);
            transition: all 0.3s ease;
        }
        .glass-card:hover {
            border-color: rgba(197, 160, 89, 0.35);
            box-shadow: 0 25px 50px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.08);
        }

        /* Section headers inside cards */
        .section-header {
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #c5a059;
            margin-bottom: 1.2rem;
            border-bottom: 1px solid rgba(197, 160, 89, 0.15);
            padding-bottom: 0.7rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section-header i {
            font-style: normal;
            font-size: 1.2rem;
        }

        /* ----- FORM ELEMENTS (Inputs, Selects) ----- */
        .stSelectbox, .stNumberInput {
            margin-bottom: 0.8rem;
        }

        /* Override Streamlit's default input styles */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background: rgba(11, 15, 26, 0.8) !important;
            border: 1px solid rgba(197, 160, 89, 0.2) !important;
            border-radius: 12px !important;
            transition: all 0.25s ease;
            color: #eaeef2 !important;
        }
        div[data-baseweb="select"]:hover > div,
        div[data-baseweb="input"]:hover > div {
            border-color: rgba(197, 160, 89, 0.5) !important;
        }
        div[data-baseweb="select"]:focus-within > div,
        div[data-baseweb="input"]:focus-within > div {
            border-color: #c5a059 !important;
            box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.2) !important;
        }
        /* Labels */
        .stSelectbox label, .stNumberInput label {
            color: #a8b2d1 !important;
            font-weight: 400 !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* ----- BUTTON ----- */
        .stButton button {
            width: 100%;
            background: linear-gradient(135deg, #c5a059 0%, #a07c3e 100%) !important;
            color: #0b0f1a !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            letter-spacing: 2px;
            padding: 0.9rem 0 !important;
            border: none !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 24px rgba(197, 160, 89, 0.25);
            transition: all 0.3s ease;
            text-transform: uppercase;
            margin-top: 1.2rem;
        }
        .stButton button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(197, 160, 89, 0.4);
            background: linear-gradient(135deg, #dbb06a 0%, #b08a44 100%) !important;
        }
        .stButton button:active {
            transform: translateY(0);
            box-shadow: 0 4px 16px rgba(197, 160, 89, 0.3);
        }

        /* ----- PRICE DISPLAY (with animation) ----- */
        .price-container {
            text-align: center;
            padding: 2rem 0.5rem 1.5rem;
            margin-top: 1.8rem;
            border-top: 1px solid rgba(197, 160, 89, 0.15);
            animation: fadeInUp 0.8s ease forwards;
        }
        .price-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 4px;
            color: #8892b0;
            margin-bottom: 0.5rem;
        }
        .price-value {
            font-size: 3.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #f6e6b0 0%, #c5a059 60%, #a07c3e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 60px rgba(197, 160, 89, 0.25);
            letter-spacing: 2px;
            animation: glowPulse 2s infinite alternate;
        }
        @keyframes glowPulse {
            0% { text-shadow: 0 0 30px rgba(197, 160, 89, 0.2); }
            100% { text-shadow: 0 0 60px rgba(197, 160, 89, 0.5); }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ----- RESPONSIVE TWEAKS ----- */
        @media (max-width: 768px) {
            .hero-title { font-size: 2.2rem !important; }
            .price-value { font-size: 2.6rem !important; }
            .glass-card { padding: 1.2rem; }
        }

        /* Hide Streamlit's default success/info boxes */
        .stAlert { display: none; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. CACHED MODEL LOADING (unchanged)
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
# 3. UI LAYOUT - HERO HEADER
# -------------------------------------------------------------
st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <div class="hero-title">Valuation Engine</div>
        <div class="hero-subtitle">Random Forest · <span>Predictive Analytics</span></div>
    </div>
""", unsafe_allow_html=True)

# Wrap the whole input area in a glass card
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    # Two-column layout for inputs
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-header"><i>🏷️</i> Categorical Attributes</div>', unsafe_allow_html=True)
        drivewheel = st.selectbox("Drive Wheel System", ["fwd", "rwd", "4wd"])
        enginelocation = st.selectbox("Engine Placement", ["front", "rear"])
        fuelsystem = st.selectbox("Fuel Delivery System", ["mpfi", "2bbl", "idi", "1bbl", "spdi", "4bbl", "mfi", "spfi"])

        st.markdown('<div class="section-header" style="margin-top:1.5rem;"><i>📏</i> Dimensions</div>', unsafe_allow_html=True)
        wheelbase = st.number_input("Wheelbase (in)", min_value=50.0, max_value=150.0, value=94.5, step=0.1)
        carlength = st.number_input("Car Length (in)", min_value=100.0, max_value=250.0, value=168.8, step=0.1)
        carwidth = st.number_input("Car Width (in)", min_value=50.0, max_value=100.0, value=64.1, step=0.1)

    with col2:
        st.markdown('<div class="section-header"><i>⚡</i> Performance Specs</div>', unsafe_allow_html=True)
        curbweight = st.number_input("Curb Weight (lbs)", min_value=1000, max_value=6000, value=2548, step=1)
        enginesize = st.number_input("Engine Size", min_value=10, max_value=500, value=130, step=1)
        boreratio = st.number_input("Bore Ratio", min_value=1.0, max_value=5.0, value=3.47, step=0.01)
        horsepower = st.number_input("Horsepower", min_value=10, max_value=1000, value=111, step=1)

        st.markdown('<div class="section-header" style="margin-top:1.5rem;"><i>⛽</i> Efficiency</div>', unsafe_allow_html=True)
        citympg = st.number_input("City MPG", min_value=5, max_value=100, value=21, step=1)
        highwaympg = st.number_input("Highway MPG", min_value=5, max_value=100, value=27, step=1)

    # Prediction button
    predict_clicked = st.button("Execute Asset Valuation", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close glass-card

# -------------------------------------------------------------
# 4. PREDICTION & OUTPUT
# -------------------------------------------------------------
if predict_clicked:
    # Construct input dictionary
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

    # Data transformation pipeline
    df_input = pd.DataFrame([input_data])
    df_encoded = pd.get_dummies(df_input, columns=['drivewheel', 'enginelocation', 'fuelsystem'])
    df_final = df_encoded.reindex(columns=model_columns, fill_value=0)
    scaled_features = scaler.transform(df_final)

    # Predict
    prediction = model.predict(scaled_features)[0]

    # Show a subtle loading animation (simulated)
    with st.spinner("Computing valuation..."):
        time.sleep(0.5)  # just for effect

    # Display result in a gorgeous container
    formatted_price = f"${prediction:,.2f}"
    st.markdown(f"""
        <div class="price-container">
            <div class="price-label">Estimated Market Asset Value</div>
            <div class="price-value">{formatted_price}</div>
        </div>
    """, unsafe_allow_html=True)

    # Optional: add a small "powered by" note
    st.markdown("""
        <div style="text-align: center; font-size: 0.65rem; color: #4a5568; margin-top: 1rem; letter-spacing: 1px;">
            ⚡ Random Forest Ensemble · Predictive Analytics Engine
        </div>
    """, unsafe_allow_html=True)